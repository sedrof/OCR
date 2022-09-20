from .models import File
from django import forms

class PdffileForm(forms.ModelForm):
    class Meta:
        model = File
        fields = (
            'pdfs',
        )