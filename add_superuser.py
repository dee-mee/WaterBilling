#!/usr/bin/env python
import os
import sys
import django

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from account.models import Account

def create_admin_user():
    """Create admin user with specified credentials"""
    email = "admin@example.com"
    password = "12345678"
    
    # Check if admin user already exists
    if Account.objects.filter(email=email).exists():
        print(f"Admin user {email} already exists")
        return
    
    # Create admin user
    try:
        admin_user = Account.objects.create_superuser(
            email=email,
            password=password
        )
        print(f"Admin user {email} created successfully")
    except Exception as e:
        print(f"Error creating admin user: {e}")

if __name__ == "__main__":
    create_admin_user()