import os
import sys
import time
from pathlib import Path
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

from db import get_db_connection

# Add OS module directory to Python path
OS_MODULE_DIR = Path(__file__).resolve().parent.parent / "os_module"
if str(OS_MODULE_DIR) not in sys.path:
    sys.path.append(str(OS_MODULE_DIR))

try:
    import cpu_scheduling
    import page_replacement
    import bankers_algorithm
    import disk_scheduling
    import process_sync
    import memory_management
    import process_management
except ImportError:
    cpu_scheduling = None
    page_replacement = None
    bankers_algorithm = None
    disk_scheduling = None
    process_sync = None
    memory_management = None
    process_management = None

# Resolve frontend directory path
FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"

app = Flask(__name__, static_folder=str(FRONTEND_DIR), static_url_path="")
CORS(app)

# In-memory storage for offline / demonstration mode when MySQL is not connected
IN_MEMORY_APPLICATIONS = [
    {
        "application_id": 1001,
        "applicant_name": "Major Rajesh Sharma (Retd)",
        "applicant_email": "rajesh.sharma@example.com",
        "service_no": "IC-49821M",
        "service_category": "EX-SERVICEMEN",
        "scheme_id": 2,
        "scheme_name": "Ex-Servicemen Medical Support",
        "current_status": "APPROVED",
        "submission_date": "2026-10-12 10:30:00",
        "documents": [
            {"id": "doc_1001_1", "name": "Discharge_Book_IC49821M.pdf", "type": "Service Discharge Book", "size": "2.4 MB", "status": "VERIFIED", "uploaded_at": "2026-10-12 10:32:00"},
            {"id": "doc_1001_2", "name": "ECHS_Smart_Card.pdf", "type": "ECHS Beneficiary Card", "size": "1.1 MB", "status": "VERIFIED", "uploaded_at": "2026-10-12 10:33:00"},
            {"id": "doc_1001_3", "name": "Hospital_Bills_Summary.pdf", "type": "Emergency Hospital Invoices", "size": "3.8 MB", "status": "VERIFIED", "uploaded_at": "2026-10-12 10:35:00"}
        ],
        "eligibility_details": {
            "status": "ELIGIBLE",
            "rule": "Ex-Servicemen Category, Age 62, Income verified under ₹8,00,000 threshold",
            "assessed_by": "Zila Sainik Welfare Officer",
            "assessed_at": "2026-10-14 11:20:00"
        },
        "scholarship_sanction": {
            "amount": 180000,
            "status": "APPROVED",
            "sanction_officer": "Col. R. K. Thapa (Director, Welfare Board)",
            "approval_date": "2026-10-16 16:45:00"
        },
        "timeline": [
            {"status": "SUBMITTED", "title": "Application Submitted", "date": "2026-10-12 10:30:00", "remarks": "Online application received and registered with ID VS-2026-1001.", "completed": True},
            {"status": "DOC_VERIFIED", "title": "Documents Verified", "date": "2026-10-13 14:15:00", "remarks": "ECHS card and discharge book validated by Zila Sainik Board.", "completed": True},
            {"status": "ELIGIBILITY_CHECK", "title": "Eligibility Assessed", "date": "2026-10-14 11:20:00", "remarks": "DBMS CheckEligibility verified age and service category criteria.", "completed": True},
            {"status": "APPROVED", "title": "Sanctioning Officer Approval", "date": "2026-10-16 16:45:00", "remarks": "Grant approved for ₹1,80,000 by Welfare Officer. Disbursal scheduled.", "completed": True},
            {"status": "DISBURSED", "title": "Grant Disbursed", "date": "Pending", "remarks": "Direct bank transfer will be credited within 3 working days.", "completed": False}
        ]
    },
    {
        "application_id": 1002,
        "applicant_name": "Sunita Devi (Veer Nari)",
        "applicant_email": "sunita.devi@example.com",
        "service_no": "VN-12048",
        "service_category": "DEFENCE WIDOW",
        "scheme_id": 3,
        "scheme_name": "Defence Widow Welfare Assistance",
        "current_status": "DOC_VERIFIED",
        "submission_date": "2026-10-15 09:15:00",
        "documents": [
            {"id": "doc_1002_1", "name": "Special_Family_Pension_Cert.pdf", "type": "Family Pension Order (PPO)", "size": "1.8 MB", "status": "VERIFIED", "uploaded_at": "2026-10-15 09:20:00"},
            {"id": "doc_1002_2", "name": "Military_Discharge_Cert.pdf", "type": "Martyr Service Record", "size": "2.1 MB", "status": "VERIFIED", "uploaded_at": "2026-10-15 09:22:00"},
            {"id": "doc_1002_3", "name": "Bank_Passbook_Aadhaar.pdf", "type": "DBT Bank Mandate", "size": "850 KB", "status": "VERIFIED", "uploaded_at": "2026-10-15 09:25:00"}
        ],
        "eligibility_details": {
            "status": "PENDING",
            "rule": "Defence Widow Assistance, Income <= ₹6,00,000 ceiling under review",
            "assessed_by": None,
            "assessed_at": None
        },
        "scholarship_sanction": {
            "amount": 100000,
            "status": "PENDING",
            "sanction_officer": "Director, Veer Nari Cell",
            "approval_date": None
        },
        "timeline": [
            {"status": "SUBMITTED", "title": "Application Submitted", "date": "2026-10-15 09:15:00", "remarks": "Application logged and priority token assigned.", "completed": True},
            {"status": "DOC_VERIFIED", "title": "Documents Verified", "date": "2026-10-17 11:30:00", "remarks": "Family pension certificate and identity proof verified by Welfare Officer.", "completed": True},
            {"status": "ELIGIBILITY_CHECK", "title": "Eligibility Assessment", "date": "In Progress", "remarks": "Automated criteria matching under review.", "completed": False},
            {"status": "APPROVED", "title": "Welfare Officer Approval", "date": "Pending", "remarks": "Awaiting final clearance.", "completed": False},
            {"status": "DISBURSED", "title": "Disbursal", "date": "Pending", "remarks": "Fund release through DBT.", "completed": False}
        ]
    },
    {
        "application_id": 1003,
        "applicant_name": "Ananya Singh (Dependent)",
        "applicant_email": "ananya.singh@example.com",
        "service_no": "DEP-78291",
        "service_category": "DEFENCE FAMILY",
        "scheme_id": 1,
        "scheme_name": "Defence Family Education Assistance (Scholarship)",
        "current_status": "SUBMITTED",
        "submission_date": "2026-10-18 18:00:00",
        "documents": [
            {"id": "doc_1003_1", "name": "Father_Service_ID_Book.pdf", "type": "Parent Service Record (Army)", "size": "1.6 MB", "status": "PENDING", "uploaded_at": "2026-10-18 18:05:00"},
            {"id": "doc_1003_2", "name": "College_Student_ID.pdf", "type": "Bonafide College Identity", "size": "950 KB", "status": "PENDING", "uploaded_at": "2026-10-18 18:06:00"},
            {"id": "doc_1003_3", "name": "Semester_IV_Marksheet.pdf", "type": "Latest Academic Marksheet (8.9 CGPA)", "size": "1.4 MB", "status": "PENDING", "uploaded_at": "2026-10-18 18:08:00"},
            {"id": "doc_1003_4", "name": "Income_Certificate_Tehsildar.pdf", "type": "Family Income Certificate (₹4.2L)", "size": "720 KB", "status": "PENDING", "uploaded_at": "2026-10-18 18:10:00"}
        ],
        "eligibility_details": {
            "status": "PENDING",
            "rule": "Age 21 <= 25, Income ₹4.2L <= ₹5L ceiling, Category: DEFENCE FAMILY",
            "assessed_by": None,
            "assessed_at": None
        },
        "scholarship_sanction": {
            "amount": 50000,
            "status": "PENDING",
            "sanction_officer": "Army Welfare Education Society (AWES)",
            "approval_date": None
        },
        "timeline": [
            {"status": "SUBMITTED", "title": "Application Submitted", "date": "2026-10-18 18:00:00", "remarks": "Academic scholarship application submitted with marksheets.", "completed": True},
            {"status": "DOC_VERIFIED", "title": "Document Verification", "date": "Pending", "remarks": "Awaiting Zila Sainik Welfare Office digital verification.", "completed": False},
            {"status": "ELIGIBILITY_CHECK", "title": "Eligibility Assessment", "date": "Pending", "remarks": "Automated CheckEligibility rules evaluation.", "completed": False},
            {"status": "APPROVED", "title": "Sanctioning Approval", "date": "Pending", "remarks": "Awaiting Scholarship Committee sign-off.", "completed": False},
            {"status": "DISBURSED", "title": "Scholarship Release", "date": "Pending", "remarks": "Annual direct transfer via DBT.", "completed": False}
        ]
    },
    {
        "application_id": 1004,
        "applicant_name": "Rohit Verma (Dependent Ward)",
        "applicant_email": "rohit.verma@example.com",
        "service_no": "DEP-99412",
        "service_category": "DEFENCE FAMILY",
        "scheme_id": 1,
        "scheme_name": "Defence Family Education Assistance (Scholarship)",
        "current_status": "ELIGIBILITY_CHECK",
        "submission_date": "2026-10-19 14:00:00",
        "documents": [
            {"id": "doc_1004_1", "name": "PPO_Copy_Havildar_Verma.pdf", "type": "Parent Discharge Certificate", "size": "2.0 MB", "status": "VERIFIED", "uploaded_at": "2026-10-19 14:05:00"},
            {"id": "doc_1004_2", "name": "BTech_College_Bonafide.pdf", "type": "College Bonafide Certificate", "size": "1.1 MB", "status": "VERIFIED", "uploaded_at": "2026-10-19 14:07:00"},
            {"id": "doc_1004_3", "name": "Engineering_Marksheets.pdf", "type": "Merit Grade Card (84%)", "size": "3.2 MB", "status": "VERIFIED", "uploaded_at": "2026-10-19 14:10:00"}
        ],
        "eligibility_details": {
            "status": "ELIGIBLE",
            "rule": "Age 20 <= 25, Income ₹3.8L <= ₹5L ceiling, Category: DEFENCE FAMILY",
            "assessed_by": "Zila Sainik Welfare Board",
            "assessed_at": "2026-10-20 10:15:00"
        },
        "scholarship_sanction": {
            "amount": 50000,
            "status": "PENDING",
            "sanction_officer": "Director of Education AWES",
            "approval_date": None
        },
        "timeline": [
            {"status": "SUBMITTED", "title": "Application Submitted", "date": "2026-10-19 14:00:00", "remarks": "Scholarship application registered.", "completed": True},
            {"status": "DOC_VERIFIED", "title": "Document Verification", "date": "2026-10-19 17:30:00", "remarks": "Academic bonafide certificate and PPO copy verified.", "completed": True},
            {"status": "ELIGIBILITY_CHECK", "title": "Eligibility Assessment", "date": "2026-10-20 10:15:00", "remarks": "Applicant verified ELIGIBLE for Prime Minister Scholarship Scheme.", "completed": True},
            {"status": "APPROVED", "title": "Scholarship Approval", "date": "Pending", "remarks": "Awaiting Sanctioning Officer digital sign-off.", "completed": False},
            {"status": "DISBURSED", "title": "Scholarship Release", "date": "Pending", "remarks": "Annual DBT direct transfer.", "completed": False}
        ]
    },
    {
        "application_id": 1005,
        "applicant_name": "Subedar Manjeet Singh (Retd)",
        "applicant_email": "manjeet.singh@example.com",
        "service_no": "JC-88219K",
        "service_category": "DISABLED VETERAN",
        "scheme_id": 5,
        "scheme_name": "War Disability Rehabilitation Grant",
        "current_status": "SUBMITTED",
        "submission_date": "2026-10-20 11:30:00",
        "documents": [
            {"id": "doc_1005_1", "name": "Disability_Pension_Order.pdf", "type": "Medical Board Assessment Report", "size": "2.8 MB", "status": "PENDING", "uploaded_at": "2026-10-20 11:35:00"},
            {"id": "doc_1005_2", "name": "Discharge_Book_JC88219K.pdf", "type": "Army Service Book", "size": "4.1 MB", "status": "PENDING", "uploaded_at": "2026-10-20 11:37:00"},
            {"id": "doc_1005_3", "name": "Assistive_Equipment_Invoice.pdf", "type": "Motorized Wheelchair Quotation", "size": "1.3 MB", "status": "PENDING", "uploaded_at": "2026-10-20 11:40:00"}
        ],
        "eligibility_details": {
            "status": "PENDING",
            "rule": "War Disability Category, Medical Board clearance required",
            "assessed_by": None,
            "assessed_at": None
        },
        "scholarship_sanction": {
            "amount": 150000,
            "status": "PENDING",
            "sanction_officer": "Military Rehabilitation Authority",
            "approval_date": None
        },
        "timeline": [
            {"status": "SUBMITTED", "title": "Application Submitted", "date": "2026-10-20 11:30:00", "remarks": "Disability equipment grant application logged.", "completed": True},
            {"status": "DOC_VERIFIED", "title": "Document Verification", "date": "Pending", "remarks": "Awaiting verification of medical board assessment report.", "completed": False},
            {"status": "ELIGIBILITY_CHECK", "title": "Eligibility Assessment", "date": "Pending", "remarks": "Review of disability percentage order.", "completed": False},
            {"status": "APPROVED", "title": "Officer Approval", "date": "Pending", "remarks": "Awaiting competent authority grant sanction.", "completed": False},
            {"status": "DISBURSED", "title": "Grant Disbursal", "date": "Pending", "remarks": "Equipment subsidy DBT transfer.", "completed": False}
        ]
    },
    {
        "application_id": 1006,
        "applicant_name": "Pooja Bisht",
        "applicant_email": "pooja.bisht@example.com",
        "service_no": "ab-20",
        "service_category": "DEFENCE FAMILY",
        "scheme_id": 1,
        "scheme_name": "Defence Family Education Assistance",
        "current_status": "SUBMITTED",
        "submission_date": "2026-11-23 11:07:15",
        "documents": [
            {"id": "doc_1006_1", "name": "Discharge_Book_ab20.pdf", "type": "Parent Army Service Record", "size": "2.4 MB", "status": "PENDING", "uploaded_at": "2026-11-23 11:07:15"},
            {"id": "doc_1006_2", "name": "University_Bonafide_Card.pdf", "type": "College Bonafide Certificate", "size": "1.1 MB", "status": "PENDING", "uploaded_at": "2026-11-23 11:07:15"},
            {"id": "doc_1006_3", "name": "Semester_Marksheet_Proof.pdf", "type": "Academic Merit Marksheet", "size": "1.8 MB", "status": "PENDING", "uploaded_at": "2026-11-23 11:07:15"}
        ],
        "eligibility_details": {
            "status": "PENDING",
            "rule": "Defence Family Category, Student Age <= 25, Family Income verified",
            "assessed_by": None,
            "assessed_at": None
        },
        "scholarship_sanction": {
            "amount": 42000,
            "status": "PENDING",
            "sanction_officer": "Col. R. K. Thapa (Director, Welfare Board)",
            "approval_date": None
        },
        "timeline": [
            {"status": "SUBMITTED", "title": "Application Submitted", "date": "2026-11-23 11:07:15", "remarks": "Application registered online with reference VS-2026-1006.", "completed": True},
            {"status": "DOC_VERIFIED", "title": "Document Verification", "date": "Pending", "remarks": "Queued for Zila Sainik Welfare Officer review.", "completed": False},
            {"status": "ELIGIBILITY_CHECK", "title": "Eligibility Assessment", "date": "Pending", "remarks": "Automated rules validation queued.", "completed": False},
            {"status": "APPROVED", "title": "Sanctioning Officer Approval", "date": "Pending", "remarks": "Welfare Directorate sign-off.", "completed": False},
            {"status": "DISBURSED", "title": "Grant Disbursal", "date": "Pending", "remarks": "Direct Bank Transfer via KSB account.", "completed": False}
        ]
    }
]

