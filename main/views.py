import os
from django.shortcuts import render, redirect, HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import *
from account.models import *
from .forms import MetricsForm, BillForm, ClientForm, BulkUploadForm, CustomerForm
from django.db.models import F, Sum
import sweetify
from account.forms import *
from main.decorators import *
import datetime
from twilio.rest import Client as TwilClient
import csv
from django.http import HttpResponse, JsonResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from django.conf import settings
import stripe
from account.forms import RegistrationForm
from django.template.loader import render_to_string

stripe.api_key = settings.STRIPE_SECRET_KEY if settings.STRIPE_SECRET_KEY else None

def landingpage(request):
    return render(request, 'landingpage/landingpage.html')  


@user_passes_test(lambda u: u.is_superuser)
def export_clients_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="clients.csv"'

    writer = csv.writer(response)
    writer.writerow(['Meter Number', 'First Name', 'Middle Name', 'Last Name', 'Contact Number', 'Address', 'Connection Status'])

    clients = Client.objects.all().values_list('meter_number', 'first_name', 'middle_name', 'last_name', 'contact_number', 'address', 'status')
    for client in clients:
        writer.writerow(client)

    return response

@login_required(login_url='login')
@verified_or_superuser
def download_invoice(request, pk):
    bill = WaterBill.objects.get(id=pk)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="invoice_{bill.id}.pdf"'

    p = canvas.Canvas(response, pagesize=letter)
    width, height = letter

    logo_path = settings.BASE_DIR / 'main/static/sb_admin/img/logo.png'
    p.drawImage(logo_path, inch, height - 1.5 * inch, width=1*inch, height=1*inch)

    p.setFont("Helvetica-Bold", 16)
    p.drawString(2 * inch, height - inch, "Water Billing System")

    p.setFont("Helvetica", 12)
    p.drawString(inch, height - 2 * inch, f"Invoice for: {bill.name.first_name} {bill.name.last_name}")
    p.drawString(inch, height - 2.25 * inch, f"Meter Number: {bill.name.meter_number}")
    p.drawString(inch, height - 2.5 * inch, f"Address: {bill.name.address}")

    p.setFont("Helvetica-Bold", 14)
    p.drawString(inch, height - 3 * inch, "Bill Details")

    p.setFont("Helvetica", 12)
    p.drawString(inch, height - 3.25 * inch, f"Billing Period: {bill.billing_date.strftime('%B %Y') if bill.billing_date else 'N/A'}")
    p.drawString(inch, height - 3.5 * inch, f"Due Date: {bill.duedate.strftime('%Y-%m-%d') if bill.duedate else 'N/A'}")
    p.drawString(inch, height - 3.75 * inch, f"Previous Reading: {bill.previous_reading}")
    p.drawString(inch, height - 4 * inch, f"Present Reading: {bill.present_reading}")
    p.drawString(inch, height - 4.25 * inch, f"Water Consumption: {bill.meter_consumption}")
    p.drawString(inch, height - 4.5 * inch, f"Total Bill: {bill.payable()}")
    p.drawString(inch, height - 4.75 * inch, f"Status: {bill.payment_status}")

    p.showPage()
    p.save()

    return response


@user_passes_test(lambda u: u.is_superuser)
def dashboard(request):
    context = {
        'title': 'Dashboard',
        'total_users': Account.objects.filter(is_superuser=False).count(),
        'total_bills': WaterBill.objects.all().count(),
        'pending_bills': WaterBill.objects.filter(payment_status='Pending').count(),
        'connected_clients': Client.objects.filter(status='Connected').count(),
        'disconnected_clients': Client.objects.filter(status='Disconnected').count(),
    }
    return render(request, 'main/dashboard.html', context)

