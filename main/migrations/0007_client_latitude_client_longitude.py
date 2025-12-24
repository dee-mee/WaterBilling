# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0006_waterbill_present_reading_waterbill_previous_reading_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='client',
            name='latitude',
            field=models.DecimalField(blank=True, decimal_places=6, help_text='Latitude coordinate for map location', max_digits=9, null=True),
        ),
        migrations.AddField(
            model_name='client',
            name='longitude',
            field=models.DecimalField(blank=True, decimal_places=6, help_text='Longitude coordinate for map location', max_digits=9, null=True),
        ),
    ]