# Comprehensive Welfare Schemes Data matching VeerSeva database schema
FALLBACK_SCHEMES = [
    {
        "scheme_id": 1,
        "scheme_name": "Defence Family Education Assistance",
        "description": "Comprehensive financial scholarship and educational grant for wards and dependent children of serving soldiers, ex-servicemen, and war heroes pursuing undergraduate and professional courses.",
        "category": "EDUCATION",
        "benefit": "Up to ₹50,000 per academic year plus annual textbook and hostel stipend",
        "required_documents": "Service ID / PPO Copy, Student College ID, Latest Marksheet, Bonafide Student Certificate",
        "deadline": "2027-03-31",
        "status": "ACTIVE",
        "min_age": 5,
        "max_age": 25,
        "income_limit": 500000,
        "service_category": "DEFENCE FAMILY"
    },
    {
        "scheme_id": 2,
        "scheme_name": "Ex-Servicemen Medical Support",
        "description": "Specialized health grant and financial reimbursement for chronic illness, emergency hospitalization, and specialized surgical procedures not fully covered under regular ECHS.",
        "category": "HEALTHCARE",
        "benefit": "Medical grant up to ₹2,50,000 per instance with immediate emergency disbursal",
        "required_documents": "Ex-Servicemen Identity Card, ECHS Card, Hospital Discharge Summary, Medical Expense Invoices",
        "deadline": "2027-12-31",
        "status": "ACTIVE",
        "min_age": 18,
        "max_age": 100,
        "income_limit": 800000,
        "service_category": "EX-SERVICEMEN"
    },
    {
        "scheme_id": 3,
        "scheme_name": "Defence Widow Welfare Assistance",
        "description": "Dedicated financial rehabilitation, monthly subsistence assistance, and daughter's marriage grant for Veer Naris and widows of armed forces personnel.",
        "category": "FINANCIAL",
        "benefit": "Monthly allowance of ₹15,000 plus one-time marriage assistance of ₹1,00,000",
        "required_documents": "Special Family Pension Certificate, Military Discharge Certificate, Identity & Bank Passbook",
        "deadline": "2027-06-30",
        "status": "ACTIVE",
        "min_age": 18,
        "max_age": 100,
        "income_limit": 600000,
        "service_category": "DEFENCE WIDOW"
    },
    {
        "scheme_id": 4,
        "scheme_name": "Skill Development & Resettlement Support",
        "description": "Subsidized vocational training, modern IT certifications, entrepreneurship incubation, and corporate placement assistance for transitioning veterans and adult dependents.",
        "category": "SKILL DEVELOPMENT",
        "benefit": "100% Course Fee Waiver + ₹8,000/month training stipend for 6 months",
        "required_documents": "Service Book / Discharge Certificate, Matriculation / Degree Certificate, Identity Proof",
        "deadline": "2027-09-30",
        "status": "ACTIVE",
        "min_age": 18,
        "max_age": 60,
        "income_limit": 700000,
        "service_category": "VETERAN OR FAMILY"
    },
    {
        "scheme_id": 5,
        "scheme_name": "War Disability Rehabilitation Grant",
        "description": "Specialized assistive equipment, motorized wheelchair support, home accessibility retrofitting, and recurring disability maintenance grants for war-wounded soldiers.",
        "category": "HEALTHCARE",
        "benefit": "One-time equipment grant of ₹1,50,000 + ₹10,000 monthly sustenance",
        "required_documents": "Disability Pension Order, Medical Board Assessment Report, Service Record",
        "deadline": "2027-11-30",
        "status": "ACTIVE",
        "min_age": 18,
        "max_age": 100,
        "income_limit": 900000,
        "service_category": "DISABLED VETERAN"
    },
    {
        "scheme_id": 6,
        "scheme_name": "Gallantry Awardee Housing Subsidy",
        "description": "Honorary housing construction subsidy, land allotment assistance, and interest concession on home loans for Param Vir Chakra, Maha Vir Chakra, Vir Chakra, and Sena Medal recipients.",
        "category": "HOUSING",
        "benefit": "Direct capital grant of ₹5,00,000 towards home purchase or renovation",
        "required_documents": "Presidential Award Gazette Notification, Medal Citation, Land/Property Documents",
        "deadline": "2027-08-31",
        "status": "ACTIVE",
        "min_age": 21,
        "max_age": 100,
        "income_limit": 1500000,
        "service_category": "GALLANTRY AWARDEE"
    }
]

