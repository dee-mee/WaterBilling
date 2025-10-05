
from django.core.management.base import BaseCommand
from django.db import transaction
from account.models import Account
from main.models import Client

class Command(BaseCommand):
    help = 'Tests if a user can see their assigned meter.'

    def handle(self, *args, **options):
        test_user = None
        test_client = None

        try:
            with transaction.atomic():
                # Step 1: Create a test user
                self.stdout.write('Step 1: Creating a test user...')
                test_user, _ = Account.objects.get_or_create(
                    email='testuser@example.com',
                    defaults={'first_name': 'Test', 'last_name': 'User'}
                )
                self.stdout.write(self.style.SUCCESS(f'   -> Created user: {test_user.email}'))

                # Step 2: Simulate admin assigning a meter to the test user
                self.stdout.write('Step 2: Simulating admin assigning a meter...')
                test_client = Client.objects.create(
                    user=test_user,
                    meter_number=999999,
                    address='123 Test Street',
                    status='Connected'
                )
                self.stdout.write(self.style.SUCCESS(f'   -> Created client and assigned to {test_user.email}'))

                # Step 3: Verify the assignment
                self.stdout.write('Step 3: Checking if the user can see the meter...')
                # This simulates the query in the user_dashboard view
                fetched_client = Client.objects.get(user=test_user)

                if fetched_client.meter_number == test_client.meter_number:
                    self.stdout.write(self.style.SUCCESS('   -> Verification successful. The user is correctly linked to the meter.'))
                    self.stdout.write("\n" + "="*30)
                    self.stdout.write(self.style.SUCCESS('    TEST PASSED SUCCESSFULLY'))
                    self.stdout.write("="*30 + "\n")
                else:
                    raise Exception("Fetched client does not match the created client.")

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'An error occurred during the test: {e}'))
            self.stdout.write("\n" + "="*30)
            self.stdout.write(self.style.ERROR('    TEST FAILED'))
            self.stdout.write("="*30 + "\n")

        finally:
            # Step 4: Clean up test data
            self.stdout.write('Step 4: Cleaning up test data...')
            if test_client:
                test_client.delete()
                self.stdout.write(self.style.SUCCESS('   -> Deleted test client.'))
            if test_user:
                test_user.delete()
                self.stdout.write(self.style.SUCCESS('   -> Deleted test user.'))
