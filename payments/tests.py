from decimal import Decimal
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import Client as HttpClient, TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from main.models import Client, Metric, WaterBill
from payments.models import Payment, PaymentAllocation
from payments.mpesa import get_access_token, register_c2b_urls
from payments.services import reconcile_payment


@override_settings(SECURE_SSL_REDIRECT=False)
class PaymentsTestBase(TestCase):
    def setUp(self):
        Metric.objects.create(consump_amount=200.0, penalty_amount=100.0)
        self.client_row = Client.objects.create(
            first_name="Jane",
            last_name="Doe",
            meter_number=1001,
            account_number="1001",
            address="Town",
            status="Connected",
            contact_number="+254700000001",
        )

    def make_bill(self, consumption=10, status="Pending", billing_date=None):
        return WaterBill.objects.create(
            name=self.client_row,
            previous_reading=0,
            present_reading=consumption,
            meter_consumption=consumption,
            payment_status=status,
            approval_status="Approved",
            billing_date=billing_date or timezone.localdate(),
        )


class ReconcilePaymentTests(PaymentsTestBase):
    def test_unknown_account_is_unmatched(self):
        payment = Payment.objects.create(
            amount=Decimal("100.00"),
            reference_code="TXNUNKNOWN",
            account_reference="no-such-account",
            status=Payment.Status.PENDING,
        )
        result = reconcile_payment(payment.pk)
        self.assertEqual(result.status, Payment.Status.UNMATCHED)
        self.assertIsNone(result.client)

    def test_partial_payment_marks_bill_partial(self):
        bill = self.make_bill(consumption=10)
        self.assertEqual(Decimal(str(bill.payable())), Decimal("2000.00"))
        payment = Payment.objects.create(
            amount=Decimal("500.00"),
            reference_code="TXNPARTIAL",
            account_reference="1001",
            status=Payment.Status.PENDING,
        )
        reconcile_payment(payment.pk)
        bill.refresh_from_db()
        payment.refresh_from_db()
        self.assertEqual(payment.status, Payment.Status.MATCHED)
        self.assertEqual(bill.payment_status, "Partial")
        self.assertEqual(bill.amount_paid, Decimal("500.00"))
        self.assertEqual(bill.balance_remaining(), Decimal("1500.00"))
        self.assertEqual(PaymentAllocation.objects.filter(payment=payment).count(), 1)

    def test_overpayment_covers_next_bill_then_credit(self):
        from datetime import timedelta
        first = self.make_bill(consumption=1, billing_date=timezone.localdate() - timedelta(days=40))
        second = self.make_bill(consumption=1, billing_date=timezone.localdate())
        payment = Payment.objects.create(
            amount=Decimal("500.00"),
            reference_code="TXNOVER",
            account_reference="1001",
            status=Payment.Status.PENDING,
        )
        reconcile_payment(payment.pk)
        first.refresh_from_db()
        second.refresh_from_db()
        self.client_row.refresh_from_db()
        self.assertEqual(first.payment_status, "Paid")
        self.assertEqual(second.payment_status, "Paid")
        self.assertEqual(self.client_row.credit_balance, Decimal("100.00"))

    def test_leading_zero_account_reference_matches(self):
        self.make_bill(consumption=1)
        payment = Payment.objects.create(
            amount=Decimal("200.00"),
            reference_code="TXNPAD",
            account_reference="0001001",
            status=Payment.Status.PENDING,
        )
        reconcile_payment(payment.pk)
        payment.refresh_from_db()
        self.assertEqual(payment.status, Payment.Status.MATCHED)
        self.assertEqual(payment.client_id, self.client_row.id)

    def test_already_matched_is_idempotent(self):
        bill = self.make_bill(consumption=1)
        payment = Payment.objects.create(
            amount=Decimal("200.00"),
            reference_code="TXNIDEMP",
            account_reference="1001",
            status=Payment.Status.PENDING,
        )
        reconcile_payment(payment.pk)
        reconcile_payment(payment.pk)
        bill.refresh_from_db()
        self.assertEqual(PaymentAllocation.objects.filter(payment=payment).count(), 1)
        self.assertEqual(bill.payment_status, "Paid")