# Audit log store
AUDIT_LOGS = [
    {"log_id": 1, "action": "INITIALIZE_SYSTEM", "table_name": "schemes", "record_id": 1, "action_time": "2026-10-18 10:00:00", "details": "VeerSeva Phase-III OSDBMS portal active"},
    {"log_id": 2, "action": "SUBMIT_APPLICATION", "table_name": "applications", "record_id": 1001, "action_time": "2026-10-18 10:30:00", "details": "New application for Ex-Servicemen Medical Support"},
    {"log_id": 3, "action": "CHECK_ELIGIBILITY", "table_name": "eligibility_rules", "record_id": 2, "action_time": "2026-10-18 11:20:00", "details": "CheckEligibility executed for user_id 1"},
    {"log_id": 4, "action": "UPDATE_STATUS", "table_name": "application_status", "record_id": 1001, "action_time": "2026-10-18 16:45:00", "details": "Status changed to APPROVED"}
]

# Home page serves frontend index.html
@app.route("/")
def home():
    return send_from_directory(
        os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend"),
        "index.html"
    )
# Frontend route
@app.route("/frontend")
def frontend():
    return send_from_directory(str(FRONTEND_DIR), "index.html")

# Static assets helper
@app.route("/<path:path>")
def serve_static(path):
    if (FRONTEND_DIR / path).is_file():
        return send_from_directory(str(FRONTEND_DIR), path)
    return send_from_directory(str(FRONTEND_DIR), "index.html")

# Project & Team Info (Phase-III Progress)
@app.route("/api/project-info", methods=["GET"])
def get_project_info():
    return jsonify({
        "project_title": "VeerSeva – Defence Welfare Management System",
        "phase": "Phase-III Project Progress",
        "institution": "Graphic Era Deemed to be University, Dehradun",
        "course_name": "OSDBMS (PCS-502 & PCS-503)",
        "team_name": "Team 210",
        "team_code": "OSDBMS/T210",
        "team_members": [
            {
                "name": "Bisht, Pooja",
                "role": "Team Lead",
                "student_id": "240221631",
                "email": "Kanchanb706@gmail.com",
                "ownership": "OS modules: process management, CPU scheduling, synchronization, deadlock & memory"
            },
            {
                "name": "Maurya, Richa",
                "role": "Team Member 2",
                "student_id": "240221320",
                "email": "Richamaurya011@gmail.com",
                "ownership": "ER diagram, normalization, SQL implementation, transactions, indexing & DBMS-OS integration"
            },
            {
                "name": "Kalkar, Sakshi",
                "role": "Team Member 3",
                "student_id": "240221444",
                "email": "Sakshi.kalkar8@gmail.com",
                "ownership": "OS simulator (FCFS, SJF, Priority, Round Robin), performance analysis & system testing"
            }
        ],
        "progress_percentage": 100,
        "references": [
            "Silberschatz, Galvin & Gagne — Operating System Concepts",
            "Silberschatz, Korth & Sudarshan — Database System Concepts",
            "MySQL Reference Manual"
        ]
    })

# Get all welfare schemes
@app.route("/api/schemes", methods=["GET"])
def get_schemes():
    connection = get_db_connection()

    if connection is not None:
        cursor = None
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("""
                SELECT
                    scheme_id,
                    scheme_name,
                    description,
                    category,
                    benefit,
                    required_documents,
                    deadline,
                    status
                FROM schemes
            """)
            schemes = cursor.fetchall()
            if schemes:
                return jsonify(schemes)
        except Exception:
            app.logger.warning("Database query error, serving fallback schemes")
        finally:
            if cursor is not None:
                cursor.close()
            if connection.is_connected():
                connection.close()

    return jsonify(FALLBACK_SCHEMES)

