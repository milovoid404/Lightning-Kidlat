from flask import Flask, jsonify, request, render_template_string, redirect, url_for

app = Flask(__name__)

# 1. IN-MEMORY DATASET (No external DB required for this lab) 
students = [
    {"id": 1, "name": "Shine", "grade": 92, "section": "ARDUINO"},
    {"id": 2, "name": "Mae", "grade": 74, "section": "ZECHARIAH"},
    {"id": 3, "name": "Ben", "grade": 85, "section": "STALLMAN"}
]

# --- HTML TEMPLATE (Cyber-Terminal Design) ---
BASE_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>MAE_LOU_TERMINAL</title>
    <style>
        body { background: #020406; color: #4cc9f0; font-family: 'Courier New', monospace; padding: 20px; }
        .container { max-width: 800px; margin: auto; border: 1px solid #4cc9f0; padding: 20px; box-shadow: 0 0 15px rgba(76, 201, 240, 0.2); }
        h1 { border-bottom: 1px solid #4cc9f0; padding-bottom: 10px; letter-spacing: 3px; }
        .student-card { border: 1px solid #222; padding: 10px; margin: 10px 0; background: rgba(255,255,255,0.05); }
        .pass { color: #00ff41; } .fail { color: #ff4d4d; }
        input, button { background: #000; color: #4cc9f0; border: 1px solid #4cc9f0; padding: 8px; margin: 5px 0; }
        button { cursor: pointer; font-weight: bold; }
        button:hover { background: #4cc9f0; color: #000; }
        a { color: #ffd700; text-decoration: none; font-size: 0.8rem; }
    </style>
</head>
<body>
    <div class="container">
        {% block content %}{% endblock %}
    </div>
</body>
</html>
"""

# --- ROUTES ---

# 2. HOME: LIST ALL STUDENTS (READ) 
@app.route('/')
def home():
    html = """
    {% extends "base" %}
    {% block content %}
    <h1>>> STELLAR_REGISTRY</h1>
    <a href="/add_form">[+] ADD_NEW_RECORD</a> | <a href="/summary">[?] VIEW_ANALYTICS</a>
    <hr>
    {% for s in students %}
    <div class="student-card">
        <strong>ID: {{ s.id }} | {{ s.name }}</strong><br>
        SECTION: {{ s.section }} | GRADE: {{ s.grade }} 
        <span class="{{ 'pass' if s.grade >= 75 else 'fail' }}">
            ({{ 'PASSED' if s.grade >= 75 else 'FAILED' }})
        </span>
        <br>
        <a href="/edit/{{ s.id }}">[EDIT]</a> | <a href="/delete/{{ s.id }}" style="color:red;">[DELETE]</a>
    </div>
    {% endfor %}
    {% endblock %}
    """
    return render_template_string(BASE_HTML + html, students=students)

# 3. ADD STUDENT FORM (CREATE) 
@app.route('/add_form')
def add_form():
    html = """
    {% extends "base" %}
    {% block content %}
    <h1>>> NEW_ENTRY_INITIALIZATION</h1>
    <form action="/add" method="POST">
        NAME: <input type="text" name="name" required><br>
        GRADE: <input type="number" name="grade" min="0" max="100" required><br>
        SECTION: <input type="text" name="section" required><br>
        <button type="submit">COMMIT_TO_REGISTRY</button>
    </form>
    <a href="/">[BACK_TO_TERMINAL]</a>
    {% endblock %}
    """
    return render_template_string(BASE_HTML + html)

@app.route('/add', methods=['POST'])
def add_student():
    new_id = max([s['id'] for s in students]) + 1 if students else 1
    new_student = {
        "id": new_id,
        "name": request.form.get("name"),
        "grade": int(request.form.get("grade")),
        "section": request.form.get("section")
    }
    students.append(new_student)
    return redirect(url_for('home'))

# 4. DELETE STUDENT (DELETE) 
@app.route('/delete/<int:id>')
def delete_student(id):
    global students
    students = [s for s in students if s['id'] != id]
    return redirect(url_for('home'))

# 5. ANALYTICS (JSON API FEATURE) 
@app.route('/summary')
def summary():
    if not students:
        return jsonify({"error": "NO_DATA_AVAILABLE"}), 200
    
    grades = [s['grade'] for s in students]
    avg = sum(grades) / len(grades)
    passed = len([g for g in grades if g >= 75])
    
    return jsonify({
        "class_average": round(avg, 2),
        "total_students": len(students),
        "pass_count": passed,
        "fail_count": len(students) - passed,
        "system_status": "STABLE"
    })

# 6. JSON ENDPOINT (For original requirement) 
@app.route('/api/students')
def api_students():
    return jsonify(students)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