@login_required(login_url='login')
@verified_or_superuser
def ongoing_bills(request):
    if request.user.is_superuser:
        ongoingbills = WaterBill.objects.filter(payment_status='Pending')
    else:
        ongoingbills = WaterBill.objects.filter(payment_status='Pending', approval_status='Approved', name__user=request.user)
    context = {
        'title': 'Ongoing Bills',
        'ongoingbills': ongoingbills,
        'form': BillForm()
    }
    if request.method == 'POST':
        billform = BillForm(request.POST)
        if billform.is_valid():
            bill = billform.save()
            sweetify.toast(request, 'Successfully Added.')
            try: 
                receiver = bill.name.contact_number
                print(f"Attempting to send SMS to: {receiver}") # Added for debugging
                totalbill = bill.payable()
                duedate = bill.duedate
                penaltydate = bill.penaltydate
                SID = os.environ.get('TWILIO_ACCOUNT_SID')
                Auth_Token = os.environ.get('TWILIO_AUTH_TOKEN')
                if SID and Auth_Token:
                    sender = '+17262005435'
                    message = f'\n Your Total Bill is: {totalbill} pesos \n\n Your due date is: {duedate} \n\n Your penalty date is: {penaltydate}'
                    cl = TwilClient(SID, Auth_Token)
                    cl.messages.create(body=message, from_=sender, to=receiver)
                    sweetify.toast(request, 'Notification Sent')
                else:
                    sweetify.toast(request, 'Twilio credentials not configured.', icon='warning')
            except Exception as e: # Catch the exception to get more details
                sweetify.toast(request, f'Contact Number is invalid format: {bill.name.contact_number} (Error: {e})', icon='error')
            return HttpResponseRedirect(request.path_info)
        else:
            print(billform.errors) # Add this line to print form errors
            sweetify.toast(request, 'Invalid Details', icon='error')
    return render(request, 'main/billsongoing.html', context)


@login_required(login_url='login')
@verified_or_superuser
def history_bills(request):
    if request.user.is_superuser:
        billshistory = WaterBill.objects.filter(payment_status='Paid')
    else:
        billshistory = WaterBill.objects.filter(payment_status='Paid', name__user=request.user)
    context = {
        'title': 'Bills History',
        'billshistory': billshistory,
        'form': BillForm()
    }
    return render(request, 'main/billshistory.html', context)

@user_passes_test(lambda u: u.is_superuser)
def update_bills(request, pk):
    bill = WaterBill.objects.get(id=pk)
    form = BillForm(instance=bill)
    context = {
        'title': 'Update Bill',
        'bill': bill,
        'form': form,
    }
    if request.method == 'POST':
        form = BillForm(request.POST, instance=bill)
        if form.is_valid():
            form.save()
            sweetify.toast(request, f'{bill} updated successfully.')
            return HttpResponseRedirect(reverse('ongoingbills'))
    return render(request, 'main/billupdate.html', context)


@user_passes_test(lambda u: u.is_superuser)
def delete_bills(request, pk):
    bill = WaterBill.objects.get(id=pk)
    context = {
        'title': 'Delete Bill',
        'bill': bill,
    }
    if request.method == 'POST':
        bill.delete()
        sweetify.toast(request, f'{bill} deleted successfully.')
        return HttpResponseRedirect(reverse('ongoingbills'))
    return render(request, 'main/billdelete.html', context)



@login_required(login_url='login')
@verified_or_superuser
def profile(request, pk):
    profile = Account.objects.get(id=pk)
    student_form = UpdateProfileForm(instance=profile)
    if request.method == 'POST':
        student_form = UpdateProfileForm(request.POST, instance=profile)
        password1 = request.POST['password']
        password2 = request.POST['password2']
        if password1 != password2:
            print("password does not match")
            sweetify.error(request, 'Password does not match!')
            return HttpResponseRedirect(request.path_info)
        elif student_form.is_valid():
            student_form.save()
            sweetify.success(request, 'Updated Successfully')
            return HttpResponseRedirect(reverse('login'))
        else: 
            sweetify.error(request, 'Invalid Credentials!')
            return HttpResponseRedirect(request.path_info)
    context = {
        'title': 'Profile',
        'student_form': student_form,
        'profile': profile,
    }
    return render(request, 'main/profile.html', context)

