from django.shortcuts import render, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.urls import reverse
from .forms import *
from .models import Account
from main.models import *
from django.conf import settings
import sweetify
import secrets
import string
import smtplib
from django.utils.crypto import constant_time_compare
from django.utils import timezone
import datetime
import logging

logger = logging.getLogger(__name__)

OTP_EXPIRY_MINUTES = 10
OTP_MAX_ATTEMPTS = 5


def landingpage(request):
    return render(request, 'account/landingpage.html')


def generate_otp():
    return "".join(secrets.choice(string.digits) for _ in range(6))


User = get_user_model()


def login_view(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        remember_me = request.POST.get('remember_me')
        user = authenticate(request, email=email, password=password)
        if user is not None:
            # Check if user is approved by admin (superusers are always approved)
            if not user.is_superuser and not user.admin_approved:
                sweetify.error(request, 'Your account is pending admin approval. Please wait for an administrator to approve your account.')
                return render(request, 'account/login.html', {'error': 'Account pending approval'})
            
            if settings.OTP:
                login(request, user)
                if user.verified:
                    sweetify.success(request, 'Login Successfully')
                    return HttpResponseRedirect(reverse('ongoingbills'))
                elif user.is_superuser:
                    if not Metric.objects.all():
                        Metric.objects.create(consump_amount=1,penalty_amount=1)
                    sweetify.success(request, 'Login Successfully')
                    return HttpResponseRedirect(reverse('dashboard'))
                elif not user.verified:
                    login(request, user)
                    user = request.user
                    otp = generate_otp()
                    user.otp = int(otp)
                    user.otp_created_at = timezone.now()
                    user.otp_attempts = 0
                    user.save()
                    try:
                        SENDER_EMAIL = settings.OTP_EMAIL
                        SENDER_PASSWORD = settings.OTP_PASSWORD
                        SUBJECT = "OTP Verification"
                        TEXT = otp
                        MESSAGE = 'Subject: {}\n\n{}'.format(SUBJECT, TEXT)
                        RECEIVER_EMAIL = email
                        SERVER = smtplib.SMTP('smtp.gmail.com', 587)
                        SERVER.starttls()
                        SERVER.login(SENDER_EMAIL, SENDER_PASSWORD)
                        SERVER.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, MESSAGE)
                    except Exception as e:
                        logger.error(f"Email sending failed: {e}")
                        return HttpResponseRedirect(reverse('verify'))
                    sweetify.success(request, 'Check your email for verification')
                    return HttpResponseRedirect(reverse('verify'))
            else:
                #Bypass OTP
                login(request, user)
                # Handle Remember Me: if not checked, expire session on browser close
                if not remember_me:
                    request.session.set_expiry(0)
                else:
                    # Two weeks
                    request.session.set_expiry(60 * 60 * 24 * 14)
                user = request.user
                user.verified = True
                user.save()
                sweetify.success(request, 'Login Successfully')
                if not user.is_superuser:
                    return HttpResponseRedirect(reverse('ongoingbills'))
                else:
                    return HttpResponseRedirect(reverse('dashboard'))
        else:
            sweetify.error(request, 'Invalid Credentialss')
            return render(request, 'account/login.html', {'error': 'Invalid Credentials'})
    return render(request, 'account/login.html')


def forgot_password_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        # Always return same message to prevent email enumeration
        safe_message = 'If an account exists with that email, a password reset link has been sent.'
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return render(request, 'account/forgot_password.html', {'message': safe_message})

        # Reuse OTP field as reset code
        code = generate_otp()
        user.otp = int(code)
        user.otp_created_at = timezone.now()
        user.otp_attempts = 0
        user.save()

        try:
            SENDER_EMAIL = settings.OTP_EMAIL
            SENDER_PASSWORD = settings.OTP_PASSWORD
            SUBJECT = "Password Reset Code"
            TEXT = f"Your password reset code is: {code}"
            MESSAGE = 'Subject: {}\n\n{}'.format(SUBJECT, TEXT)
            RECEIVER_EMAIL = email
            SERVER = smtplib.SMTP('smtp.gmail.com', 587)
            SERVER.starttls()
            SERVER.login(SENDER_EMAIL, SENDER_PASSWORD)
            SERVER.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, MESSAGE)
            SERVER.quit()
        except Exception as e:
            logger.error(f"Password reset email failed for {email}: {e}")
            # Even if email fails, return same message to prevent enumeration
            return render(request, 'account/forgot_password.html', {'message': safe_message})

        return render(request, 'account/forgot_password.html', {
            'message': safe_message
        })

    return render(request, 'account/forgot_password.html')


