from functools import wraps
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from main.models import *
import sweetify


def verified_or_superuser(function):
  @wraps(function)
  def wrap(request, *args, **kwargs):
        profile = request.user
        # Superusers are always allowed
        if profile.is_superuser:
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



