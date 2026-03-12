from flask import Flask, jsonify, request

app = Flask(__name__)

# Sample Data (In-memory database) 
students_db = [
    {"id": 1, "name": "Shine", "grade": 92, "section": "ARDUINO"},
    {"id": 2, "name": "Mae", "grade": 74, "section": "ZECHARIAH"},
    {"id": 3, "name": "Ben", "grade": 85, "section": "STALLMAN"}
]

@app.route("/")
def home():
    return "<h1>STATION_MASTER_V1.0</h1><p>Status: ONLINE</p><p>Go to /students to view registry.</p>"

# Feature 1: View All Students 
@app.route("/students")
def get_all_students():
    return jsonify({
        "system": "STELLAR_REGISTRY",
        "total_count": len(students_db),
        "records": students_db
    })

# Feature 2: Dynamic Grade Evaluation (Pass/Fail) 
@app.route("/student")
def get_student():
    # Get grade from query parameter (e.g., /student?grade=80) 
    grade_input = request.args.get('grade')
    
    if not grade_input:
        return jsonify({"error": "Please provide a ?grade= parameter"}), 400

    try:
        grade = int(grade_input)
        # Data Validation: Check if grade is between 0-100 
        if grade < 0 or grade > 100:
            return jsonify({"error": "Grade must be between 0 and 100"}), 400
            
        # Logical Remark: 75 is the passing mark 
        remarks = "PASS" if grade >= 75 else "FAIL"
        
        return jsonify({
            "name": "Shine",
            "input_grade": grade,
            "remarks": remarks,
            "status": "DATA_PROCESSED"
        })
    except ValueError:
        return jsonify({"error": "Invalid grade format. Use numbers only."}), 400

# Feature 3: Analytics Summary 
@app.route("/summary")
def summary():
    grades = [s['grade'] for s in students_db]
    passed = len([g for g in grades if g >= 75])
    failed = len(grades) - passed
    avg = sum(grades) / len(grades)
    
    return jsonify({
        "class_average": round(avg, 2),
        "total_passed": passed,
        "total_failed": failed,
        "integrity": "SECURE"
    })

if __name__ == "__main__":
    # Local testing configuration 
    app.run(host="0.0.0.0", port=5000, debug=True)