# Submit an application
@app.route("/api/applications", methods=["POST"])
def submit_application():
    data = request.get_json(silent=True) or {}

    applicant_name = data.get("applicant_name", "").strip()
    applicant_email = data.get("applicant_email", "").strip().lower()
    scheme_id = data.get("scheme_id")
    service_no = data.get("service_no", "AR-PENDING").strip()
    service_category = data.get("service_category", "EX-SERVICEMEN").strip()

    if not applicant_name or not applicant_email or not scheme_id:
        return jsonify({
            "error": "Applicant Name, Email, and Welfare Scheme selection are required."
        }), 400

    try:
        scheme_id = int(scheme_id)
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid scheme selected."}), 400

    connection = get_db_connection()
    if connection is not None:
        cursor = None
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(
                "SELECT scheme_id, scheme_name FROM schemes WHERE scheme_id = %s AND status = 'ACTIVE'",
                (scheme_id,)
            )
            scheme = cursor.fetchone()
            if scheme is None:
                return jsonify({"error": "Selected scheme is inactive or unavailable."}), 400

            cursor.execute("SELECT user_id FROM users WHERE email = %s", (applicant_email,))
            user = cursor.fetchone()

            if user:
                user_id = user["user_id"]
                cursor.execute(
                    "UPDATE users SET full_name = %s WHERE user_id = %s",
                    (applicant_name, user_id)
                )
            else:
                cursor.execute(
                    "INSERT INTO users (full_name, email, password, user_type) VALUES (%s, %s, %s, %s)",
                    (applicant_name, applicant_email, "default_hash", "BENEFICIARY")
                )
                user_id = cursor.lastrowid

            cursor.execute(
                "INSERT INTO applications (user_id, scheme_id, current_status) VALUES (%s, %s, %s)",
                (user_id, scheme_id, "SUBMITTED")
            )
            application_id = cursor.lastrowid

            # Trigger status history insert
            try:
                cursor.execute(
                    "INSERT INTO application_status (application_id, status, remarks) VALUES (%s, %s, %s)",
                    (application_id, "SUBMITTED", "Initial online application submitted via VeerSeva portal.")
                )
            except Exception:
                pass

            # Log audit
            try:
                cursor.execute(
                    "INSERT INTO audit_logs (user_id, action, table_name, record_id) VALUES (%s, %s, %s, %s)",
                    (user_id, "SUBMIT_APPLICATION", "applications", application_id)
                )
            except Exception:
                pass

            connection.commit()

            return jsonify({
                "message": "Application submitted successfully to MySQL Database!",
                "application_id": application_id,
                "user_id": user_id,
                "status": "SUBMITTED",
                "database_mode": "MYSQL_CONNECTED"
            }), 201

        except Exception as e:
            if connection.is_connected():
                connection.rollback()
            app.logger.exception("DB submission failed, falling back to session store")
        finally:
            if cursor is not None:
                cursor.close()
            if connection.is_connected():
                connection.close()

    # In-memory fallback
    new_app_id = 1000 + len(IN_MEMORY_APPLICATIONS) + 1
    scheme_match = next((s for s in FALLBACK_SCHEMES if s["scheme_id"] == scheme_id), None)
    scheme_name = scheme_match["scheme_name"] if scheme_match else "Defence Welfare Scheme"
    timestamp_str = time.strftime("%Y-%m-%d %H:%M:%S")

    is_education = "scholarship" in scheme_name.lower() or "education" in scheme_name.lower()
    default_amount = 42000 if is_education else (500000 if "martyr" in scheme_name.lower() or "ex-gratia" in scheme_name.lower() else 100000)

    app_record = {
        "application_id": new_app_id,
        "applicant_name": applicant_name,
        "applicant_email": applicant_email,
        "service_no": service_no,
        "service_category": service_category,
        "scheme_id": scheme_id,
        "scheme_name": scheme_name,
        "current_status": "SUBMITTED",
        "submission_date": timestamp_str,
        "documents": [
            {"id": f"doc_{new_app_id}_1", "name": f"Discharge_Book_{service_no}.pdf", "type": "Service Discharge Book", "size": "2.4 MB", "status": "PENDING", "uploaded_at": timestamp_str},
            {"id": f"doc_{new_app_id}_2", "name": f"ECHS_Card_{service_no}.pdf", "type": "ECHS Beneficiary Smart Card", "size": "1.1 MB", "status": "PENDING", "uploaded_at": timestamp_str},
            {"id": f"doc_{new_app_id}_3", "name": "Academic_Bonafide_Marksheet.pdf", "type": "Bonafide Marksheet & Income Affidavit", "size": "1.8 MB", "status": "PENDING", "uploaded_at": timestamp_str}
        ],
        "eligibility_details": {
            "status": "PENDING",
            "rule": f"{service_category} Category, Service ID {service_no}, criteria evaluation pending.",
            "assessed_by": "Awaiting Assessment",
            "assessed_at": "Pending"
        },
        "scholarship_sanction": {
            "amount": default_amount,
            "status": "PENDING",
            "sanction_officer": "Col. R. K. Thapa (Director, Welfare Board)"
        },
        "timeline": [
            {
                "status": "SUBMITTED",
                "title": "Application Submitted",
                "date": timestamp_str,
                "remarks": f"Application registered successfully. Application Reference ID: VS-2026-{new_app_id}.",
                "completed": True
            },
            {
                "status": "DOC_VERIFIED",
                "title": "Document Verification",
                "date": "Pending",
                "remarks": "Assigned to Zila Sainik Welfare Officer for digital document verification.",
                "completed": False
            },
            {
                "status": "ELIGIBILITY_CHECK",
                "title": "Eligibility Assessment",
                "date": "Pending",
                "remarks": "Automated CheckEligibility procedure queued.",
                "completed": False
            },
            {
                "status": "APPROVED",
                "title": "Sanctioning Officer Approval",
                "date": "Pending",
                "remarks": "Competent Welfare Authority sign-off.",
                "completed": False
            },
            {
                "status": "DISBURSED",
                "title": "Grant Disbursal",
                "date": "Pending",
                "remarks": "Direct Bank Transfer via KSB welfare account.",
                "completed": False
            }
        ]
    }
    IN_MEMORY_APPLICATIONS.insert(0, app_record)

    AUDIT_LOGS.append({
        "log_id": len(AUDIT_LOGS) + 1,
        "action": "SUBMIT_APPLICATION",
        "table_name": "applications",
        "record_id": new_app_id,
        "action_time": timestamp_str,
        "details": f"Application {new_app_id} created for {applicant_name}"
    })

    return jsonify({
        "message": "Application submitted successfully! Your tracking reference has been generated.",
        "application_id": new_app_id,
        "user_id": 99,
        "status": "SUBMITTED",
        "database_mode": "ACTIVE_SESSION"
    }), 201


# ==============================================================================
# ADMIN OFFICER MODULE: DOCUMENT VERIFICATION, ELIGIBILITY & SCHOLARSHIP APPROVAL
# ==============================================================================

@app.route("/api/admin/applications", methods=["GET"])
def admin_get_applications():
    category = request.args.get("category", "").strip().upper()
    status_filter = request.args.get("status", "").strip().upper()

    apps = list(IN_MEMORY_APPLICATIONS)
    if category and category != "ALL":
        apps = [a for a in apps if category in a.get("service_category", "").upper() or category in a.get("scheme_name", "").upper()]
    if status_filter and status_filter != "ALL":
        apps = [a for a in apps if a.get("current_status", "").upper() == status_filter]

    return jsonify(apps)

@app.route("/api/admin/verify-documents", methods=["POST"])
def admin_verify_documents():
    data = request.get_json(silent=True) or {}
    app_id = int(data.get("application_id", 0))
    officer_name = data.get("officer_name", "Zila Sainik Welfare Officer").strip()
    action = data.get("action", "VERIFIED").strip().upper()
    remarks = data.get("remarks", "Service ID, marksheet, and identity credentials validated against military records.").strip()
    timestamp_str = time.strftime("%Y-%m-%d %H:%M:%S")

    target_app = next((a for a in IN_MEMORY_APPLICATIONS if a["application_id"] == app_id), None)
    if not target_app:
        return jsonify({"error": f"Application #{app_id} not found."}), 404

    if action == "VERIFIED":
        target_app["current_status"] = "DOC_VERIFIED"
        for doc in target_app.get("documents", []):
            doc["status"] = "VERIFIED"
            doc["verified_by"] = officer_name
            doc["verified_at"] = timestamp_str

        for step in target_app.get("timeline", []):
            if step["status"] == "DOC_VERIFIED":
                step["completed"] = True
                step["date"] = timestamp_str
                step["remarks"] = f"{remarks} (Verified by: {officer_name})"
            elif step["status"] == "ELIGIBILITY_CHECK":
                step["date"] = "In Progress"
                step["remarks"] = "Documents verified. Queued for automated CheckEligibility rules engine."

        AUDIT_LOGS.append({
            "log_id": len(AUDIT_LOGS) + 1,
            "action": "DOCUMENTS_VERIFIED",
            "table_name": "documents",
            "record_id": app_id,
            "action_time": timestamp_str,
            "details": f"Documents for application #{app_id} verified by {officer_name}"
        })

        return jsonify({
            "message": f"Documents for application VS-2026-{app_id} verified successfully!",
            "application": target_app
        })
    else:
        target_app["current_status"] = "DOC_REJECTED"
        for step in target_app.get("timeline", []):
            if step["status"] == "DOC_VERIFIED":
                step["completed"] = False
                step["date"] = timestamp_str
                step["remarks"] = f"Document discrepancy flagged: {remarks}"

        AUDIT_LOGS.append({
            "log_id": len(AUDIT_LOGS) + 1,
            "action": "DOCUMENTS_REJECTED",
            "table_name": "documents",
            "record_id": app_id,
            "action_time": timestamp_str,
            "details": f"Documents for application #{app_id} rejected by {officer_name}: {remarks}"
        })

        return jsonify({
            "message": f"Application VS-2026-{app_id} flagged for document discrepancy.",
            "application": target_app
        })