@user_passes_test(lambda u: u.is_superuser)
def users(request):
    context = {
        'title': 'Users',
        'users': Account.objects.filter(is_superuser=False)
    }
    return render(request, 'main/users.html', context)

@user_passes_test(lambda u: u.is_superuser)
def update_user(request, pk):
    user = Account.objects.get(id=pk)
    form = UpdateUserForm(instance=user)
    context = {
        'title': 'Users',
        'user': user,
        'form': form,
    }
    if request.method == 'POST':
        form = UpdateUserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            sweetify.toast(request, f'{user} updated sucessfuly')
            return HttpResponseRedirect(reverse('users'))
    return render(request, 'main/userupdate.html', context)

@user_passes_test(lambda u: u.is_superuser)
def delete_user(request, pk):
    user = Account.objects.get(id=pk)
    context = {
        'title': 'Users',
        'user': user,
    }
    if request.method == 'POST':
        user.delete()
        sweetify.toast(request, 'Deleted successfuly.')
        return HttpResponseRedirect(reverse('users'))
    return render(request, 'main/userdelete.html', context)

@user_passes_test(lambda u: u.is_superuser)
def add_user(request):
    form = RegistrationForm()
    context = {
        'title': 'Add User',
        'form': form
    }
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            sweetify.toast(request, 'User added successfully')
            return HttpResponseRedirect(reverse('users'))
        else:
            sweetify.toast(request, 'Invalid details', icon='error')
    return render(request, 'main/useradd.html', context)

@user_passes_test(lambda u: u.is_superuser)
def clients(request):
    form = ClientForm()
    context = {
        'title': 'Clients',
        'clients': Client.objects.all(),
        'form': form
    }
    if request.method == 'POST':
        form = ClientForm(request.POST)
        contact_number = request.POST['contact_number']
        check_number = Client.objects.filter(contact_number=contact_number).exists()
        if form.is_valid():
            form.save()
            sweetify.toast(request, 'Client added')
            return HttpResponseRedirect(reverse('clients'))
        elif check_number:
            sweetify.toast(request,'Phone number already exist', icon='error')
        else:
            sweetify.toast(request, 'Invalid details', icon='error')
    return render(request, 'main/clients.html', context)

@user_passes_test(lambda u: u.is_superuser)
def client_update(request,pk):
    client = Client.objects.get(id=pk)
    form = ClientForm(instance=client)
    context = {
        'title': 'Update Client',
        'client': client,
        'form': form
    }
    if request.method == 'POST':
        form = ClientForm(request.POST, instance=client)
        if form.is_valid():
            form.save()
            sweetify.toast(request, 'Client updated successfully')
            return HttpResponseRedirect(reverse('clients'))
        else:
            sweetify.toast(request, 'Invalid Details', icon='error')
    return render(request, 'main/clientupdate.html', context)


@user_passes_test(lambda u: u.is_superuser)
def client_delete(request,pk):
    client = Client.objects.get(id=pk)
    if request.method == 'POST':
        client.delete()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})



def metrics(request):
    clients = Client.objects.all()
    total_meters = clients.count()
    total_consumption_all = WaterBill.objects.aggregate(Sum('meter_consumption'))['meter_consumption__sum'] or 0
    connected_clients = Client.objects.filter(status='Connected').count()
    disconnected_clients = Client.objects.filter(status='Disconnected').count()
    pending_clients = Client.objects.filter(status='Pending').count()

    for client in clients:
        client.total_consumption = WaterBill.objects.filter(name=client).aggregate(Sum('meter_consumption'))['meter_consumption__sum'] or 0

    context = {
        'title': 'Metrics',
        'clients': clients,
        'total_meters': total_meters,
        'total_consumption': total_consumption_all,
        'connected_clients': connected_clients,
        'disconnected_clients': disconnected_clients,
        'pending_clients': pending_clients,
        'form': CustomerForm()
    }
    return render(request, 'main/metrics.html', context)


