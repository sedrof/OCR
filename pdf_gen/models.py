from django.db import models
from django.core.validators import FileExtensionValidator
import os

PDF_DIRECTORY = 'pdfdirectory/'

# this function is used to rename the pdf to the name specified by filename field
def set_pdf_file_name(instance, pdf_filename):
    return os.path.join(PDF_DIRECTORY, f'{instance.pdfs.name}')


class File(models.Model):
    # validator checks file is pdf when form submitted
    pdfs = models.FileField(
        upload_to=set_pdf_file_name, 
        validators=[FileExtensionValidator(allowed_extensions=['pdf'])]
        )