@app.route("/api/admin/assess-eligibility", methods=["POST"])
def admin_assess_eligibility():
    data = request.get_json(silent=True) or {}
    app_id = int(data.get("application_id", 0))
    officer_name = data.get("officer_name", "Welfare Assessment Board").strip()
    is_eligible = bool(data.get("is_eligible", True))
    remarks = data.get("remarks", "Applicant satisfies age, income ceiling, and defence service category criteria.").strip()
    timestamp_str = time.strftime("%Y-%m-%d %H:%M:%S")

    target_app = next((a for a in IN_MEMORY_APPLICATIONS if a["application_id"] == app_id), None)
    if not target_app:
        return jsonify({"error": f"Application #{app_id} not found."}), 404

    target_app["current_status"] = "ELIGIBILITY_CHECK" if is_eligible else "NOT_ELIGIBLE"
    if "eligibility_details" not in target_app:
        target_app["eligibility_details"] = {}
    target_app["eligibility_details"]["status"] = "ELIGIBLE" if is_eligible else "INELIGIBLE"
    target_app["eligibility_details"]["assessed_by"] = officer_name
    target_app["eligibility_details"]["assessed_at"] = timestamp_str
    target_app["eligibility_details"]["remarks"] = remarks

    for step in target_app.get("timeline", []):
        if step["status"] == "ELIGIBILITY_CHECK":
            step["completed"] = is_eligible
            step["date"] = timestamp_str
            step["remarks"] = f"{remarks} (Assessed by: {officer_name})"
        elif step["status"] == "APPROVED" and is_eligible:
            step["date"] = "Queued for Sanction"
            step["remarks"] = "Eligible. Awaiting Sanctioning Officer scholarship / grant approval sign-off."

    AUDIT_LOGS.append({
        "log_id": len(AUDIT_LOGS) + 1,
        "action": "ELIGIBILITY_ASSESSED",
        "table_name": "eligibility_rules",
        "record_id": app_id,
        "action_time": timestamp_str,
        "details": f"CheckEligibility completed for app #{app_id}: {'ELIGIBLE' if is_eligible else 'INELIGIBLE'} by {officer_name}"
    })

    return jsonify({
        "message": f"Eligibility for application VS-2026-{app_id} evaluated: {'ELIGIBLE' if is_eligible else 'INELIGIBLE'}",
        "application": target_app
    })

@app.route("/api/admin/approve-scholarship", methods=["POST"])
def admin_approve_scholarship():
    data = request.get_json(silent=True) or {}
    app_id = int(data.get("application_id", 0))
    officer_name = data.get("officer_name", "Col. R. K. Thapa (Director, Welfare Board)").strip()
    decision = data.get("decision", "APPROVED").strip().upper()
    sanction_amount = int(data.get("sanction_amount", 50000))
    remarks = data.get("remarks", f"Grant of ₹{sanction_amount:,} sanctioned by Competent Welfare Authority.").strip()
    timestamp_str = time.strftime("%Y-%m-%d %H:%M:%S")

    target_app = next((a for a in IN_MEMORY_APPLICATIONS if a["application_id"] == app_id), None)
    if not target_app:
        return jsonify({"error": f"Application #{app_id} not found."}), 404

    target_app["current_status"] = decision
    if "scholarship_sanction" not in target_app:
        target_app["scholarship_sanction"] = {}
    target_app["scholarship_sanction"]["amount"] = sanction_amount
    target_app["scholarship_sanction"]["sanction_officer"] = officer_name
    target_app["scholarship_sanction"]["approval_date"] = timestamp_str
    target_app["scholarship_sanction"]["status"] = decision

    for step in target_app.get("timeline", []):
        step["completed"] = True
        step["date"] = timestamp_str
        if step["status"] == "SUBMITTED":
            step["remarks"] = f"Application registered successfully. Application Reference ID: VS-2026-{app_id}."
        elif step["status"] == "DOC_VERIFIED":
            step["remarks"] = f"All service credentials, discharge books, and certificates digitally verified by {officer_name}."
        elif step["status"] == "ELIGIBILITY_CHECK":
            step["remarks"] = "Automated CheckEligibility procedure verified criteria: ELIGIBLE."
        elif step["status"] == "APPROVED":
            step["remarks"] = f"Grant sanctioned: ₹{sanction_amount:,}. Signed by {officer_name}."
        elif step["status"] == "DISBURSED":
            if decision == "DISBURSED":
                step["remarks"] = f"DBT fund release of ₹{sanction_amount:,} credited to beneficiary account."
            else:
                step["remarks"] = f"DBT transfer of ₹{sanction_amount:,} scheduled for direct bank credit."

    AUDIT_LOGS.append({
        "log_id": len(AUDIT_LOGS) + 1,
        "action": f"SCHOLARSHIP_{decision}",
        "table_name": "applications",
        "record_id": app_id,
        "action_time": timestamp_str,
        "details": f"Scholarship / Welfare grant of ₹{sanction_amount:,} {decision.lower()} by {officer_name} for app #{app_id}"
    })

    return jsonify({
        "message": f"Scholarship/Grant for application VS-2026-{app_id} updated to {decision}!",
        "application": target_app
    })

@app.route("/api/admin/quick-approve", methods=["POST"])
def admin_quick_approve():
    data = request.get_json(silent=True) or {}
    app_id = int(data.get("application_id", 0))
    officer_name = data.get("officer_name", "Col. R. K. Thapa (Director, Welfare Board)").strip()
    timestamp_str = time.strftime("%Y-%m-%d %H:%M:%S")

    target_app = next((a for a in IN_MEMORY_APPLICATIONS if a["application_id"] == app_id), None)
    if not target_app:
        return jsonify({"error": f"Application #{app_id} not found."}), 404

    scheme_name = target_app.get("scheme_name", "")
    is_education = "scholarship" in scheme_name.lower() or "education" in scheme_name.lower()
    grant_amount = int(data.get("sanction_amount", 42000 if is_education else 100000))

    # 1. Documents
    target_app["current_status"] = "APPROVED"
    for doc in target_app.get("documents", []):
        doc["status"] = "VERIFIED"
        doc["verified_by"] = officer_name
        doc["verified_at"] = timestamp_str

    # 2. Eligibility
    if "eligibility_details" not in target_app:
        target_app["eligibility_details"] = {}
    target_app["eligibility_details"]["status"] = "ELIGIBLE"
    target_app["eligibility_details"]["assessed_by"] = "Automated CheckEligibility Engine"
    target_app["eligibility_details"]["assessed_at"] = timestamp_str
    target_app["eligibility_details"]["remarks"] = "All eligibility rules verified and access granted."

    # 3. Scholarship sanction
    if "scholarship_sanction" not in target_app:
        target_app["scholarship_sanction"] = {}
    target_app["scholarship_sanction"]["amount"] = grant_amount
    target_app["scholarship_sanction"]["sanction_officer"] = officer_name
    target_app["scholarship_sanction"]["approval_date"] = timestamp_str
    target_app["scholarship_sanction"]["status"] = "APPROVED"

    # Timeline update - mark all 5 stages completed with checkmarks
    for step in target_app.get("timeline", []):
        step["completed"] = True
        step["date"] = timestamp_str
        if step["status"] == "SUBMITTED":
            step["remarks"] = f"Application registered successfully. Application Reference ID: VS-2026-{app_id}."
        elif step["status"] == "DOC_VERIFIED":
            step["remarks"] = f"Verified by Zila Sainik Welfare Officer ({officer_name})."
        elif step["status"] == "ELIGIBILITY_CHECK":
            step["remarks"] = "Automated CheckEligibility procedure verified criteria: ELIGIBLE."
        elif step["status"] == "APPROVED":
            step["remarks"] = f"Executive approval granted for ₹{grant_amount:,} by {officer_name}."
        elif step["status"] == "DISBURSED":
            step["remarks"] = f"DBT fund transfer of ₹{grant_amount:,} credited to beneficiary account."

    AUDIT_LOGS.append({
        "log_id": len(AUDIT_LOGS) + 1,
        "action": "FAST_APPROVAL_SANCTION",
        "table_name": "applications",
        "record_id": app_id,
        "action_time": timestamp_str,
        "details": f"1-Click executive approval granted for #{app_id} (₹{grant_amount:,}) by {officer_name}"
    })

    return jsonify({
        "message": f"Application VS-2026-{app_id} successfully approved & sanctioned for ₹{grant_amount:,}!",
        "application": target_app
    })

