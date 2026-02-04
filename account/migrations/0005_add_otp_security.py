# Generated migration for OTP security improvements

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0004_account_rejection_reason'),
    ]

    operations = [
        migrations.AddField(
            model_name='account',
            name='otp_created_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='account',
            name='otp_attempts',
            field=models.IntegerField(default=0),
        ),
    ]
