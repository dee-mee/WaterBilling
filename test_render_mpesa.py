#!/usr/bin/env python
"""
Quick test script for M-Pesa configuration on Render
Run this on your Render server using: python test_render_mpesa.py
"""
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.conf import settings

print("=== M-Pesa Configuration Check ===")
print(f"Environment: {settings.MPESA_ENV}")
print(f"Shortcode: {settings.MPESA_SHORTCODE}")
print(f"Callback URL: {settings.MPESA_CALLBACK_BASE_URL}")
print(f"Consumer Key: {settings.MPESA_CONSUMER_KEY[:10]}...")
print(f"Consumer Secret: {settings.MPESA_CONSUMER_SECRET[:10]}...")
print()

print("=== Testing OAuth Token ===")
try:
    from payments.mpesa import get_access_token
    token = get_access_token()
    print(f"✅ OAuth Token obtained: {token[:20]}...")
except Exception as e:
    print(f"❌ OAuth Token failed: {e}")

print()
print("=== Next Steps ===")
print("1. Register C2B URLs: python manage.py register_mpesa_c2b_urls")
print("2. Test simulation: python manage.py simulate_mpesa_c2b ACCOUNT AMOUNT")
print("3. Check admin: https://waterbilling-r92q.onrender.com/admin/")
print("4. Test webhooks with curl commands from RENDER_ENV_SETUP.md")