@app.route("/api/admin/stats", methods=["GET"])
def admin_get_stats():
    apps = IN_MEMORY_APPLICATIONS
    total_apps = len(apps)
    pending_docs = sum(1 for a in apps if a.get("current_status") == "SUBMITTED")
    pending_elig = sum(1 for a in apps if a.get("current_status") == "DOC_VERIFIED")
    pending_appr = sum(1 for a in apps if a.get("current_status") == "ELIGIBILITY_CHECK")
    approved = sum(1 for a in apps if a.get("current_status") in ["APPROVED", "DISBURSED"])
    total_amount = sum(a.get("scholarship_sanction", {}).get("amount", 0) for a in apps if a.get("current_status") in ["APPROVED", "DISBURSED"])

    return jsonify({
        "total_applications": total_apps,
        "pending_documents": pending_docs,
        "pending_eligibility": pending_elig,
        "pending_approval": pending_appr,
        "approved_count": approved,
        "total_sanctioned_amount": total_amount
    })

# ==============================================================================
# AUTHENTICATION MODULE (SEPARATE BENEFICIARY & ADMIN LOGIN)
# ==============================================================================

@app.route("/api/auth/beneficiary-login", methods=["POST"])
def auth_beneficiary_login():
    data = request.get_json(silent=True) or {}
    identifier = data.get("identifier", "").strip()
    password = data.get("password", "").strip()

    if not identifier:
        return jsonify({"error": "Service No or Email required."}), 400

    applicant_name = "Pooja Bisht"
    service_no = identifier or "ab-20"
    email = f"{identifier.lower()}@veteran.in" if "@" not in identifier else identifier
    app_id = 1006

    for a in IN_MEMORY_APPLICATIONS:
        if identifier.lower() in a.get("applicant_email", "").lower() or identifier.upper() == a.get("service_no", "").upper():
            applicant_name = a.get("applicant_name")
            service_no = a.get("service_no")
            email = a.get("applicant_email")
            app_id = a.get("application_id")
            break

    return jsonify({
        "message": f"Welcome back, {applicant_name}!",
        "role": "BENEFICIARY",
        "user": {
            "name": applicant_name,
            "service_no": service_no,
            "email": email,
            "application_id": f"VS-2026-{app_id}"
        },
        "token": "bearer_beneficiary_token_demo"
    })

@app.route("/api/auth/admin-login", methods=["POST"])
def auth_admin_login():
    data = request.get_json(silent=True) or {}
    officer_id = data.get("officer_id", "").strip()
    pin = data.get("pin", "").strip()

    return jsonify({
        "message": "Officer clearance authenticated successfully.",
        "role": "ADMIN",
        "officer": {
            "name": "Col. R. K. Thapa",
            "rank": "Director, Welfare Board (Sanctioning Authority)",
            "officer_id": officer_id or "OFFICER-KSB-2026",
            "permissions": ["VERIFY_DOCS", "ASSESS_ELIGIBILITY", "SANCTION_GRANT", "DBT_DISBURSE"]
        },
        "token": "bearer_admin_officer_token_demo"
    })

# Track application status
@app.route("/api/applications/track", methods=["GET"])
def track_application():
    app_id = request.args.get("id")
    email = request.args.get("email", "").strip().lower()

    if not app_id and not email:
        return jsonify({"error": "Please provide Application ID or registered Email."}), 400

    for record in IN_MEMORY_APPLICATIONS:
        if app_id and str(record["application_id"]) == str(app_id).replace("VS-2026-", ""):
            return jsonify(record)
        if email and record["applicant_email"] == email:
            return jsonify(record)

    connection = get_db_connection()
    if connection is not None:
        cursor = None
        try:
            cursor = connection.cursor(dictionary=True)
            if app_id:
                clean_id = str(app_id).replace("VS-2026-", "")
                cursor.execute("""
                    SELECT a.application_id, a.current_status, a.application_date,
                           u.full_name as applicant_name, u.email as applicant_email,
                           s.scheme_name, s.scheme_id
                    FROM applications a
                    JOIN users u ON a.user_id = u.user_id
                    JOIN schemes s ON a.scheme_id = s.scheme_id
                    WHERE a.application_id = %s
                """, (clean_id,))
            else:
                cursor.execute("""
                    SELECT a.application_id, a.current_status, a.application_date,
                           u.full_name as applicant_name, u.email as applicant_email,
                           s.scheme_name, s.scheme_id
                    FROM applications a
                    JOIN users u ON a.user_id = u.user_id
                    JOIN schemes s ON a.scheme_id = s.scheme_id
                    WHERE u.email = %s
                    ORDER BY a.application_date DESC LIMIT 1
                """, (email,))
            row = cursor.fetchone()
            if row:
                return jsonify({
                    "application_id": row["application_id"],
                    "applicant_name": row["applicant_name"],
                    "applicant_email": row["applicant_email"],
                    "scheme_id": row["scheme_id"],
                    "scheme_name": row["scheme_name"],
                    "current_status": row["current_status"],
                    "submission_date": str(row["application_date"]),
                    "timeline": [
                        {"status": "SUBMITTED", "title": "Application Submitted", "date": str(row["application_date"]), "remarks": "Logged in database.", "completed": True},
                        {"status": "DOC_VERIFIED", "title": "Document Verification", "date": "In Progress", "remarks": "Verification queued.", "completed": row["current_status"] in ["VERIFIED", "APPROVED", "DISBURSED"]},
                        {"status": "APPROVED", "title": "Sanctioning Officer Approval", "date": "Pending", "remarks": "Officer review.", "completed": row["current_status"] in ["APPROVED", "DISBURSED"]},
                        {"status": "DISBURSED", "title": "Fund Disbursal", "date": "Pending", "remarks": "Direct transfer.", "completed": row["current_status"] == "DISBURSED"}
                    ]
                })
        except Exception:
            pass
        finally:
            if cursor:
                cursor.close()
            if connection.is_connected():
                connection.close()

    return jsonify({"error": f"No application record found for reference '{app_id or email}'."}), 404

# ==============================================================================
# OS MODULE 1: CPU SCHEDULING (FCFS, SJF, SRTF, PRIORITY, ROUND ROBIN)
# ==============================================================================
@app.route("/api/os/schedule", methods=["POST"])

