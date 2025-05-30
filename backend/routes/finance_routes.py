from flask import Blueprint, request, jsonify
# from werkzeug.utils import secure_filename
import os
from datetime import datetime
from config.settings import UPLOAD_FOLDER, ALLOWED_EXTENSIONS
from backend.database import DatabaseManager
from modules.parse_pdf import extract_payslip_data
from modules.missing_payslips import find_missing_payslips

finance_bp = Blueprint('finance', __name__)




def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@finance_bp.route("/upload", methods=["POST"])
def upload_payslip():
    user_id = request.form.get('user_id')

    if not user_id:
        return jsonify({"error": "User ID is required"}), 400
        

    files = request.files.getlist('files')
    
    if not files or all(f.filename == '' for f in files):
        return jsonify({"error": "No files provided"}), 400

    db = DatabaseManager()
    uploaded_ids = []

    for file in files:
        if not allowed_file(file.filename):
            continue  # Skip invalid file types

        filename = file.filename
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)

        parsed_data = extract_payslip_data(file_path)

        earnings = []
        if 'total_pay' in parsed_data:
            earnings.append({'type': 'Total Pay', 'amount': parsed_data['total_pay']})
        if 'holiday_pay' in parsed_data:
            earnings.append({'type': 'Holiday Pay', 'amount': parsed_data['holiday_pay']})
        if 'service_charge' in parsed_data:
            earnings.append({'type': 'Service Charge', 'amount': parsed_data['service_charge']})

        deductions = []
        if 'tax' in parsed_data:
            deductions.append({'type': 'Income Tax', 'amount': parsed_data['tax']})
        if 'national_insurance' in parsed_data:
            deductions.append({'type': 'National Insurance', 'amount': parsed_data['national_insurance']})
        if 'employee_contribution' in parsed_data:
            deductions.append({'type': 'Pension', 'amount': parsed_data['employee_contribution']})

        pension_data = [
            {'type': 'employee_contribution', 'amount': parsed_data.get('employee_contribution', 0)},
            {'type': 'employer_contribution', 'amount': parsed_data.get('employer_contribution', 0)}
        ]

        payslip_id = db.insert_complete_payslip(
            user_id=int(user_id),
            username="cchilton2002",
            email="christoph0295@gmail.com",
            password_hash="this_is_a_password_hash",
            payment_date=parsed_data['payment_date'],
            earning=earnings,
            deductions=deductions,
            pension_data=pension_data,
            pdf_path=file_path
        )

        uploaded_ids.append(payslip_id)

    return jsonify({
        "message": f"{len(uploaded_ids)} payslip(s) uploaded successfully",
        "uploaded_ids": uploaded_ids
    }), 201


@finance_bp.route('/summary', methods=["GET"])
def get_summary():
    user_id = request.args.get('user_id')
    tax_year = 2025    
    db = DatabaseManager()
    
    summary = db.get_summaries(user_id)
    
    uploaded_dates = db.get_summary_dates(user_id, tax_year)
    
    missing_dates = find_missing_payslips(2025, uploaded_dates)

    return jsonify({
        "message": "Summary returned",
        "user_id": user_id,
        "summary": summary ,
        "missing_payslips": missing_dates
    }), 200



    




