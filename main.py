import pandas as pd
from typing import Dict, Optional
import pdfplumber  
import re
import io
import contextlib

def extract_payslip_data(pdf_path: str) -> Dict[str, Optional[float]]:
    data= {
        "date" : None,
        "pay" : None,
        "tax" : None,
        "pension" : None,
        "service_charge" : None,
        "holidays" : None,
        "national_insurance" : None
    }
    
    text = extract_text_from_pdf(pdf_path)
    
    date_match = re.search(r'\d{2}/\d{2}/\d{4}', text)
    pay_match = re.search(r'Total Payments\s+(\d+\.\d{2})', text)
    tax_match = re.search(r'Tax\s+(\d+\.\d{2})', text)
    ni_match = re.search(r'National Ins.\s+(\d+\.\d{2})',text)
    hol_match = re.search(r'HOL DAYS HRS\s+(\d+\.\d{2})',text)
    service_charge_match = re.search(r'Service Charge Non Ni-able\s+(\d+\.\d{2})',text)
    
    pension_matches = re.findall(r'(Worksave Pension Plan)[^\d]*(\d+\.\d{2})', text)



        # Store values
    if pay_match:
        data['total_payments'] = float(pay_match.group(1))
    if tax_match:
        data['tax'] = float(tax_match.group(1))
    if ni_match:
        data['national_insurance'] = float(ni_match.group(1))
    if hol_match:
        data['holiday_pay'] = float(hol_match.group(1))
    if service_charge_match:
        data['service_charge'] = float(service_charge_match.group(1))
    if pension_matches:
        data['pension_deduction'] = float(pension_matches[0][1])
        data['pension_contribution'] = float(pension_matches[1][1])

        
        # Calculate net pay if we have the required values
    if data['total_payments'] is not None and data['tax'] is not None:
        data['net_pay'] = data['total_payments'] - data['tax']
        if data['national_insurance'] is not None:
            data['net_pay'] -= data['national_insurance']
        if data['pension_deduction'] is not None:
            data['net_pay'] -= data['pension_deduction']

    return data

def extract_text_from_pdf(pdf_path: str) -> str:
    text = ""
    with contextlib.redirect_stderr(io.StringIO()):
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""  # Handle None returns
    return text

data = extract_payslip_data("document.pdf")
print(data)