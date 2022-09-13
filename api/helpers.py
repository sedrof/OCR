import re
from .validations import validate_time, mtn




def total_amount_func(pdf_all_pages):
    patterns = re.compile(r'[$](\d{3}|\d{4}|\d{2}|\d{1})[.](\d{2}|\d{1})')
    matches = patterns.finditer(pdf_all_pages)
    total_amount = [ result.group(0) for result in matches][-1].split('$')[-1]
    return float(total_amount)

def inv_ref_func(pdf_all_pages):
    patterns = re.compile(r'\d{4}\s{2}\d{3}\s{2}\d{4}')
    matches = patterns.finditer(pdf_all_pages)
    ref = [ result.group(0) for result in matches][0].replace(" ",'')
    return int(ref)

def description_func(pdf_all_pages):
    patterns = re.compile(r'(PARRAMATTA\s\sWESTFIELD|AnyThingElse)\s{2}\w{3}\s{2}\d{4}')
    matches = patterns.finditer(pdf_all_pages)
    ref = [ result.group(0) for result in matches][0]
    return ref

def supplier_code_func(pdf_all_pages):
    patterns = patt = re.compile(r'Biller\s{2}code:\s{2}\d{5}')
    matches = patterns.finditer(pdf_all_pages)
    ref = [result.group(0) for result in matches][0].split()[-1]
    return ref

def invoice_date_func(pdf_all_pages):
    patterns = re.compile(r'Date\s{2}of(\s{2}|\s{1})issue\s{2}(\d{2}|\d)\s{2}\w{3}\s{2}\d{4}')
    matches = patterns.finditer(pdf_all_pages)
    ref = [result.group(0) for result in matches][0].split()
    new = mtn(ref[-2])
    date = str(ref[-3]) + " " + str(new) + " " + str(ref[-1])
    new_data = validate_time(date.replace(" ", '/'))

    return new_data

def due_date_func(pdf_all_pages):
    patterns = re.compile(r'\d{2}/\d{2}/\d{2}')
    matches = patterns.finditer(pdf_all_pages)
    ref = [result.group(0) for result in matches][0]
    year_4_char = int(ref.split('/')[-1]) + int(2000)
    month = ref.split('/')[-2]
    day = ref.split('/')[0]
    date = str(year_4_char) + "-" + str(month) + "-" + str(day)
    return date

def total_water_usage_func(pdf_all_pages):
    patterns = re.compile(r'details\s{2}(\d{1}|\d{2}|\d{3}|\d{4}).(\d{2})')
    matches = patterns.finditer(pdf_all_pages)
    ref = [result.group(0) for result in matches][0].split()[-1]
    return float(ref)

def total_water_rate_func(pdf_all_pages):
    patterns = re.compile(r'\d{2}/\d{2}\s{2}\d{2}')
    matches = patterns.finditer(pdf_all_pages)
    ref = [result.group(0) for result in matches][0].split()[-1]
    return float(ref)

def total_other_amount_func(pdf_all_pages):
    patterns = re.compile(r'\d{2}/\d{2}\s{2}\d{2}')
    matches = patterns.finditer(pdf_all_pages)
    ref = [result.group(0) for result in matches][0].split()[-1]
    return ref

def meter_length(pdf_all_pages):
    meter_numbers = re.compile(r'[A-Z](\w{3}|\w{4}|\w{5}|\w{6})\d{3}\s{2}\d')
    meter_numbers_matches = meter_numbers.finditer(pdf_all_pages)
    meter_numbers_ref = [result.group(0) for result in meter_numbers_matches]

    return len(meter_numbers_ref)

def meter_no_func(pdf_all_pages):
    patterns = re.compile(r'[A-Z](\w{3}|\w{4}|\w{5}|\w{6})\d{3}\s{2}\d')
    matches = patterns.finditer(pdf_all_pages)
    ref = [result.group(0) for result in matches]
    final_list = []
    for i in range(len(ref)):
        final_list.append(ref[i].split(' ',1)[0])

    return final_list
