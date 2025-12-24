from django import forms
from .models import *
from django.core.validators import RegexValidator

class BillForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(BillForm, self).__init__(*args, **kwargs)
        self.fields['payment_status'].initial = 'Pending'

    class Meta:
        model = WaterBill
        fields = ['name','meter_consumption', 'payment_status', 'billing_date', 'duedate', 'penaltydate']
        exclude = ['penalty', 'bill',]
        widgets = {
            'name': forms.Select(attrs={'type': 'text', 'class': 'form-control', 'placeholder':'Name' }),
            'meter_consumption': forms.TextInput(attrs={'type': 'number', 'class': 'form-control', 'placeholder':'00000000' }),
            'payment_status': forms.Select(attrs={'type': 'text', 'class': 'form-control', 'placeholder':'Pay Status' }),
            'duedate': forms.TextInput(attrs={'type': 'date', 'class': 'form-control', 'placeholder':'Due Date' }),
            'penaltydate': forms.TextInput(attrs={'type': 'date', 'class': 'form-control', 'placeholder':'Penalty Date' }),
            'billing_date': forms.TextInput(attrs={'type': 'date', 'class': 'form-control', 'placeholder':'Billing Date' }),
        }


class ClientForm(forms.ModelForm):
    contact_number = forms.CharField(max_length=13, validators=[RegexValidator(r'^\+254\d{9}$', 'Enter a valid Kenyan phone number.')])

    class Meta:
        model = Client
        fields = ['user', 'meter_number', 'contact_number', 'address', 'latitude', 'longitude', 'status']
        widgets = {
            'meter_number': forms.TextInput(attrs={'type': 'number', 'class': 'form-control', 'placeholder':'0000000' }),
            'first_name': forms.TextInput(attrs={'type': 'text', 'class': 'form-control', 'placeholder':'First Name' }),
            'middle_name': forms.TextInput(attrs={'type': 'text', 'class': 'form-control', 'placeholder':'Middle Name' }),
            'last_name': forms.TextInput(attrs={'type': 'text', 'class': 'form-control', 'placeholder':'Last Name' }),
            'address': forms.TextInput(attrs={'type': 'text', 'class': 'form-control', 'placeholder':'House Number, Street, Area' }),
            'latitude': forms.NumberInput(attrs={'type': 'number', 'step': '0.000001', 'class': 'form-control', 'placeholder':'-1.2921', 'id': 'id_latitude'}),
            'longitude': forms.NumberInput(attrs={'type': 'number', 'step': '0.000001', 'class': 'form-control', 'placeholder':'36.8219', 'id': 'id_longitude'}),
            'status': forms.Select(attrs={'class': 'form-control', 'placeholder':'Select' }),
        }


class CustomerForm(forms.ModelForm):
    contact_number = forms.CharField(max_length=13, validators=[RegexValidator(r'^\+254\d{9}$', 'Enter a valid Kenyan phone number.')])

    class Meta:
        model = Client
        fields = ['user', 'meter_number', 'contact_number', 'address', 'latitude', 'longitude', 'status']
        widgets = {
            'user': forms.Select(attrs={'class': 'form-control'}),
            'meter_number': forms.TextInput(attrs={'type': 'number', 'class': 'form-control', 'placeholder':'0000000' }),
            'address': forms.TextInput(attrs={'type': 'text', 'class': 'form-control', 'placeholder':'House Number, Street, Area' }),
            'latitude': forms.NumberInput(attrs={'type': 'number', 'step': '0.000001', 'class': 'form-control', 'placeholder':'-1.2921', 'id': 'id_latitude'}),
            'longitude': forms.NumberInput(attrs={'type': 'number', 'step': '0.000001', 'class': 'form-control', 'placeholder':'36.8219', 'id': 'id_longitude'}),
            'status': forms.Select(attrs={'class': 'form-control', 'placeholder':'Select' }),
        }


class MetricsForm(forms.ModelForm):
    class Meta:
        model = Metric
        fields = ['consump_amount', 'penalty_amount']
        widgets = {
            'consump_amount': forms.TextInput(attrs={'type': 'number', 'class': 'form-control', 'placeholder':'00000000' }),
            'penalty_amount': forms.TextInput(attrs={'type': 'number', 'class': 'form-control', 'placeholder':'00000000' })
        }

class BulkUploadForm(forms.Form):
    csv_file = forms.FileField()