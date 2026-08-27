from django import forms
from .models import *
from django.core.validators import RegexValidator

class BillForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(BillForm, self).__init__(*args, **kwargs)
        self.fields['payment_status'].initial = 'Pending'

    class Meta:
        model = WaterBill
        fields = ['name', 'previous_reading', 'present_reading', 'meter_consumption', 'payment_status', 'approval_status', 'billing_date', 'duedate', 'penaltydate']
        exclude = ['penalty', 'bill',]
        widgets = {
            'name': forms.Select(attrs={'type': 'text', 'class': 'form-control', 'placeholder':'Name' }),
            'previous_reading': forms.TextInput(attrs={'type': 'number', 'class': 'form-control', 'placeholder':'Previous Reading' }),
            'present_reading': forms.TextInput(attrs={'type': 'number', 'class': 'form-control', 'placeholder':'Present Reading' }),
            'meter_consumption': forms.TextInput(attrs={'type': 'number', 'class': 'form-control', 'placeholder':'Consumption' }),
            'payment_status': forms.Select(attrs={'type': 'text', 'class': 'form-control', 'placeholder':'Pay Status' }),
            'approval_status': forms.Select(attrs={'class': 'form-control', 'placeholder':'Approval Status' }),
            'duedate': forms.TextInput(attrs={'type': 'date', 'class': 'form-control', 'placeholder':'Due Date' }),
            'penaltydate': forms.TextInput(attrs={'type': 'date', 'class': 'form-control', 'placeholder':'Penalty Date' }),
            'billing_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control', 'placeholder':'Billing Date', 'required': 'required'}),
        }


class ClientForm(forms.ModelForm):
    contact_number = forms.CharField(
        max_length=13, 
        required=False,
        validators=[RegexValidator(r'^\+254\d{9}$', 'Enter a valid Kenyan phone number in format +254XXXXXXXXX.')]
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'user' in self.fields:
            self.fields['user'].required = False
        if 'account_number' in self.fields:
            self.fields['account_number'].required = False
        if 'latitude' in self.fields:
            self.fields['latitude'].required = False
        if 'longitude' in self.fields:
            self.fields['longitude'].required = False

    def clean_contact_number(self):
        contact = self.cleaned_data.get('contact_number')
        if not contact or not contact.strip():
            return None
        contact = contact.strip()
        qs = Client.objects.filter(contact_number=contact)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError(f"Contact number {contact} is already assigned to another customer.")
        return contact

    def clean_meter_number(self):
        meter_number = self.cleaned_data.get('meter_number')
        if meter_number:
            qs = Client.objects.filter(meter_number=meter_number)
            if self.instance and self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise forms.ValidationError(f"Meter number {meter_number} is already assigned to another customer.")
        return meter_number

    def clean_account_number(self):
        acc = self.cleaned_data.get('account_number')
        if not acc or not acc.strip():
            return ""
        acc = acc.strip()
        qs = Client.objects.filter(account_number=acc)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError(f"Paybill account number {acc} is already assigned to another customer.")
        return acc

    class Meta:
        model = Client
        fields = ['user', 'first_name', 'middle_name', 'last_name', 'meter_number', 'account_number', 'contact_number', 'address', 'latitude', 'longitude', 'status']
        widgets = {
            'user': forms.Select(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'type': 'text', 'class': 'form-control', 'placeholder':'First Name'}),
            'middle_name': forms.TextInput(attrs={'type': 'text', 'class': 'form-control', 'placeholder':'Middle Name'}),
            'last_name': forms.TextInput(attrs={'type': 'text', 'class': 'form-control', 'placeholder':'Last Name'}),
            'meter_number': forms.TextInput(attrs={'type': 'number', 'class': 'form-control', 'placeholder':'0000000'}),
            'account_number': forms.TextInput(attrs={'type': 'text', 'class': 'form-control', 'placeholder':'Paybill account number'}),
            'address': forms.TextInput(attrs={'type': 'text', 'class': 'form-control', 'placeholder':'House Number, Street, Area'}),
            'latitude': forms.NumberInput(attrs={'type': 'number', 'step': '0.000001', 'class': 'form-control', 'placeholder':'-1.2921', 'id': 'id_latitude'}),
            'longitude': forms.NumberInput(attrs={'type': 'number', 'step': '0.000001', 'class': 'form-control', 'placeholder':'36.8219', 'id': 'id_longitude'}),
            'status': forms.Select(attrs={'class': 'form-control', 'placeholder':'Select'}),
        }


class CustomerForm(forms.ModelForm):
    contact_number = forms.CharField(
        max_length=13, 
        required=False,
        validators=[RegexValidator(r'^\+254\d{9}$', 'Enter a valid Kenyan phone number in format +254XXXXXXXXX.')],
        help_text='Format: +254XXXXXXXXX (optional)'
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'user' in self.fields:
            self.fields['user'].required = False
        if 'first_name' in self.fields:
            self.fields['first_name'].required = False
        if 'last_name' in self.fields:
            self.fields['last_name'].required = False
        if 'account_number' in self.fields:
            self.fields['account_number'].required = False
        if 'contact_number' in self.fields:
            self.fields['contact_number'].required = False
        if 'latitude' in self.fields:
            self.fields['latitude'].required = False
        if 'longitude' in self.fields:
            self.fields['longitude'].required = False

    def clean_contact_number(self):
        contact = self.cleaned_data.get('contact_number')
        if not contact or not contact.strip():
            return None
        contact = contact.strip()
        qs = Client.objects.filter(contact_number=contact)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError(f"Contact number {contact} is already assigned to another customer.")
        return contact

    def clean_meter_number(self):
        meter_number = self.cleaned_data.get('meter_number')
        if meter_number:
            qs = Client.objects.filter(meter_number=meter_number)
            if self.instance and self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise forms.ValidationError(f"Meter number {meter_number} is already assigned to another customer.")
        return meter_number

    def clean_account_number(self):
        acc = self.cleaned_data.get('account_number')
        if not acc or not acc.strip():
            return ""
        acc = acc.strip()
        qs = Client.objects.filter(account_number=acc)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError(f"Paybill account number {acc} is already assigned to another customer.")
        return acc

    class Meta:
        model = Client
        fields = ['user', 'first_name', 'last_name', 'meter_number', 'account_number', 'contact_number', 'address', 'latitude', 'longitude', 'status']
        widgets = {
            'user': forms.Select(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'type': 'text', 'class': 'form-control', 'placeholder': 'First Name (optional if User selected)'}),
            'last_name': forms.TextInput(attrs={'type': 'text', 'class': 'form-control', 'placeholder': 'Last Name (optional if User selected)'}),
            'meter_number': forms.TextInput(attrs={'type': 'number', 'class': 'form-control', 'placeholder':'0000000', 'required': True}),
            'account_number': forms.TextInput(attrs={'type': 'text', 'class': 'form-control', 'placeholder':'Paybill account (auto if blank)'}),
            'address': forms.TextInput(attrs={'type': 'text', 'class': 'form-control', 'placeholder':'House Number, Street, Area', 'required': True}),
            'latitude': forms.NumberInput(attrs={'type': 'number', 'step': '0.000001', 'class': 'form-control', 'placeholder':'-1.2921', 'id': 'id_latitude'}),
            'longitude': forms.NumberInput(attrs={'type': 'number', 'step': '0.000001', 'class': 'form-control', 'placeholder':'36.8219', 'id': 'id_longitude'}),
            'status': forms.Select(attrs={'class': 'form-control', 'placeholder':'Select', 'required': True}),
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