class ConfirmationWebhookTests(PaymentsTestBase):
    def test_duplicate_trans_id_creates_one_payment(self):
        body = {
            "TransID": "RKTQDM7W6S",
            "TransAmount": "200.00",
            "BillRefNumber": "1001",
        }
        http = HttpClient()
        url = reverse("mpesa_confirmation")
        with patch("payments.views._enqueue_reconcile", return_value=True):
            first = http.post(url, data=body, content_type="application/json")
            second = http.post(url, data=body, content_type="application/json")
        self.assertEqual(first.status_code, 200)
        self.assertEqual(second.status_code, 200)
        self.assertEqual(Payment.objects.filter(reference_code="RKTQDM7W6S").count(), 1)

    def test_validation_accepts_known_account(self):
        http = HttpClient()
        url = reverse("mpesa_validation")
        response = http.post(
            url,
            data={"BillRefNumber": "1001"},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["ResultCode"], "0")

    def test_validation_rejects_unknown_account(self):
        http = HttpClient()
        url = reverse("mpesa_validation")
        response = http.post(
            url,
            data={"BillRefNumber": "missing"},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["ResultCode"], "C2B00012")

    @override_settings(MPESA_CALLBACK_SECRET="s3cret")
    def test_secret_path_required_when_configured(self):
        http = HttpClient()
        open_url = reverse("mpesa_validation")
        denied = http.post(open_url, data={"BillRefNumber": "1001"}, content_type="application/json")
        self.assertEqual(denied.status_code, 403)
        secret_url = reverse("mpesa_validation_secret", kwargs={"callback_secret": "s3cret"})
        ok = http.post(secret_url, data={"BillRefNumber": "1001"}, content_type="application/json")
        self.assertEqual(ok.json()["ResultCode"], "0")


class DarajaClientTests(TestCase):
    @override_settings(
        MPESA_CONSUMER_KEY="key",
        MPESA_CONSUMER_SECRET="secret",
        MPESA_SHORTCODE="174379",  # Sandbox test shortcode
        MPESA_ENV="sandbox",
        MPESA_CALLBACK_BASE_URL="https://example.test",
        MPESA_CALLBACK_SECRET="",
    )
    @patch("payments.mpesa.requests.get")
    def test_get_access_token_cached(self, mock_get):
        mock_get.return_value.json.return_value = {"access_token": "tok", "expires_in": 3600}
        mock_get.return_value.raise_for_status = lambda: None
        import payments.mpesa as mpesa_mod

        mpesa_mod._token_cache["access_token"] = None
        mpesa_mod._token_cache["expires_at"] = 0
        first = get_access_token()
        second = get_access_token()
        self.assertEqual(first, "tok")
        self.assertEqual(second, "tok")
        self.assertEqual(mock_get.call_count, 1)

    @override_settings(
        MPESA_CONSUMER_KEY="key",
        MPESA_CONSUMER_SECRET="secret",
        MPESA_SHORTCODE="174379",  # Sandbox test shortcode
        MPESA_ENV="sandbox",
        MPESA_CALLBACK_BASE_URL="https://example.test",
        MPESA_CALLBACK_SECRET="xyz",
    )
    @patch("payments.mpesa.get_access_token", return_value="tok")
    @patch("payments.mpesa.requests.post")
    def test_register_c2b_urls(self, mock_post, _token):
        mock_post.return_value.json.return_value = {"ResponseDescription": "Success"}
        mock_post.return_value.raise_for_status = lambda: None
        register_c2b_urls()
        payload = mock_post.call_args.kwargs["json"]
        self.assertTrue(payload["ValidationURL"].endswith("/payments/mpesa/xyz/validation/"))
        self.assertTrue(payload["ConfirmationURL"].endswith("/payments/mpesa/xyz/confirmation/"))


class UnmatchedStaffViewTests(PaymentsTestBase):
    def setUp(self):
        super().setUp()
        User = get_user_model()
        self.staff = User.objects.create_user(
            email="staff@example.com",
            password="password123",
            is_staff=True,
            verified=True,
            admin_approved=True,
        )
        self.http = HttpClient()
        self.http.force_login(self.staff)

    def test_assign_unmatched_payment(self):
        self.make_bill(consumption=1)
        payment = Payment.objects.create(
            amount=Decimal("200.00"),
            reference_code="TXNSTAFF",
            account_reference="wrong",
            status=Payment.Status.UNMATCHED,
        )
        url = reverse("assign_unmatched_payment", args=[payment.pk])
        response = self.http.post(url, {"client_id": self.client_row.pk})
        self.assertEqual(response.status_code, 302)
        payment.refresh_from_db()
        self.assertEqual(payment.status, Payment.Status.MATCHED)
        self.assertEqual(payment.client_id, self.client_row.id)
