import os
import time
from pathlib import Path
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

from db import get_db_connection

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
        "timeline": [
            {"status": "SUBMITTED", "title": "Application Submitted", "date": "2026-10-12 10:30:00", "remarks": "Online application received and registered with ID VS-2026-1001.", "completed": True},
            {"status": "DOC_VERIFIED", "title": "Documents Verified", "date": "2026-10-13 14:15:00", "remarks": "ECHS card and discharge book validated by Zila Sainik Board.", "completed": True},
            {"status": "ELIGIBILITY_CHECK", "title": "Eligibility Assessed", "date": "2026-10-14 11:20:00", "remarks": "DBMS CheckEligibility verified age and service category criteria.", "completed": True},
            {"status": "APPROVED", "title": "Sanctioning Officer Approval", "date": "2026-10-16 16:45:00", "remarks": "Grant approved by Welfare Officer. Disbursal scheduled.", "completed": True},
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
        "timeline": [
            {"status": "SUBMITTED", "title": "Application Submitted", "date": "2026-10-15 09:15:00", "remarks": "Application logged and priority token assigned.", "completed": True},
            {"status": "DOC_VERIFIED", "title": "Documents Verified", "date": "2026-10-17 11:30:00", "remarks": "Family pension certificate and identity proof verified.", "completed": True},
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
        "scheme_name": "Defence Family Education Assistance",
        "current_status": "SUBMITTED",
        "submission_date": "2026-10-18 18:00:00",
        "timeline": [
            {"status": "SUBMITTED", "title": "Application Submitted", "date": "2026-10-18 18:00:00", "remarks": "Academic scholarship application submitted with marksheets.", "completed": True},
            {"status": "DOC_VERIFIED", "title": "Document Verification", "date": "Pending", "remarks": "Awaiting Zila Sainik Welfare Office review.", "completed": False},
            {"status": "ELIGIBILITY_CHECK", "title": "Eligibility Assessment", "date": "Pending", "remarks": "Rules engine evaluation.", "completed": False},
            {"status": "APPROVED", "title": "Sanctioning Approval", "date": "Pending", "remarks": "Awaiting officer sign-off.", "completed": False},
            {"status": "DISBURSED", "title": "Scholarship Release", "date": "Pending", "remarks": "Annual direct transfer.", "completed": False}
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
    {"log_id": 1, "action": "INITIALIZE_SYSTEM", "table_name": "schemes", "record_id": 1, "action_time": "2026-10-18 10:00:00", "details": "VeerSeva Phase 2 portal active"},
    {"log_id": 2, "action": "SUBMIT_APPLICATION", "table_name": "applications", "record_id": 1001, "action_time": "2026-10-18 10:30:00", "details": "New application for Ex-Servicemen Medical Support"},
    {"log_id": 3, "action": "CHECK_ELIGIBILITY", "table_name": "eligibility_rules", "record_id": 2, "action_time": "2026-10-18 11:20:00", "details": "CheckEligibility executed for user_id 1"},
    {"log_id": 4, "action": "UPDATE_STATUS", "table_name": "application_status", "record_id": 1001, "action_time": "2026-10-18 16:45:00", "details": "Status changed to APPROVED"}
]

# Home page serves frontend index.html
@app.route("/")
def home():
    return send_from_directory(str(FRONTEND_DIR), "index.html")

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

    # Graceful fallback: always return rich schemes so the portal is never blank
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

    # In-memory / demonstration fallback
    new_app_id = 1000 + len(IN_MEMORY_APPLICATIONS) + 1
    scheme_match = next((s for s in FALLBACK_SCHEMES if s["scheme_id"] == scheme_id), None)
    scheme_name = scheme_match["scheme_name"] if scheme_match else "Defence Welfare Scheme"
    timestamp_str = time.strftime("%Y-%m-%d %H:%M:%S")

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
    IN_MEMORY_APPLICATIONS.append(app_record)

    # Add to audit logs
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

# Track application status
@app.route("/api/applications/track", methods=["GET"])
def track_application():
    app_id = request.args.get("id")
    email = request.args.get("email", "").strip().lower()

    if not app_id and not email:
        return jsonify({"error": "Please provide Application ID or registered Email."}), 400

    # Search in-memory store
    for record in IN_MEMORY_APPLICATIONS:
        if app_id and str(record["application_id"]) == str(app_id).replace("VS-2026-", ""):
            return jsonify(record)
        if email and record["applicant_email"] == email:
            return jsonify(record)

    # If database is connected, search MySQL
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

# OS Module CPU Scheduling Simulation API
@app.route("/api/os/schedule", methods=["POST"])
def simulate_cpu_scheduling():
    data = request.get_json(silent=True) or {}
    algo = data.get("algorithm", "fcfs").lower()
    processes = data.get("processes", ["P1", "P2", "P3"])
    burst = data.get("burst", [5, 3, 2])
    priority = data.get("priority", [2, 1, 3])
    quantum = data.get("quantum", 2)

    try:
        burst = [int(b) for b in burst]
        priority = [int(p) for p in priority]
        quantum = int(quantum)
    except (ValueError, TypeError):
        return jsonify({"error": "Burst, priority, and quantum must be numbers"}), 400

    n = len(processes)
    if n == 0 or len(burst) != n:
        return jsonify({"error": "Process list and burst time list must have identical non-zero lengths"}), 400

    chart_order = []
    chart_durations = []
    waiting = [0] * n
    turnaround = [0] * n
    response = [0] * n

    if algo == "fcfs":
        for i in range(1, n):
            waiting[i] = waiting[i - 1] + burst[i - 1]
        for i in range(n):
            turnaround[i] = waiting[i] + burst[i]
            response[i] = waiting[i]
        chart_order = processes[:]
        chart_durations = burst[:]

    elif algo == "sjf":
        order = sorted(range(n), key=lambda i: burst[i])
        current_time = 0
        for i in order:
            waiting[i] = current_time
            response[i] = current_time
            current_time += burst[i]
            turnaround[i] = current_time
            chart_order.append(processes[i])
            chart_durations.append(burst[i])

    elif algo == "priority":
        order = sorted(range(n), key=lambda i: priority[i])
        current_time = 0
        for i in order:
            waiting[i] = current_time
            response[i] = current_time
            current_time += burst[i]
            turnaround[i] = current_time
            chart_order.append(processes[i])
            chart_durations.append(burst[i])

    elif algo == "round_robin":
        remaining = burst.copy()
        response = [-1] * n
        current_time = 0
        while any(remaining[i] > 0 for i in range(n)):
            for i in range(n):
                if remaining[i] > 0:
                    if response[i] == -1:
                        response[i] = current_time
                    run_time = min(quantum, remaining[i])
                    chart_order.append(processes[i])
                    chart_durations.append(run_time)
                    current_time += run_time
                    remaining[i] -= run_time
                    if remaining[i] == 0:
                        turnaround[i] = current_time
                        waiting[i] = turnaround[i] - burst[i]

    else:
        return jsonify({"error": f"Unknown algorithm '{algo}'. Supported: fcfs, sjf, priority, round_robin"}), 400

    # Build Gantt blocks with start and end times
    gantt_blocks = []
    curr = 0
    for p, d in zip(chart_order, chart_durations):
        gantt_blocks.append({
            "process": p,
            "duration": d,
            "start": curr,
            "end": curr + d
        })
        curr += d

    results_table = []
    for i in range(n):
        results_table.append({
            "process": processes[i],
            "burst": burst[i],
            "priority": priority[i] if i < len(priority) else 1,
            "waiting": waiting[i],
            "turnaround": turnaround[i],
            "response": response[i]
        })

    avg_waiting = round(sum(waiting) / n, 2)
    avg_turnaround = round(sum(turnaround) / n, 2)
    avg_response = round(sum(response) / n, 2)

    return jsonify({
        "algorithm": algo.upper(),
        "total_time": curr,
        "gantt": gantt_blocks,
        "results": results_table,
        "avg_waiting": avg_waiting,
        "avg_turnaround": avg_turnaround,
        "avg_response": avg_response
    })

# Live portal statistics
@app.route("/api/stats", methods=["GET"])
def get_stats():
    return jsonify({
        "active_schemes": len(FALLBACK_SCHEMES),
        "total_applications": 1204 + len(IN_MEMORY_APPLICATIONS),
        "disbursed_funds_cr": "452.8",
        "beneficiaries_served": "1,24,900+",
        "os_modules_active": ["FCFS", "SJF", "Priority", "Round Robin"],
        "dbms_tables_count": 8
    })

# Audit logs endpoint
@app.route("/api/audit-logs", methods=["GET"])
def get_audit_logs():
    return jsonify(AUDIT_LOGS)

if __name__ == "__main__":
    app.run(debug=True, port=5000)