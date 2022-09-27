from pdf_gen.models import File
from django.db import models
import ocrmypdf
import pdfplumber
from django.urls import reverse
from django.db.models.signals import post_save
from django.conf import settings
from django.contrib.auth import get_user_model
import os
from .helpers import (
    description_func,
    supplier_code_func,
    inv_ref_func,
    invoice_date_func,
    due_date_func,
    total_amount_func,
    total_other_amount_func,
    total_water_rate_func,
    total_water_usage_func,
    meter_length,
    meter_no_func,
)

from .services import extract_text_via_ocr_service


class Invoice(models.Model):
    inv_ref = models.CharField(max_length=100, unique=True)
    user = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, null=True, blank=True
    )
    pdf = models.ForeignKey(
        File,
        on_delete=models.CASCADE,
        related_name="invoice_pdf",
        null=True,
        blank=True,
    )
    description = models.CharField(max_length=500)
    supplier_code = models.IntegerField(null=True)
    supplier_name = models.CharField(max_length=100)
    invoice_date = models.DateField(null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    total_invoice_amount = models.FloatField(null=True)
    total_water_rate = models.FloatField(null=True)
    total_water_usage = models.FloatField(null=True)
    total_other_amount = models.FloatField(null=True)

    def __str__(self):
        return str(self.inv_ref)

    def get_absolute_url(self):
        print("here")
        return reverse("invoices:update", kwargs={"id": self.id})


PDF_DIRECTORY = "pdfdirectory/"


class Meter(models.Model):
    invoice = models.ForeignKey(
        Invoice, on_delete=models.CASCADE, related_name="meters"
    )
    meter_no = models.CharField(max_length=50, null=True)
    meter_type = models.CharField(max_length=50, null=True)
    acc_description = models.CharField(max_length=250, null=True)
    this_reading = models.IntegerField(null=True)
    last_reading = models.IntegerField(null=True)
    consumption = models.IntegerField(null=True)
    average_rate = models.FloatField(null=True)
    other_rate = models.FloatField(null=True)
    consumption_period = models.DateField(null=True, blank=True)
    amount_from_inv = models.FloatField(null=True)
    from_date = models.DateField(null=True, blank=True)
    to_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return str(self.meter_no)


def my_pdf(pdf_filename_path, pdf_page_dir, pdf_name, instance):
    # output = os.system(f'ocrmypdf  D:\easyOCR\OCR\media\pdfdirectory\{pdf_name} {pdf_page_dir}\output.pdf')
    ocrmypdf.ocr(f"{pdf_page_dir}{pdf_name}", f"{pdf_page_dir}output.pdf")

    with pdfplumber.open(f"{pdf_page_dir}output.pdf") as pdf:
        texts = []
        for i in range(len(pdf.pages)):
            page = pdf.pages[i]
            texts.append(page.extract_text(x_tolerance=2))

    line_pages = [line for line in texts]

    pdf_all_pages = ""
    for l in line_pages:
        pdf_all_pages += l

    with open("sampley.txt", "w") as f:
        f.write(pdf_all_pages)
    pdf = File.objects.filter(pdfs=instance.pdfs).first()
    invoice_c, created = Invoice.objects.update_or_create(
        inv_ref=inv_ref_func(pdf_all_pages),
        defaults={
            "description": description_func(pdf_all_pages),
            "pdf": pdf,
            "supplier_code": supplier_code_func(pdf_all_pages),
            "supplier_name": "Sydney Water",
            "invoice_date": invoice_date_func(pdf_all_pages),
            "due_date": due_date_func(pdf_all_pages),
            "total_invoice_amount": total_amount_func(pdf_all_pages),
            "total_water_rate": total_water_rate_func(pdf_all_pages),
            "total_water_usage": total_water_usage_func(pdf_all_pages),
        },
    )
    invoice_c.save()

    meters_len = meter_length(pdf_all_pages)
    print(meter_length(pdf_all_pages), "ffffffffffff")
    for i in range(meters_len):
        print(meter_no_func(pdf_all_pages)[i], "liiiiiiiii")
        meter, created = Meter.objects.update_or_create(
            invoice=invoice_c,
            meter_no=meter_no_func(pdf_all_pages)[i],
            defaults={
                # 'meter_no' : meter_no_func(pdf_all_pages)[i]
            },
        )
        meter.save()


def convert_pdf_to_image(sender, instance, created, **kwargs):
    if created:
        pdf_page_dir = os.path.join(settings.MEDIA_ROOT, PDF_DIRECTORY)
        pdf_name = os.path.basename(instance.pdfs.name)
        pdf_filename_path = os.path.join(pdf_page_dir, pdf_name)
        # print("pdf_page_dir: ",pdf_page_dir,"\n pdf_name: ", pdf_name, "\npdf_filename_path: ", pdf_filename_path)
        print(pdf_filename_path, "naaaame")

        print(extract_text_via_ocr_service(instance.pdfs))

        # my_pdf(pdf_filename_path, pdf_page_dir, pdf_name, instance)


post_save.connect(convert_pdf_to_image, sender=File)
