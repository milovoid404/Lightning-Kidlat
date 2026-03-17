from flask import Flask, jsonify, request, render_template_string, redirect, url_for
import sqlite3

app = Flask(__name__)
DB_FILE = "registry.db"

# 1. DATABASE INITIALIZATION
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            grade INTEGER NOT NULL,
            section TEXT NOT NULL
        )
    ''')
    cursor.execute("SELECT COUNT(*) FROM students")
    if cursor.fetchone()[0] == 0:
        sample_data = [('Shine', 92, 'ARDUINO'), ('Mae', 74, 'ZECHARIAH'), ('Ben', 85, 'STALLMAN')]
        cursor.executemany("INSERT INTO students (name, grade, section) VALUES (?, ?, ?)", sample_data)
    conn.commit()
    conn.close()

init_db()

# --- HTML MASTER LAYOUT ---
BASE_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>MAE_LOU_TERMINAL</title>
    <style>
        body {{ background: #020406; color: #4cc9f0; font-family: 'Courier New', monospace; padding: 20px; }}
        .container {{ max-width: 800px; margin: auto; border: 1px solid #4cc9f0; padding: 20px; box-shadow: 0 0 15px rgba(76, 201, 240, 0.2); }}
        h1 {{ border-bottom: 1px solid #4cc9f0; padding-bottom: 10px; letter-spacing: 3px; text-align:center; text-transform: uppercase; }}
        .search-box {{ margin-bottom: 20px; display: flex; gap: 10px; }}
        .student-card {{ border: 1px solid #222; padding: 15px; margin: 10px 0; background: rgba(255,255,255,0.05); border-left: 5px solid #4cc9f0; transition: 0.3s; }}
        .student-card:hover {{ background: rgba(76, 201, 240, 0.1); border-left: 5px solid #ffd700; }}
        .pass {{ color: #00ff41; text-shadow: 0 0 5px #00ff41; }} 
        .fail {{ color: #ff4d4d; text-shadow: 0 0 5px #ff4d4d; }}
        input, button {{ background: #000; color: #4cc9f0; border: 1px solid #4cc9f0; padding: 10px; font-family: inherit; }}
        button {{ cursor: pointer; font-weight: bold; text-transform: uppercase; }}
        button:hover {{ background: #4cc9f0; color: #000; box-shadow: 0 0 10px #4cc9f0; }}
        .nav-links {{ margin-bottom: 15px; font-size: 0.9rem; text-align: center; }}
        a {{ color: #ffd700; text-decoration: none; }}
        a:hover {{ text-decoration: underline; }}
        
        /* Analytics Features */
        .stat-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-top: 20px; }}
        .stat-card {{ border: 1px solid #4cc9f0; padding: 20px; text-align: center; background: rgba(0,0,0,0.5); }}
        .stat-value {{ font-size: 2.5rem; display: block; margin: 10px 0; }}
        .progress-bar-bg {{ background: #111; border: 1px solid #4cc9f0; height: 25px; width: 100%; margin: 20px 0; position: relative; }}
        .progress-bar-fill {{ background: #4cc9f0; height: 100%; transition: width 1s ease-in-out; box-shadow: 0 0 10px #4cc9f0; }}
    </style>
</head>
<body>
    <div class="container">
        {content}
    </div>
</body>
</html>
"""

# --- ROUTES ---

@app.route('/')
def home():
    search_query = request.args.get('search', '')
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    if search_query:
        cursor.execute("SELECT * FROM students WHERE name LIKE ?", ('%' + search_query + '%',))
    else:
        cursor.execute("SELECT * FROM students")
    
    rows = cursor.fetchall()
    conn.close()

    content = """
    <h1>>> SYSTEM_REGISTRY_V2</h1>
    <div class="nav-links">
        <a href="/add_form">[+] NEW_RECORD</a> | <a href="/summary">[?] ANALYTICS</a>
    </div>

    <form class="search-box" action="/" method="GET">
        <input type="text" name="search" placeholder="SEARCH_BY_NAME..." value="{{ search_val }}" style="flex-grow: 1;">
        <button type="submit">QUERY</button>
        {% if search_val %}<a href="/" style="align-self:center; margin-left: 10px;">[CLEAR]</a>{% endif %}
    </form>

    <hr style="border: 0; border-top: 1px dashed #4cc9f0; margin: 20px 0;">
    {% for s in students %}
    <div class="student-card">
        <strong>NAME: {{ s['name'] }}</strong><br>
        SECTION: {{ s['section'] }} | GRADE: {{ s['grade'] }} 
        <span class="{{ 'pass' if s['grade'] >= 75 else 'fail' }}">
            ({{ 'PASSED' if s['grade'] >= 75 else 'FAILED' }})
        </span>
        <div style="margin-top:10px; font-size:0.8rem;">
             <a href="/edit/{{ s['id'] }}" style="color:#4cc9f0; margin-right: 15px;">[EDIT_ENTRY]</a>
             <a href="/delete/{{ s['id'] }}" style="color:#ff4d4d;" onclick="return confirm('Confirm deletion?')">[DELETE_ENTRY]</a>
        </div>
    </div>
    {% else %}
    <p style="text-align:center; color: #888; padding: 20px;">NO_RECORDS_FOUND_IN_SECTOR</p>
    {% endfor %}
    """
    return render_template_string(BASE_HTML.format(content=content), students=rows, search_val=search_query)

@app.route('/summary')
def summary():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT grade FROM students")
    grades = [row[0] for row in cursor.fetchall()]
    conn.close()

    if not grades:
        content = "<h1>>> ANALYTICS_OFFLINE</h1><p style='text-align:center;'>NO DATA AVAILABLE FOR ANALYSIS.</p><br><a href='/'>[RETURN]</a>"
        return render_template_string(BASE_HTML.format(content=content))

    total = len(grades)
    avg = sum(grades) / total
    passed = len([g for g in grades if g >= 75])
    failed = total - passed
    pass_rate = (passed / total) * 100

    content = f"""
    <h1>>> SYSTEM_ANALYTICS_REPORT</h1>
    
    <div class="stat-grid">
        <div class="stat-card">
            <small>CLASS_AVERAGE</small>
            <span class="stat-value" style="color:#ffd700;">{round(avg, 2)}%</span>
        </div>
        <div class="stat-card">
            <small>TOTAL_ENTRIES</small>
            <span class="stat-value">{total}</span>
        </div>
        <div class="stat-card">
            <small>SUCCESS_COUNT</small>
            <span class="stat-value pass">{passed}</span>
        </div>
        <div class="stat-card">
            <small>FAILURE_COUNT</small>
            <span class="stat-value fail">{failed}</span>
        </div>
    </div>

    <div style="margin-top: 30px;">
        <small>SYSTEM_SUCCESS_RATE: {round(pass_rate, 1)}%</small>
        <div class="progress-bar-bg">
            <div class="progress-bar-fill" style="width: {pass_rate}%;"></div>
        </div>
    </div>

    <div style="text-align:center; margin-top: 30px;">
        <a href="/" style="font-size: 1.2rem; border: 1px solid #ffd700; padding: 10px 20px;">[<] RETURN_TO_TERMINAL</a>
    </div>
    """
    return render_template_string(BASE_HTML.format(content=content))

# --- OTHER ROUTES (ADD/EDIT/DELETE) ---

@app.route('/add_form')
def add_form():
    content = """
    <h1>>> INITIALIZE_NEW_DATA</h1>
    <form action="/add" method="POST">
        NAME: <input type="text" name="name" required style="width:100%;"><br><br>
        GRADE: <input type="number" name="grade" min="0" max="100" required style="width:100%;"><br><br>
        SECTION: <input type="text" name="section" required style="width:100%;"><br><br>
        <button type="submit" style="width:100%;">COMMIT_TO_DATABASE</button>
    </form>
    <br><a href="/">[RETURN_TO_MAIN_TERMINAL]</a>
    """
    return render_template_string(BASE_HTML.format(content=content))

@app.route('/edit/<int:id>')
def edit_form(id):
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students WHERE id = ?", (id,))
    student = cursor.fetchone()
    conn.close()
    if not student: return "Record not found", 404

    content = f"""
    <h1>>> MODIFY_DATA_SECTOR_{id}</h1>
    <form action="/update" method="POST">
        <input type="hidden" name="id" value="{student['id']}">
        NAME: <input type="text" name="name" value="{student['name']}" required style="width:100%;"><br><br>
        GRADE: <input type="number" name="grade" value="{student['grade']}" min="0" max="100" required style="width:100%;"><br><br>
        SECTION: <input type="text" name="section" value="{student['section']}" required style="width:100%;"><br><br>
        <button type="submit" style="width:100%;">UPDATE_DATABASE_RECORD</button>
    </form>
    <br><a href="/">[CANCEL_CHANGES]</a>
    """
    return render_template_string(BASE_HTML.format(content=content))

@app.route('/update', methods=['POST'])
def update_student():
    sid, name, grade, section = request.form.get("id"), request.form.get("name"), int(request.form.get("grade", 0)), request.form.get("section")
    conn = sqlite3.connect(DB_FILE); cursor = conn.cursor()
    cursor.execute("UPDATE students SET name=?, grade=?, section=? WHERE id=?", (name, grade, section, sid))
    conn.commit(); conn.close()
    return redirect(url_for('home'))

@app.route('/add', methods=['POST'])
def add_student():
    name, grade, section = request.form.get("name"), int(request.form.get("grade", 0)), request.form.get("section")
    conn = sqlite3.connect(DB_FILE); cursor = conn.cursor()
    cursor.execute("INSERT INTO students (name, grade, section) VALUES (?, ?, ?)", (name, grade, section))
    conn.commit(); conn.close()
    return redirect(url_for('home'))

@app.route('/delete/<int:id>')
def delete_student(id):
    conn = sqlite3.connect(DB_FILE); cursor = conn.cursor()
    cursor.execute("DELETE FROM students WHERE id = ?", (id,))
    conn.commit(); conn.close()
    return redirect(url_for('home'))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