@app.route("/api/os/schedule", methods=["POST"])
def simulate_cpu_scheduling():
    data = request.get_json(silent=True)

    # Check request data
    if not isinstance(data, dict):
        return jsonify({"error": "Valid JSON object required"}), 400

    algo = data.get("algorithm", "fcfs")

    if not isinstance(algo, str):
        return jsonify({"error": "Algorithm must be a string"}), 400

    algo = algo.lower()

    supported = [
        "fcfs", "sjf", "srtf",
        "priority", "round_robin", "compare_all"
    ]

    if algo not in supported:
        return jsonify({
            "error": "Unsupported scheduling algorithm",
            "supported": supported
        }), 400

    processes = data.get(
        "processes",
        ["P1", "P2", "P3", "P4"]
    )
    burst = data.get("burst", [5, 3, 2, 4])
    priority = data.get("priority", [2, 1, 3, 2])
    quantum = data.get("quantum", 2)

    # Validate process names
    if not isinstance(processes, list) or not processes:
        return jsonify({"error": "Process list cannot be empty"}), 400

    if not all(
        isinstance(p, str) and p.strip()
        for p in processes
    ):
        return jsonify({"error": "Invalid process names"}), 400

    if not isinstance(burst, list):
        return jsonify({"error": "Burst must be a list"}), 400

    try:
        burst = [int(b) for b in burst]
        quantum = int(quantum)

        if not isinstance(priority, list):
            raise ValueError("Priority must be a list")

        priority = [int(p) for p in priority]

    except (ValueError, TypeError, OverflowError):
        return jsonify({
            "error": "Burst, priority and quantum must contain integers"
        }), 400

    n = len(processes)

    # Validate burst times
    if len(burst) != n:
        return jsonify({
            "error": "Process and burst lists must have equal lengths"
        }), 400

    if any(b <= 0 for b in burst):
        return jsonify({
            "error": "Burst times must be greater than zero"
        }), 400

    # Validate priority
    if algo in ["priority", "compare_all"]:
        if len(priority) != n:
            return jsonify({
                "error": "Each process must have one priority value"
            }), 400

        if any(p < 0 for p in priority):
            return jsonify({
                "error": "Priority cannot be negative"
            }), 400

    # Validate Round Robin time quantum
    if quantum <= 0:
        return jsonify({
            "error": "Time quantum must be greater than zero"
        }), 400

    if cpu_scheduling is None:
        return jsonify({
            "error": "CPU scheduling module unavailable"
        }), 500

    try:
        if algo == "fcfs":
            res = cpu_scheduling.solve_fcfs(processes, burst)

        elif algo == "sjf":
            res = cpu_scheduling.solve_sjf(processes, burst)

        elif algo == "srtf":
            res = cpu_scheduling.solve_srtf(processes, burst)

        elif algo == "priority":
            res = cpu_scheduling.solve_priority(
                processes, burst, priority
            )

        elif algo == "round_robin":
            res = cpu_scheduling.solve_round_robin(
                processes, burst, quantum
            )

        else:
            return jsonify(
                cpu_scheduling.compare_all_schedulers(
                    processes, burst, priority, quantum
                )
            )

        results_table = []

        for i in range(n):
            results_table.append({
                "process": processes[i],
                "burst": burst[i],
                "priority": priority[i] if i < len(priority) else 1,
                "waiting": res["waiting"][i],
                "turnaround": res["turnaround"][i],
                "response": res["response"][i]
            })

        return jsonify({
            "algorithm": res["algorithm"],
            "total_time": res["total_time"],
            "gantt": res["gantt"],
            "results": results_table,
            "avg_waiting": res["avg_waiting"],
            "avg_turnaround": res["avg_turnaround"],
            "avg_response": res["avg_response"]
        })

    except (ValueError, TypeError, KeyError, IndexError) as e:
        app.logger.exception("CPU scheduling calculation failed")
        return jsonify({
            "error": "Invalid scheduling calculation",
            "details": str(e)
        }), 400

    except Exception:
        app.logger.exception("Unexpected CPU scheduling error")
        return jsonify({
            "error": "Internal scheduling error"
        }), 500

# ==============================================================================
# OS MODULE 2: DEADLOCK MANAGEMENT & BANKER'S ALGORITHM
# ==============================================================================
@app.route("/api/os/bankers", methods=["POST"])
def simulate_bankers():
    data = request.get_json(silent=True) or {}
    action = data.get("action", "safety")
    available = data.get("available", [3, 3, 2])
    allocation = data.get("allocation", [
        [0, 1, 0],
        [2, 0, 0],
        [3, 0, 2],
        [2, 1, 1],
        [0, 0, 2]
    ])
    max_demand = data.get("max", [
        [7, 5, 3],
        [3, 2, 2],
        [9, 0, 2],
        [2, 2, 2],
        [4, 3, 3]
    ])
    process_names = data.get("processes", [
        "P0 (Emergency Medical)",
        "P1 (Veer Nari Subsistence)",
        "P2 (Education Scholarship)",
        "P3 (Housing Grant)",
        "P4 (Disability Support)"
    ])

    if bankers_algorithm is None:
        return jsonify({"error": "Banker's algorithm module not loaded"}), 500

    try:
        if action == "request":
            proc_idx = int(data.get("process_idx", 0))
            req_vector = [int(r) for r in data.get("request", [1, 0, 2])]
            req_res = bankers_algorithm.request_resources(
                available, allocation, max_demand, proc_idx, req_vector, process_names
            )
            return jsonify(req_res)
        else:
            safety_result = bankers_algorithm.is_safe_state(available, allocation, max_demand, process_names)
            return jsonify(safety_result)
    except Exception as e:
        return jsonify({"error": f"Banker's algorithm execution failed: {str(e)}"}), 400

# ==============================================================================
# OS MODULE 3: VIRTUAL MEMORY & PAGE REPLACEMENT (FIFO, LRU, OPTIMAL, LFU)
# ==============================================================================
@app.route("/api/os/page-replacement", methods=["POST"])
def simulate_page_replacement():
    data = request.get_json(silent=True) or {}
    algo = data.get("algorithm", "fifo").lower()
    pages = data.get("pages", [7, 0, 1, 2, 0, 3, 0, 4, 2, 3, 0, 3, 2, 1, 2, 0, 1, 7, 0, 1])
    frames = data.get("frames", 3)

    try:
        pages = [int(p) for p in pages]
        frames = max(1, min(10, int(frames)))
    except (ValueError, TypeError):
        return jsonify({"error": "Pages must be a list of integers and frames must be an integer"}), 400

    if not pages:
        return jsonify({"error": "Page reference sequence cannot be empty"}), 400

    if page_replacement is None:
        return jsonify({"error": "Page replacement module not loaded"}), 500

    if algo == "fifo":
        res = page_replacement.fifo(pages, frames)
    elif algo == "lru":
        res = page_replacement.lru(pages, frames)
    elif algo == "optimal":
        res = page_replacement.optimal(pages, frames)
    elif algo == "lfu":
        res = page_replacement.lfu(pages, frames)
    elif algo == "compare_all":
        res = page_replacement.compare_page_algorithms(pages, frames)
    else:
        return jsonify({"error": f"Unknown algorithm '{algo}'. Supported: fifo, lru, optimal, lfu, compare_all"}), 400

    return jsonify(res)

@app.route("/api/os/belady-anomaly", methods=["GET"])
def check_belady_anomaly():
    if page_replacement is None:
        return jsonify({"error": "Page replacement module not loaded"}), 500
    return jsonify(page_replacement.evaluate_beladys_anomaly())

# ==============================================================================
# OS MODULE 4: DISK I/O SCHEDULING (FCFS, SSTF, SCAN, C-SCAN, LOOK, C-LOOK)
# ==============================================================================
@app.route("/api/os/disk-schedule", methods=["POST"])
def simulate_disk_scheduling():
    data = request.get_json(silent=True) or {}
    algo = data.get("algorithm", "sstf").lower()
    requests_list = data.get("requests", [98, 183, 37, 122, 14, 124, 65, 67])
    initial_head = data.get("initial_head", 53)
    disk_size = data.get("disk_size", 200)

    try:
        requests_list = [int(r) for r in requests_list]
        initial_head = int(initial_head)
        disk_size = int(disk_size)
    except (ValueError, TypeError):
        return jsonify({"error": "Requests, initial head, and disk size must be numeric"}), 400

    if not requests_list:
        return jsonify({"error": "Disk requests list cannot be empty"}), 400

    if disk_scheduling is None:
        return jsonify({"error": "Disk scheduling module not loaded"}), 500

    if algo == "fcfs":
        res = disk_scheduling.disk_fcfs(requests_list, initial_head)
    elif algo == "sstf":
        res = disk_scheduling.disk_sstf(requests_list, initial_head)
    elif algo == "scan":
        res = disk_scheduling.disk_scan(requests_list, initial_head, disk_size)
    elif algo == "cscan":
        res = disk_scheduling.disk_cscan(requests_list, initial_head, disk_size)
    elif algo == "look":
        res = disk_scheduling.disk_look(requests_list, initial_head)
    elif algo == "clook":
        res = disk_scheduling.disk_clook(requests_list, initial_head)
    elif algo == "compare_all":
        res = disk_scheduling.compare_disk_algorithms(requests_list, initial_head, disk_size)
    else:
        return jsonify({"error": f"Unknown algorithm '{algo}'. Supported: fcfs, sstf, scan, cscan, look, clook, compare_all"}), 400

    return jsonify(res)

