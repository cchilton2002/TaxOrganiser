from flask import Blueprint, request, jsonify
# from werkzeug.utils import secure_filename
import os
from datetime import datetime
from config import UPLOAD_FOLDER, ALLOWED_EXTENSIONS
from backend.database import DatabaseManager
from modules.parse_pdf import extract_payslip_data

finance_bp = Blueprint('finance', __name__)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@finance_bp.route("/upload", methods=["POST"])
def upload_payslip():
    user_id = request.form.get('user_id')
    
    if not user_id:
        return jsonify({"error": "User ID is required"}), 400

    file = request.files.get('file')
    if not file or file.filename == '':
        return jsonify({"error": "No file provided"}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": "Invalid file type"}), 400


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
    
    pension_data = {
        'employee_contribution': parsed_data.get('pension_total', 0),
        'employer_contribution': 0  # set as 0 or extract if available
    }


    # db = DatabaseManager()

    # payslip_id = db.insert_complete_payslip(
    #     user_id=int(user_id),
    #     payment_date=parsed_data['payment_date'],
    #     earnings=earnings,
    #     deductions=deductions,
    #     pension_data=pension_data,
    #     pdf_path=file_path
    # )

    # return jsonify({"message": "Payslip uploaded successfully", "payslip_id": payslip_id}), 201

    payslip_id = 9999  # Just a dummy value for testing

    # Return the parsed data and dummy ID for verification
    return jsonify({
        "message": "Payslip parsed successfully (DB skipped)",
        "parsed_data": parsed_data,
        "earnings": earnings,
        "deductions": deductions,
        "pension_data": pension_data,
        "payslip_id": payslip_id
    }), 200


    