def reset_password_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        code = request.POST.get('code')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')

        if password != password2:
            return render(request, 'account/reset_password.html', {
                'error': 'Passwords do not match.'
            })

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return render(request, 'account/reset_password.html', {
                'error': 'No account found with that email.'
            })

        # Check OTP expiration
        if user.otp_created_at:
            otp_age = timezone.now() - user.otp_created_at
            if otp_age > datetime.timedelta(minutes=OTP_EXPIRY_MINUTES):
                return render(request, 'account/reset_password.html', {
                    'error': 'Reset code has expired. Please request a new one.'
                })
        
        # Check OTP attempts
        if user.otp_attempts >= OTP_MAX_ATTEMPTS:
            return render(request, 'account/reset_password.html', {
                'error': 'Too many failed attempts. Please request a new reset code.'
            })

        # Validate code with constant-time comparison
        try:
            if not user.otp or not constant_time_compare(str(user.otp), code):
                user.otp_attempts += 1
                user.save()
                return render(request, 'account/reset_password.html', {
                    'error': 'Invalid reset code.'
                })
        except (TypeError, ValueError):
            return render(request, 'account/reset_password.html', {
                'error': 'Invalid reset code.'
            })

        # Set new password
        user.set_password(password)
        user.otp = None
        user.otp_created_at = None
        user.otp_attempts = 0
        user.save()

        sweetify.success(request, 'Password updated successfully. You can now log in.')
        return HttpResponseRedirect(reverse('login'))

    return render(request, 'account/reset_password.html')


def verify(request):
    otp_form = VerificationForm()
    context = {
        'otp_form': otp_form
    }
    if request.method == 'POST':
        user = request.user
        otp_form = VerificationForm(request.POST)
        user_otp = request.POST.get('otp', '')
        
        # Check OTP expiration
        if user.otp_created_at:
            otp_age = timezone.now() - user.otp_created_at
            if otp_age > datetime.timedelta(minutes=OTP_EXPIRY_MINUTES):
                return render(request, 'account/verify.html', {
                    'error': 'OTP has expired. Please login again to get a new one.',
                    'otp_form': otp_form
                })
        
        # Check attempt limit
        if user.otp_attempts >= OTP_MAX_ATTEMPTS:
            return render(request, 'account/verify.html', {
                'error': 'Too many failed attempts. Please login again.',
                'otp_form': otp_form
            })
        
        # Verify OTP with constant-time comparison
        try:
            if user.otp and constant_time_compare(str(user.otp), user_otp):
                user.verified = True
                user.otp = None
                user.otp_created_at = None
                user.otp_attempts = 0
                user.save()
                sweetify.success(request, 'Login Successfully')
                return HttpResponseRedirect(reverse('ongoingbills'))
            else:
                user.otp_attempts += 1
                user.save()
                return render(request, 'account/verify.html', {
                    'error': 'OTP is incorrect!',
                    'otp_form': otp_form
                })
        except (TypeError, ValueError):
            user.otp_attempts += 1
            user.save()
            return render(request, 'account/verify.html', {
                'error': 'Invalid OTP format!',
                'otp_form': otp_form
            })

    return render(request, 'account/verify.html', context)


def register_view(request):
    Registration_Form = RegistrationForm()
    if request.method == 'POST':
        Registration_Form = RegistrationForm(request.POST)
        email = request.POST['email']
        password1 = request.POST['password']
        password2 = request.POST['password2']
        if password1 != password2:
            sweetify.error(request, 'Password do not match!')
            return render(request, 'account/register.html', {'error': 'Password do not match!', 'Registration_Form':Registration_Form})
        elif Registration_Form.is_valid():
            user = Registration_Form.save()
            # New users are not approved by default
            user.admin_approved = False
            user.save()
            sweetify.success(request, 'Registration Successful. Your account is pending admin approval.')
            return HttpResponseRedirect(reverse('login'))
        elif Account.objects.filter(email=email).exists():
            sweetify.error(request, 'Email already exist!')
            return render(request, 'account/register.html', {'error': 'Email already exist!','Registration_Form':Registration_Form})
        else:
            sweetify.error(request, 'Invalid Credentials!')
            return render(request, 'account/register.html', {'error': 'Invalid Credentials!','Registration_Form':Registration_Form})
    return render(request, 'account/register.html', {'Registration_Form':Registration_Form})


def logout_view(request):
    logout(request)
    return render(request, 'account/login.html')

