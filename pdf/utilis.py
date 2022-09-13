import os
import ocrmypdf
import pdfplumber
from api.models import Invoice, Meter
from api.helpers import description_func, supplier_code_func,\
                            inv_ref_func, invoice_date_func,\
                                due_date_func, total_amount_func,\
                                    total_other_amount_func, total_water_rate_func,\
                                        total_water_usage_func, meter_length,\
                                            meter_no_func




def my_pdf(file_path, pdf_page_dir):
    os.system(f'ocrmypdf {file_path} {pdf_page_dir}\output.pdf')

    with pdfplumber.open(f'{pdf_page_dir}output.pdf') as pdf:
        texts = []
        for i in range(len(pdf.pages)):
            page = pdf.pages[i]
            texts.append(page.extract_text(x_tolerance=2))

    line_pages = [line for line in texts]

    pdf_all_pages = ''
    for l in line_pages:
        pdf_all_pages += l
    
    with open('sampley.txt', 'w') as f:
        f.write(pdf_all_pages)
    
    invoice_c, created = Invoice.objects.update_or_create(
        inv_ref =inv_ref_func(pdf_all_pages),
        defaults={
            'description': description_func(pdf_all_pages),
            'supplier_code':supplier_code_func(pdf_all_pages),
            'supplier_name':'Sydney Water',
            'invoice_date':invoice_date_func(pdf_all_pages),
            'due_date':due_date_func(pdf_all_pages),
            'total_invoice_amount':total_amount_func(pdf_all_pages),
            'total_water_rate':total_water_rate_func(pdf_all_pages),
            'total_water_usage':total_water_usage_func(pdf_all_pages)
        }

    )
    invoice_c.save()

    meters_len = meter_length(pdf_all_pages)
    print(meter_length(pdf_all_pages), 'ffffffffffff')
    for i in range(meters_len):
        print(meter_no_func(pdf_all_pages)[i], 'liiiiiiiii')
        meter, created = Meter.objects.update_or_create(
            invoice = invoice_c,
            meter_no = meter_no_func(pdf_all_pages)[i],
            defaults={
                # 'meter_no' : meter_no_func(pdf_all_pages)[i]
            }
        )
        meter.save()
