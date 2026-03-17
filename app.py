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
        .pass {{ color: #00ff41; text-shadow: 0 0 5px #00ff41; }} 
        .fail {{ color: #ff4d4d; text-shadow: 0 0 5px #ff4d4d; }}
        input, button {{ background: #000; color: #4cc9f0; border: 1px solid #4cc9f0; padding: 10px; font-family: inherit; }}
        button {{ cursor: pointer; font-weight: bold; text-transform: uppercase; }}
        button:hover {{ background: #4cc9f0; color: #000; box-shadow: 0 0 10px #4cc9f0; }}
        .nav-links {{ margin: 30px 0; font-size: 1.1rem; text-align: center; display: flex; justify-content: space-around; }}
        a {{ color: #ffd700; text-decoration: none; }}
        a:hover {{ text-decoration: underline; }}
        
        .stat-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-top: 20px; }}
        .stat-card {{ border: 1px solid #4cc9f0; padding: 20px; text-align: center; background: rgba(0,0,0,0.5); }}
        .stat-card.clickable {{ cursor: pointer; transition: 0.3s; border: 2px solid #4cc9f0; }}
        .stat-card.clickable:hover {{ border-color: #ffd700; background: rgba(255, 215, 0, 0.1); box-shadow: 0 0 15px #ffd700; }}
        .stat-value {{ font-size: 2.5rem; display: block; margin: 10px 0; }}
        
        .progress-bar-bg {{ background: #111; border: 1px solid #4cc9f0; height: 25px; width: 100%; margin: 20px 0; }}
        .progress-bar-fill {{ background: #4cc9f0; height: 100%; box-shadow: 0 0 10px #4cc9f0; }}
        
        .hidden-list {{ display: none; margin-top: 20px; border-top: 1px dashed #4cc9f0; padding-top: 20px; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 15px; }}
        th, td {{ padding: 10px; border: 1px solid #1a1a1a; text-align: left; }}
        th {{ background: rgba(76, 201, 240, 0.1); }}
    </style>
</head>
<body>
    <div class="container">
        {content}
    </div>
    <script>
        function toggleEntries() {{
            var list = document.getElementById("entriesList");
            list.style.display = (list.style.display === "none" || list.style.display === "") ? "block" : "none";
            if(list.style.display === "block") list.scrollIntoView({{ behavior: 'smooth' }});
        }}

        function filterList() {{
            var input = document.getElementById("listSearch");
            var filter = input.value.toUpperCase();
            var rows = document.querySelectorAll(".student-row");
            rows.forEach(row => {{
                var text = row.innerText.toUpperCase();
                row.style.display = text.includes(filter) ? "" : "none";
            }});
        }}
    </script>
</body>
</html>
"""

# --- ROUTES ---

@app.route('/')
def home():
    content = """
    <h1>>> COMMAND_CENTER_V2</h1>
    <p style="text-align:center; color: #888;">SYSTEM STATUS: ONLINE | DATABASE: CONNECTED</p>
    
    <div class="nav-links">
        <a href="/add_form" style="border: 1px solid #ffd700; padding: 15px;">[+] INITIALIZE_NEW_RECORD</a>
        <a href="/summary" style="border: 1px solid #ffd700; padding: 15px;">[?] ACCESS_ANALYTICS</a>
    </div>

    <div style="margin-top: 50px; border: 1px solid #222; padding: 20px; background: rgba(255,255,255,0.02);">
        <h3>>> QUICK_SEARCH</h3>
        <form class="search-box" action="/summary" method="GET">
            <input type="text" name="search" placeholder="Enter student name to jump to analytics..." style="flex-grow: 1;">
            <button type="submit">QUERY</button>
        </form>
    </div>
    """
    return render_template_string(BASE_HTML.format(content=content))

@app.route('/summary')
def summary():
    search_query = request.args.get('search', '')
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students")
    all_students = cursor.fetchall()
    conn.close()

    if not all_students:
        content = "<h1>>> ANALYTICS_OFFLINE</h1><p style='text-align:center;'>NO DATA.</p><br><a href='/'>[RETURN]</a>"
        return render_template_string(BASE_HTML.format(content=content))

    grades = [s['grade'] for s in all_students]
    total = len(grades)
    avg = sum(grades) / total
    passed = len([g for g in grades if g >= 75])
    fail_count = total - passed
    pass_rate = (passed / total) * 100

    # Building the hidden table rows
    table_rows = ""
    for s in all_students:
        status_class = "pass" if s['grade'] >= 75 else "fail"
        table_rows += f"""
        <tr class="student-row">
            <td>{s['name']}</td>
            <td>{s['section']}</td>
            <td class="{status_class}">{s['grade']}</td>
            <td>
                <a href="/edit/{s['id']}" style="color:#ffd700; margin-right:10px;">[EDIT]</a>
                <a href="/delete/{s['id']}" style="color:#ff4d4d;" onclick="return confirm('Delete?')">[DEL]</a>
            </td>
        </tr>
        """

    content = f"""
    <h1>>> SYSTEM_ANALYTICS</h1>
    
    <div class="stat-grid">
        <div class="stat-card">
            <small>AVG_PERFORMANCE</small>
            <span class="stat-value" style="color:#ffd700;">{round(avg, 2)}%</span>
        </div>
        
        <div class="stat-card clickable" onclick="toggleEntries()">
            <small>TOTAL_ENTRIES (CLICK TO VIEW)</small>
            <span class="stat-value">{total}</span>
        </div>
        
        <div class="stat-card"><small>PASSED</small><span class="stat-value pass">{passed}</span></div>
        <div class="stat-card"><small>FAILED</small><span class="stat-value fail">{fail_count}</span></div>
    </div>

    <div id="entriesList" class="hidden-list" {'style="display:block;"' if search_query else ''}>
        <div style="display:flex; justify-content:between; align-items:center;">
            <h3>>> DATABASE_LOG</h3>
            <input type="text" id="listSearch" onkeyup="filterList()" placeholder="Live Filter..." 
                   value="{search_query}" style="margin-left: auto; padding: 5px;">
        </div>
        <table>
            <tr><th>NAME</th><th>SECTION</th><th>GRADE</th><th>ACTIONS</th></tr>
            {table_rows}
        </table>
    </div>

    <div style="margin-top: 30px;">
        <small>SUCCESS_RATE: {round(pass_rate, 1)}%</small>
        <div class="progress-bar-bg"><div class="progress-bar-fill" style="width: {pass_rate}%;"></div></div>
    </div>

    <div style="text-align:center;"><a href="/">[<] BACK_TO_DASHBOARD</a></div>
    """
    return render_template_string(BASE_HTML.format(content=content))

@app.route('/add_form')
def add_form():
    content = """
    <h1>>> INITIALIZE_RECORD</h1>
    <form action="/add" method="POST">
        NAME: <input type="text" name="name" required style="width:100%;"><br><br>
        GRADE: <input type="number" name="grade" min="0" max="100" required style="width:100%;"><br><br>
        SECTION: <input type="text" name="section" required style="width:100%;"><br><br>
        <button type="submit" style="width:100%;">COMMIT_DATA</button>
    </form>
    <br><a href="/">[CANCEL]</a>
    """
    return render_template_string(BASE_HTML.format(content=content))

@app.route('/edit/<int:id>')
def edit_form(id):
    conn = sqlite3.connect(DB_FILE); conn.row_factory = sqlite3.Row; cursor = conn.cursor()
    cursor.execute("SELECT * FROM students WHERE id = ?", (id,))
    student = cursor.fetchone(); conn.close()
    content = f"""
    <h1>>> MODIFY_ENTRY_{id}</h1>
    <form action="/update" method="POST">
        <input type="hidden" name="id" value="{student['id']}">
        NAME: <input type="text" name="name" value="{student['name']}" required style="width:100%;"><br><br>
        GRADE: <input type="number" name="grade" value="{student['grade']}" required style="width:100%;"><br><br>
        SECTION: <input type="text" name="section" value="{student['section']}" required style="width:100%;"><br><br>
        <button type="submit" style="width:100%;">UPDATE_ENTRY</button>
    </form>
    <br><a href="/summary">[CANCEL]</a>
    """
    return render_template_string(BASE_HTML.format(content=content))

@app.route('/update', methods=['POST'])
def update_student():
    sid, name, grade, section = request.form.get("id"), request.form.get("name"), request.form.get("grade"), request.form.get("section")
    conn = sqlite3.connect(DB_FILE); cursor = conn.cursor()
    cursor.execute("UPDATE students SET name=?, grade=?, section=? WHERE id=?", (name, grade, section, sid))
    conn.commit(); conn.close()
    return redirect(url_for('summary'))

@app.route('/add', methods=['POST'])
def add_student():
    name, grade, section = request.form.get("name"), request.form.get("grade"), request.form.get("section")
    conn = sqlite3.connect(DB_FILE); cursor = conn.cursor()
    cursor.execute("INSERT INTO students (name, grade, section) VALUES (?, ?, ?)", (name, grade, section))
    conn.commit(); conn.close()
    return redirect(url_for('summary'))

@app.route('/delete/<int:id>')
def delete_student(id):
    conn = sqlite3.connect(DB_FILE); cursor = conn.cursor()
    cursor.execute("DELETE FROM students WHERE id = ?", (id,))
    conn.commit(); conn.close()
    return redirect(url_for('summary'))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