# ==============================================================================
# OS MODULE 5: PROCESS SYNCHRONIZATION (BOUNDED BUFFER & READERS-WRITERS)
# ==============================================================================
@app.route("/api/os/sync", methods=["GET", "POST"])
def simulate_synchronization():
    if process_sync is None:
        return jsonify({"error": "Process synchronization module not loaded"}), 500

    if request.method == "GET":
        return jsonify({
            "bounded_buffer": process_sync.bounded_buffer.get_state(),
            "readers_writers": process_sync.readers_writers.get_state()
        })

    data = request.get_json(silent=True) or {}
    action = data.get("action", "")

    # Bounded Buffer actions
    if action == "produce":
        name = data.get("name", "New Welfare Application")
        res = process_sync.bounded_buffer.produce(name)
        return jsonify(res)
    elif action == "consume":
        res = process_sync.bounded_buffer.consume()
        return jsonify(res)
    elif action == "reset_buffer":
        res = process_sync.bounded_buffer.reset()
        return jsonify({"message": "Buffer reset to initial state", "state": res})

    # Readers-Writers actions
    elif action == "reader_start":
        reader_id = data.get("reader_id", f"Reader-{int(time.time()) % 1000}")
        res = process_sync.readers_writers.start_read(reader_id)
        return jsonify(res)
    elif action == "reader_end":
        reader_id = data.get("reader_id")
        res = process_sync.readers_writers.end_read(reader_id)
        return jsonify(res)
    elif action == "writer_start":
        writer_id = data.get("writer_id", f"AdminWriter-{int(time.time()) % 1000}")
        res = process_sync.readers_writers.start_write(writer_id)
        return jsonify(res)
    elif action == "writer_end":
        res = process_sync.readers_writers.end_write()
        return jsonify(res)

    return jsonify({"error": f"Invalid sync action '{action}'"}), 400

# ==============================================================================
# OS MODULE 6: CONTIGUOUS MEMORY ALLOCATION (FIRST-FIT, BEST-FIT, WORST-FIT)
# ==============================================================================
@app.route("/api/os/memory-allocation", methods=["POST"])
def simulate_memory_allocation():
    if memory_management is None:
        return jsonify({"error": "Memory management module not loaded"}), 500

    data = request.get_json(silent=True) or {}
    algo = data.get("algorithm", "compare_all").lower()
    blocks = data.get("blocks", [100, 500, 200, 300, 600])
    processes = data.get("processes", [212, 417, 112, 426])
    block_labels = data.get("block_labels", ["Block 1 (100KB)", "Block 2 (500KB)", "Block 3 (200KB)", "Block 4 (300KB)", "Block 5 (600KB)"])
    proc_labels = data.get("process_labels", ["P1 (Biometric OCR 212KB)", "P2 (PPO Archive 417KB)", "P3 (Rules Query 112KB)", "P4 (DBT Audit 426KB)"])

    try:
        blocks = [int(b) for b in blocks]
        processes = [int(p) for p in processes]
    except (ValueError, TypeError):
        return jsonify({"error": "Blocks and processes must be lists of integers"}), 400

    if algo == "first_fit":
        res = memory_management.allocate_first_fit(blocks, processes, block_labels, proc_labels)
    elif algo == "best_fit":
        res = memory_management.allocate_best_fit(blocks, processes, block_labels, proc_labels)
    elif algo == "worst_fit":
        res = memory_management.allocate_worst_fit(blocks, processes, block_labels, proc_labels)
    elif algo == "compare_all":
        res = memory_management.compare_memory_algorithms(blocks, processes, block_labels, proc_labels)
    else:
        return jsonify({"error": f"Unknown algorithm '{algo}'. Supported: first_fit, best_fit, worst_fit, compare_all"}), 400

    return jsonify(res)

# ==============================================================================
# OS MODULE 7: PROCESS LIFECYCLE & PROCESS CONTROL BLOCK (PCB) VIEWER
# ==============================================================================
@app.route("/api/os/process-lifecycle", methods=["GET", "POST"])
def handle_process_lifecycle():
    if process_management is None:
        return jsonify({"error": "Process management module not loaded"}), 500

    mgr = process_management.process_lifecycle_manager

    if request.method == "GET":
        return jsonify(mgr.get_system_state())

    data = request.get_json(silent=True) or {}
    action = data.get("action", "state")

    if action == "state":
        return jsonify(mgr.get_system_state())
    elif action == "admit":
        name = data.get("name", "New Welfare Background Job")
        burst = int(data.get("burst_time", 4))
        prio = int(data.get("priority", 2))
        mem = int(data.get("memory_kb", 64))
        res = mgr.admit_process(name, burst, prio, mem)
        return jsonify({"message": "Process admitted to Ready Queue", "pcb": res, "state": mgr.get_system_state()})
    elif action == "dispatch":
        pid = data.get("pid")
        res = mgr.dispatch(int(pid) if pid else None)
        return jsonify({"result": res, "state": mgr.get_system_state()})
    elif action == "trigger_io":
        pid = data.get("pid")
        res = mgr.trigger_io(int(pid) if pid else None)
        return jsonify({"result": res, "state": mgr.get_system_state()})
    elif action == "complete_io":
        pid = data.get("pid")
        res = mgr.complete_io(int(pid) if pid else None)
        return jsonify({"result": res, "state": mgr.get_system_state()})
    elif action == "terminate":
        pid = data.get("pid")
        res = mgr.terminate_process(int(pid) if pid else None)
        return jsonify({"result": res, "state": mgr.get_system_state()})
    elif action == "execute_slice":
        if mgr.running_process and mgr.running_process in mgr.processes:
            pcb = mgr.processes[mgr.running_process]
            slice_res = pcb.execute_slice(int(data.get("time_slice", 1)))
            return jsonify({"slice": slice_res, "pcb": pcb.to_dict(), "state": mgr.get_system_state()})
        return jsonify({"error": "No running process to execute CPU slice"}), 400

    return jsonify({"error": f"Unknown action '{action}'"}), 400

# ==============================================================================
# BENCHMARK ALL OS ALGORITHMS ENDPOINT
# ==============================================================================
@app.route("/api/os/benchmark-all", methods=["GET"])
def benchmark_all_os_algorithms():
    results = {}
    if cpu_scheduling:
        results["cpu"] = cpu_scheduling.compare_all_schedulers(
            ["P1 (OCR)", "P2 (Biometric)", "P3 (CheckEligibility)", "P4 (DBT)"],
            [5, 3, 2, 4],
            [2, 1, 3, 2],
            quantum=2
        )
    if disk_scheduling:
        results["disk"] = disk_scheduling.compare_disk_algorithms([98, 183, 37, 122, 14, 124, 65, 67], 53, 200)
    if page_replacement:
        results["page_replacement"] = page_replacement.compare_page_algorithms(
            [7, 0, 1, 2, 0, 3, 0, 4, 2, 3, 0, 3, 2, 1, 2, 0, 1, 7, 0, 1],
            3
        )
    if memory_management:
        results["memory_allocation"] = memory_management.compare_memory_algorithms(
            [100, 500, 200, 300, 600],
            [212, 417, 112, 426]
        )
    return jsonify(results)

# Live portal statistics
@app.route("/api/stats", methods=["GET"])
def get_stats():
    return jsonify({
        "active_schemes": len(FALLBACK_SCHEMES),
        "total_applications": 1204 + len(IN_MEMORY_APPLICATIONS),
        "disbursed_funds_cr": "452.8",
        "beneficiaries_served": "1,24,900+",
        "phase": "Phase-III Progress Completed",
        "team": "Team 210 (OSDBMS/T210)",
        "os_modules_active": [
            "1. CPU Scheduling (FCFS, SJF, SRTF, Priority, Round Robin)",
            "2. Deadlock Management & Banker's Algorithm (Safety & Request)",
            "3. Virtual Memory & Page Replacement (FIFO, LRU, Optimal, LFU, Belady's Anomaly)",
            "4. Disk I/O Scheduling (FCFS, SSTF, SCAN, C-SCAN, LOOK, C-LOOK)",
            "5. Process Synchronization (Producer-Consumer Bounded Buffer & Readers-Writers)",
            "6. Contiguous Memory Allocation (First-Fit, Best-Fit, Worst-Fit)",
            "7. Process Lifecycle & Process Control Block (PCB 5-State Machine)"
        ],
        "dbms_tables_count": 8
    })

# Audit logs endpoint
@app.route("/api/audit-logs", methods=["GET"])
def get_audit_logs():
    return jsonify(AUDIT_LOGS)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
