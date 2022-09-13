from django.db import models
from . utilis import  my_pdf
from django.core.validators import FileExtensionValidator
from django.db.models.signals import post_save
from django.conf import settings
import os

PDF_DIRECTORY = 'pdfdirectory/'

# this function is used to rename the pdf to the name specified by filename field
def set_pdf_file_name(instance, pdf_filename):
    return os.path.join(PDF_DIRECTORY, f'{instance.pdf.name}')


class Pdffile(models.Model):
    # validator checks file is pdf when form submitted
    pdf = models.FileField(
        upload_to=set_pdf_file_name, 
        validators=[FileExtensionValidator(allowed_extensions=['pdf'])]
        )

def convert_pdf_to_image(sender, instance, created, **kwargs):
    if created:
        pdf_page_dir = os.path.join(settings.MEDIA_ROOT, PDF_DIRECTORY)
        pdf_name = os.path.basename(instance.pdf.name)
        pdf_filename_path = os.path.join(pdf_page_dir, pdf_name)

        
        my_pdf(pdf_filename_path, pdf_page_dir)


post_save.connect(convert_pdf_to_image, sender=Pdffile)
