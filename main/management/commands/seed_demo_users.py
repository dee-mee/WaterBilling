from django.core.management.base import BaseCommand
from account.models import Account
from main.models import Client


class Command(BaseCommand):
    help = 'Seeds the database with demo users for testing'

    def handle(self, *args, **options):
        # Create admin user
        admin_email = 'admin@example.com'
        admin_password = '12345678'
        
        if not Account.objects.filter(email=admin_email).exists():
            admin = Account.objects.create_superuser(
                email=admin_email,
                password=admin_password,
                first_name='Admin',
                last_name='User'
            )
            self.stdout.write(
                self.style.SUCCESS(f'✓ Created admin user: {admin_email}')
            )
        else:
            self.stdout.write(
                self.style.WARNING(f'⚠ Admin user already exists: {admin_email}')
            )

        # Create customer user
        customer_email = 'user1@gmail.com'
        customer_password = 'password'
        
        if not Account.objects.filter(email=customer_email).exists():
            customer = Account.objects.create_user(
                email=customer_email,
                password=customer_password,
                first_name='John',
                last_name='Customer'
            )
            
            # Create associated client if not exists
            if not Client.objects.filter(user=customer).exists():
                client = Client.objects.create(
                    user=customer,
                    meter_number=1001,
                    contact_number='+254712345678',
                    address='Nairobi, Kenya',
                    status='Connected'
                )
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Created customer user: {customer_email}')
                )
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Created client profile with meter: {client.meter_number}')
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Created customer user: {customer_email}')
                )
                self.stdout.write(
                    self.style.WARNING(f'⚠ Client profile already exists')
                )
        else:
            self.stdout.write(
                self.style.WARNING(f'⚠ Customer user already exists: {customer_email}')
            )

        self.stdout.write(
            self.style.SUCCESS('\n✓ Demo users seed completed!')
        )
        self.stdout.write(
            self.style.SUCCESS('Admin login: admin@example.com / 12345678')
        )
        self.stdout.write(
            self.style.SUCCESS('Customer login: user1@gmail.com / password')
        )
