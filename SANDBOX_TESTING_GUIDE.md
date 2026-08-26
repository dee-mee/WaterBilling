# M-Pesa Sandbox Testing Guide

## Quick Start

### 1. Get Sandbox Credentials
1. Go to [developer.safaricom.co.ke](https://developer.safaricom.co.ke)
2. Create an account or log in
3. Create a new app (e.g., "WaterBilling")
4. Add products: "M-PESA Express Sandbox" and "MPesa Sandbox"
5. Copy your **Consumer Key** and **Consumer Secret**

### 2. Configure Environment
Add to your `.env` file:
```bash
MPESA_CONSUMER_KEY=your_sandbox_consumer_key
MPESA_CONSUMER_SECRET=your_sandbox_consumer_secret
MPESA_SHORTCODE=174379
MPESA_ENV=sandbox
MPESA_CALLBACK_BASE_URL=https://your-public-url.com
```

**Important Notes:**
- **Shortcode:** Always use `174379` for sandbox (Safaricom's test shortcode)
- **Phone:** Always use `254708374149` for sandbox simulations
- No real Paybill registration needed for sandbox

### 3. Set Up Public HTTPS Endpoint
For local testing, use ngrok:
```bash
# Install ngrok if not already installed
# On Linux: sudo apt install ngrok

# Start ngrok
ngrok http 8000

# Copy the HTTPS URL (e.g., https://abc123.ngrok.io)
# Set MPESA_CALLBACK_BASE_URL=https://abc123.ngrok.io
```

For production testing, deploy to Render/staging and use that URL.

### 4. Register C2B URLs
```bash
python manage.py register_mpesa_c2b_urls
```

Expected output:
```json
{
  "ResponseDescription": "success",
  "ResponseCode": "0",
  ...
}
```

### 5. Test Payment Simulation
Create a test client and bill first:
```bash
python manage.py shell
```
```python
from main.models import Client, WaterBill, Metric
from django.utils import timezone

# Create metric if needed
Metric.objects.get_or_create(consump_amount=200.0, penalty_amount=100.0)

# Create test client
client = Client.objects.create(
    first_name="Test",
    last_name="Customer",
    meter_number=9999,
    account_number="9999",
    address="Test Address",
    status="Connected",
    contact_number="+254700000000"
)

# Create test bill
bill = WaterBill.objects.create(
    name=client,
    previous_reading=0,
    present_reading=10,
    meter_consumption=10,
    payment_status="Pending",
    approval_status="Approved",
    billing_date=timezone.localdate(),
    duedate=timezone.localdate(),
    penaltydate=timezone.localdate()
)

print(f"Client account number: {client.account_number}")
print(f"Bill amount: {bill.payable()}")
```

Then simulate payment:
```bash
python manage.py simulate_mpesa_c2b 9999 500 --msisdn 254708374149
```

### 6. Verify Results
Check Django admin or run:
```bash
python manage.py shell
```
```python
from payments.models import Payment
from main.models import WaterBill

# Check payment
payment = Payment.objects.first()
print(f"Payment status: {payment.status}")
print(f"Payment amount: {payment.amount}")

# Check bill
bill = WaterBill.objects.first()
print(f"Bill payment status: {bill.payment_status}")
print(f"Amount paid: {bill.amount_paid}")
print(f"Balance remaining: {bill.balance_remaining()}")
```

## Common Issues

### "Connection refused" when registering C2B URLs
- Ensure your ngrok/public URL is accessible
- Check that `MPESA_CALLBACK_BASE_URL` is set correctly
- Verify the URL includes the full path (no trailing slash)

### "Invalid Account Number" in validation
- Ensure the client account_number exists in your database
- Check the account_number matches exactly what you're testing with
- Try different formats (with/without leading zeros)

### Payment not reconciling
- Check if Celery worker is running (or use process_pending_payments)
- Verify payment status in Django admin
- Check logs for reconciliation errors

### Tests failing
- Ensure all dependencies are installed
- Run migrations: `python manage.py migrate`
- Check that Redis is running if using Celery

## Next Steps After Sandbox

Once sandbox testing is successful:

1. **Get Production Paybill**
   - Register a Paybill number with Safaricom (not Till number)
   - This is required for production as Till numbers don't carry account reference

2. **Get Production Credentials**
   - Apply for production access in Daraja portal
   - Get production Consumer Key/Secret

3. **Update Configuration**
   ```bash
   MPESA_SHORTCODE=your_actual_paybill_number
   MPESA_CONSUMER_KEY=production_key
   MPESA_CONSUMER_SECRET=production_secret
   MPESA_ENV=production
   MPESA_ALLOWED_IPS=safaricom_ip_ranges
   ```

4. **Deploy to Production**
   - Deploy to your production environment
   - Register production C2B URLs
   - Do a small real-money test
   - Monitor for any issues

## Testing Checklist

- [ ] Sandbox credentials obtained
- [ ] Environment variables configured
- [ ] Public HTTPS endpoint available
- [ ] C2B URLs registered successfully
- [ ] Test client and bill created
- [ ] Payment simulation works
- [ ] Payment reconciled correctly
- [ ] Bill status updated
- [ ] Unmatched payments interface works
- [ ] PDF invoice shows correct Paybill/account
- [ ] All tests pass

## Useful Commands

```bash
# Register C2B URLs
python manage.py register_mpesa_c2b_urls

# Simulate payment
python manage.py simulate_mpesa_c2b <account_number> <amount> --msisdn 254708374149

# Process pending payments (fallback)
python manage.py process_pending_payments

# Run tests
python manage.py test payments

# Check migrations
python manage.py showmigrations payments

# Create superuser
python manage.py createsuperuser
```

## Support

For issues with:
- **Daraja API:** Check [Safaricom Developer Portal](https://developer.safaricom.co.ke)
- **This implementation:** Check the code documentation and tests
- **Deployment:** Refer to `PAYMENTS_IMPLEMENTATION_STATUS.md`