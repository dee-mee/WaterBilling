from functools import wraps
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from main.models import *
import sweetify


def verified_or_superuser(function):
  @wraps(function)
  def wrap(request, *args, **kwargs):
        profile = request.user
        # Superusers and staff are always allowed
        if profile.is_superuser or profile.is_staff:
             return function(request, *args, **kwargs)
        # Check if user is verified (OTP) and approved by admin
        if profile.verified and profile.admin_approved:
             return function(request, *args, **kwargs)
        # If not verified, redirect to verification
        elif not profile.verified:
            return HttpResponseRedirect(reverse('verify'))
        # If rejected, show rejection message
        elif hasattr(profile, 'rejected') and profile.rejected:
            sweetify.error(request, 'Your account has been rejected by an administrator. Please contact support for assistance.')
            return HttpResponseRedirect(reverse('login'))
        # If not approved by admin, show message and redirect to login
        else:
            sweetify.error(request, 'Your account is pending admin approval. Please wait for an administrator to approve your account.')
            return HttpResponseRedirect(reverse('login'))

  return wrap


def staff_required(function):
    @wraps(function)
    @login_required(login_url='login')
    def wrap(request, *args, **kwargs):
        if request.user.is_staff or request.user.is_superuser:
            return function(request, *args, **kwargs)
        else:
            sweetify.error(request, 'You do not have permission to access this page.')
            return HttpResponseRedirect(reverse('ongoingbills'))
    return wrap



