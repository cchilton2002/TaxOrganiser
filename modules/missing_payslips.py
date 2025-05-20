import datetime
from datetime import date, timedelta
from typing import List

def get_expected_payslip_dates(tax_year: int) -> List[date]:
    bank_holidays = set([
        date(2025, 4, 18),
        date(2025, 4, 21),
        date(2025, 5, 5),
        date(2025, 5, 26),
        date(2025, 8, 25),
        date(2025, 12, 25),
        date(2025, 12, 26),
        date(2026, 1, 1),
        date(2026, 4, 3),
        date(2026, 4, 6),
    ])
    
    dates = []
    today = date.today()
    start_date = date(tax_year, 4, 6)
    end_date = min(today, date(tax_year + 1, 4, 5))
    
    while start_date.weekday() != 0:
        start_date += timedelta(days=1)

    current = start_date

    while current <= end_date:
        payday = current
        if payday in bank_holidays:
            friday_before = payday - timedelta(days=3)
            if friday_before in bank_holidays:
                payday -= timedelta(days=4)
            else:
                payday -= timedelta(days=3)
        dates.append(payday)
        current += timedelta(weeks=1)

    return dates

def find_missing_payslips(tax_year: int, uploaded_dates) -> List[date]:
    uploaded_set = set()
    for d in uploaded_dates:
        payment_date = d['payment_date']
        # Handle both string and date objects
        if isinstance(payment_date, str):
            date_obj = datetime.datetime.strptime(payment_date, "%Y-%m-%d").date()
        else:
            date_obj = payment_date  # Assume it's already a date object
        uploaded_set.add(date_obj)

    expected_dates = get_expected_payslip_dates(tax_year)
    missing_dates = [d for d in expected_dates if d not in uploaded_set]
    return [d.isoformat() for d in missing_dates]