@user_passes_test(lambda u: u.is_superuser)
def metrics_update(request, pk):
    metric = Metric.objects.get(id=pk)
    form = MetricsForm(instance=metric)
    context = {
        'title': 'Update Metrics',
        'metric': metric,
        'form': form,
    }
    if request.method == 'POST':
        form = MetricsForm(request.POST, instance=metric)
        if form.is_valid():
            form.save()
            sweetify.toast(request, 'Metrics updated successfully.')
            return HttpResponseRedirect(reverse('metrics'))
    return render(request, 'main/metricsupdate.html', context)


@user_passes_test(lambda u: u.is_superuser)
def add_customer(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'form_html': render_to_string('main/customer_form_partial.html', {'form': form}, request=request)})
    else:
        form = CustomerForm()
    return render(request, 'main/customer_form_partial.html', {'form': form})


@user_passes_test(lambda u: u.is_superuser)
def edit_customer(request, pk):
    try:
        client = Client.objects.get(id=pk)
    except Client.DoesNotExist:
        return HttpResponse("Client not found.", status=404)

    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=client)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'form_html': render_to_string('main/customer_form_partial.html', {'form': form, 'client': client}, request=request)})
    else: # GET request
        form = CustomerForm(instance=client)

    context = {
        'form': form,
        'client': client,
    }
    return render(request, 'main/customer_form_partial.html', context)



@user_passes_test(lambda u: u.is_superuser)
def bulk_upload_view(request):
    if request.method == 'POST':
        form = BulkUploadForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = request.FILES['csv_file']
            decoded_file = csv_file.read().decode('utf-8').splitlines()
            reader = csv.DictReader(decoded_file)
            for row in reader:
                try:
                    client = Client.objects.get(meter_number=row['meter_number'])
                    WaterBill.objects.create(
                        client=client,
                        billing_date=row['billing_date'],
                        previous_reading=row['previous_reading'],
                        present_reading=row['present_reading'],
                        due_date=row['due_date'],
                        penalty_date=row['penalty_date'],
                    )
                except Client.DoesNotExist:
                    sweetify.toast(request, f"Client with meter number {row['meter_number']} does not exist.", icon='error')
                except Exception as e:
                    sweetify.toast(request, f"An error occurred: {e}", icon='error')
            sweetify.toast(request, 'Bulk upload successful.')
            return HttpResponseRedirect(reverse('ongoingbills'))
    else:
        form = BulkUploadForm()
    return render(request, 'main/bulk_upload.html', {'form': form})


@user_passes_test(lambda u: u.is_superuser)
def send_reminders_view(request):
    if request.method == 'POST':
        ongoing_bills = WaterBill.objects.filter(payment_status='Pending')
        for bill in ongoing_bills:
            try:
                SID = os.environ.get('TWILIO_ACCOUNT_SID')
                Auth_Token = os.environ.get('TWILIO_AUTH_TOKEN')
                if SID and Auth_Token:
                    sender = '+17262005435'
                    receiver = bill.client.contact_number
                    message = f'\n Your Total Bill is: {bill.total_bill} pesos \n\n Your due date is: {bill.due_date} \n\n Your penalty date is: {bill.penalty_date}'
                    cl = TwilClient(SID, Auth_Token)
                    cl.messages.create(body=message, from_=sender, to=receiver)
                    sweetify.toast(request, f'Reminder sent to {bill.client.first_name} {bill.client.last_name}')
                else:
                    sweetify.toast(request, 'Twilio credentials not configured.', icon='warning')
                    break # Stop sending reminders if keys are not set
            except:
                sweetify.toast(request, f'Could not send reminder to {bill.client.first_name} {bill.client.last_name}', icon='error')
        return HttpResponseRedirect(reverse('ongoingbills'))
    return render(request, 'main/send_reminders.html')


@user_passes_test(lambda u: u.is_superuser)
def approve_bills_view(request):
    bills = WaterBill.objects.filter(approval_status='Pending Approval')
    context = {
        'title': 'Approve Bills',
        'bills': bills
    }
    return render(request, 'main/approve_bills.html', context)

