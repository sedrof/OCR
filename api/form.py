from django import forms
from .models import *


class InvoiceEditForm(forms.ModelForm):
    required_css_class = 'required-field'
    inv_ref = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control", "style":"width:30%;"}))
    description = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control", "style":"width:30%;"}))
    supplier_code = forms.IntegerField(widget=forms.NumberInput(attrs={"class": "form-control", "style":"width:30%;"}))
    supplier_name = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control", "style":"width:30%;"}))
    total_invoice_amount = forms.FloatField(widget=forms.NumberInput(attrs={"class": "form-control", "style":"width:30%;"}))

    class Meta:
        model = Invoice
        fields = (
            "inv_ref",
            "description",
            "supplier_code",
            "supplier_name",
            "total_invoice_amount",
        )


class MeterEditForm(forms.ModelForm):
    meter_no = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control", "style":"width:30%;"}))
    meter_type = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control", "style":"width:30%;"}))
    acc_description = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control", "style":"width:30%;"}))
    this_reading = forms.FloatField(widget=forms.NumberInput(attrs={"class": "form-control", "style":"width:30%;"}))
    class Meta:
        model = Meter
        fields = ("meter_no", "meter_type", "acc_description", "this_reading")
