# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='account',
            name='admin_approved',
            field=models.BooleanField(default=False, help_text='Designates whether this user has been approved by an admin.'),
        ),
    ]