@user_passes_test(lambda u: u.is_superuser)
def bill_approve(request, pk):
    bill = WaterBill.objects.get(id=pk)
    bill.approval_status = 'Approved'
    bill.save()
    sweetify.toast(request, 'Bill approved successfully')
    return HttpResponseRedirect(reverse('approve_bills'))

@user_passes_test(lambda u: u.is_superuser)
def bill_reject(request, pk):
    bill = WaterBill.objects.get(id=pk)
    bill.approval_status = 'Rejected'
    bill.save()
    sweetify.toast(request, 'Bill rejected successfully')
    return HttpResponseRedirect(reverse('approve_bills'))



@login_required(login_url='login')
def usage_analytics_view(request):
    if request.user.is_superuser:
        bills = WaterBill.objects.exclude(billing_date__isnull=True).order_by('billing_date')
    else:
        bills = WaterBill.objects.filter(name__user=request.user).exclude(billing_date__isnull=True).order_by('billing_date')

    if request.user.is_superuser:
        bills = WaterBill.objects.exclude(billing_date__isnull=True).order_by('billing_date')
    else:
        bills = WaterBill.objects.filter(name__user=request.user).exclude(billing_date__isnull=True).order_by('billing_date')

    print(f"Bills for user {request.user}: {bills}")

    labels = [bill.billing_date.strftime('%B %Y') for bill in bills]
    data = [bill.meter_consumption for bill in bills]

    print(f"Usage Analytics Labels: {labels}")
    print(f"Usage Analytics Data: {data}")

    average_usage = sum(data) / len(data) if data else 0
    highest_consumption = max(data) if data else 0
    highest_consumption_month = labels[data.index(highest_consumption)] if data else 'N/A'

    context = {
        'title': 'Usage Analytics',
        'labels': labels,
        'data': data,
        'average_usage': average_usage,
        'highest_consumption': highest_consumption,
        'highest_consumption_month': highest_consumption_month,
    }
    return render(request, 'main/usage_analytics.html', context)


@login_required(login_url='login')
def create_checkout_session(request, pk):
    if not settings.STRIPE_SECRET_KEY:
        sweetify.toast(request, 'Stripe is not configured.', icon='error')
        return HttpResponseRedirect(reverse('ongoingbills'))
    bill = WaterBill.objects.get(id=pk)
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': 'php',
                'product_data': {
                    'name': f'Water Bill for {bill.name.first_name} {bill.name.last_name}',
                },
                'unit_amount': int(bill.payable() * 100),
            },
            'quantity': 1,
        }],
        mode='payment',
        success_url=request.build_absolute_uri(reverse('payment_success', args=[bill.id])),
        cancel_url=request.build_absolute_uri(reverse('payment_cancel')),
    )
    return redirect(session.url, code=303)


@login_required(login_url='login')
def payment_success(request, pk):
    bill = WaterBill.objects.get(id=pk)
    bill.payment_status = 'Paid'
    bill.save()
    sweetify.toast(request, 'Payment successful.')
    return HttpResponseRedirect(reverse('billshistory'))


@login_required(login_url='login')
def payment_cancel(request):
    sweetify.toast(request, 'Payment cancelled.', icon='error')
    return HttpResponseRedirect(reverse('ongoingbills'))


@login_required(login_url='login')
@verified_or_superuser
def user_dashboard(request):
    try:
        client = Client.objects.get(user=request.user)
        bills = WaterBill.objects.filter(name=client, approval_status='Approved').order_by('-billing_date')
        metrics = Metric.objects.get(user=request.user)
        print(f"Client found: {client.first_name} {client.last_name}, Meter: {client.meter_number}")
        print(f"Metrics found: Consumption Amount: {metrics.consump_amount}, Penalty Amount: {metrics.penalty_amount}")
    except Client.DoesNotExist:
        client = None
        bills = []
        metrics = None
        print("Client does not exist for this user.")
    except Metric.DoesNotExist:
        metrics = None
        print("Metrics do not exist for this user.")

    context = {
        'title': 'My Meter',
        'client': client,
        'bills': bills,
        'metrics': metrics,
    }
    return render(request, 'main/user_dashboard.html', context)
