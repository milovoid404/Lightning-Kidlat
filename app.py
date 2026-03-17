from flask import Flask, jsonify, request, render_template_string, redirect, url_for
import sqlite3

app = Flask(__name__)
DB_FILE = "registry_v3.db"

# 1. DATABASE INITIALIZATION
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            section TEXT NOT NULL,
            sub1_name TEXT, sub1_grade INTEGER,
            sub2_name TEXT, sub2_grade INTEGER,
            sub3_name TEXT, sub3_grade INTEGER
        )
    ''')
    cursor.execute("SELECT COUNT(*) FROM students")
    if cursor.fetchone()[0] == 0:
        sample_data = [
            ('Shine', 'ARDUINO', 'Math', 95, 'Science', 90, 'English', 92),
            ('Mae', 'ZECHARIAH', 'Math', 70, 'Science', 75, 'English', 72),
            ('Ben', 'STALLMAN', 'Math', 85, 'Science', 80, 'English', 88)
        ]
        cursor.executemany("""INSERT INTO students 
            (name, section, sub1_name, sub1_grade, sub2_name, sub2_grade, sub3_name, sub3_grade) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)""", sample_data)
    conn.commit()
    conn.close()

init_db()

# --- HTML MASTER LAYOUT ---
BASE_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>MAE_LOU_TERMINAL_V3</title>
    <style>
        body {{ background: #020406; color: #4cc9f0; font-family: 'Courier New', monospace; padding: 20px; }}
        .container {{ max-width: 900px; margin: auto; border: 1px solid #4cc9f0; padding: 20px; box-shadow: 0 0 15px rgba(76, 201, 240, 0.2); }}
        h1 {{ border-bottom: 1px solid #4cc9f0; padding-bottom: 10px; letter-spacing: 3px; text-align:center; text-transform: uppercase; }}
        input, button {{ background: #000; color: #4cc9f0; border: 1px solid #4cc9f0; padding: 10px; font-family: inherit; margin: 5px 0; }}
        button {{ cursor: pointer; font-weight: bold; text-transform: uppercase; }}
        button:hover {{ background: #4cc9f0; color: #000; box-shadow: 0 0 10px #4cc9f0; }}
        .nav-links {{ margin: 30px 0; text-align: center; display: flex; justify-content: space-around; }}
        a {{ color: #ffd700; text-decoration: none; border: 1px solid #ffd700; padding: 10px; }}
        a:hover {{ background: #ffd700; color: #000; }}
        .stat-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; margin-top: 20px; }}
        .stat-card {{ border: 1px solid #4cc9f0; padding: 15px; text-align: center; background: rgba(0,0,0,0.5); }}
        .stat-value {{ font-size: 1.8rem; display: block; margin: 5px 0; }}
        .pass {{ color: #00ff41; }} .fail {{ color: #ff4d4d; }}
        .hidden-list {{ display: none; margin-top: 20px; border-top: 1px dashed #4cc9f0; padding-top: 20px; }}
        table {{ width: 100%; border-collapse: collapse; font-size: 0.8rem; }}
        th, td {{ padding: 8px; border: 1px solid #1a1a1a; text-align: left; }}
        .subject-tag {{ font-size: 0.7rem; color: #888; display: block; }}
        .search-container {{ margin: 20px 0; display: flex; gap: 10px; justify-content: center; }}
    </style>
</head>
<body>
    <div class="container">{content}</div>
    <script>
        function toggleEntries() {{
            var list = document.getElementById("entriesList");
            list.style.display = (list.style.display === "none" || list.style.display === "") ? "block" : "none";
        }}
        
        function filterTable() {{
            var input = document.getElementById("searchInput");
            var filter = input.value.toUpperCase();
            var table = document.getElementById("studentTable");
            var tr = table.getElementsByTagName("tr");
            document.getElementById("entriesList").style.display = "block";

            for (var i = 1; i < tr.length; i++) {{
                var td = tr[i].getElementsByTagName("td")[0];
                if (td) {{
                    var txtValue = td.textContent || td.innerText;
                    tr[i].style.display = txtValue.toUpperCase().indexOf(filter) > -1 ? "" : "none";
                }}
            }}
        }}
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    content = """
    <h1>>> MULTI_SUBJECT_TERMINAL</h1>
    <div class="nav-links">
        <a href="/add_form">[+] NEW_STUDENT_RECORD</a>
        <a href="/summary">[?] ANALYTICS_DASHBOARD</a>
    </div>
    """
    return render_template_string(BASE_HTML.format(content=content))

@app.route('/summary')
def summary():
    search_q = request.args.get('search', '')
    conn = sqlite3.connect(DB_FILE); conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students")
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return render_template_string(BASE_HTML.format(content="<h1>NO DATA</h1><a href='/'>BACK</a>"))

    all_avg = []
    passed_count = 0
    table_rows = ""

    for s in rows:
        avg = (s['sub1_grade'] + s['sub2_grade'] + s['sub3_grade']) / 3
        all_avg.append(avg)
        status = "pass" if avg >= 75 else "fail"
        if avg >= 75: passed_count += 1
        
        table_rows += f"""
        <tr>
            <td><strong>{s['name']}</strong><br><small>{s['section']}</small></td>
            <td><span class="subject-tag">{s['sub1_name']}</span> {s['sub1_grade']}</td>
            <td><span class="subject-tag">{s['sub2_name']}</span> {s['sub2_grade']}</td>
            <td><span class="subject-tag">{s['sub3_name']}</span> {s['sub3_grade']}</td>
            <td class="{status}"><strong>{round(avg, 2)}</strong></td>
            <td>
                <a href="/edit/{s['id']}" style="border:none; color:#ffd700;">[E]</a>
                <a href="/delete/{s['id']}" style="border:none; color:#ff4d4d;">[X]</a>
            </td>
        </tr>"""

    class_avg = sum(all_avg) / len(all_avg)
    
    # Check if we should auto-show the list based on search
    list_display = "block" if search_q else "none"

    content = f"""
    <h1>>> ANALYTICS_V3</h1>
    
    <div class="search-container">
        <input type="text" id="searchInput" placeholder="SEARCH_BY_NAME..." value="{search_q}" style="flex-grow: 1;">
        <button onclick="filterTable()">QUERY_SYSTEM</button>
        <a href="/summary" style="border:1px solid #4cc9f0; padding:10px;">RESET</a>
    </div>

    <div class="stat-grid">
        <div class="stat-card"><small>CLASS_AVG</small><span class="stat-value" style="color:#ffd700;">{round(class_avg, 2)}</span></div>
        <div class="stat-card" style="cursor:pointer; border: 2px solid #ffd700;" onclick="toggleEntries()">
            <small>TOTAL_STUDENTS</small>
            <span class="stat-value">{len(rows)}</span>
            <small>(CLICK TO VIEW)</small>
        </div>
        <div class="stat-card"><small>PASSED</small><span class="stat-value pass">{passed_count}</span></div>
        <div class="stat-card"><small>FAILED</small><span class="stat-value fail">{len(rows)-passed_count}</span></div>
    </div>

    <div id="entriesList" class="hidden-list" style="display:{list_display};">
        <table id="studentTable">
            <tr><th>STUDENT</th><th>SUB_1</th><th>SUB_2</th><th>SUB_3</th><th>GEN_AVG</th><th>ACT</th></tr>
            {table_rows}
        </table>
    </div>
    <br><div style="text-align:center;"><a href="/">RETURN_TO_BASE</a></div>
    """
    return render_template_string(BASE_HTML.format(content=content))

@app.route('/add_form')
def add_form():
    content = """
    <h1>>> INITIALIZE_3_SUBJECT_DATA</h1>
    <form action="/add" method="POST" style="display:grid; grid-template-columns: 1fr 1fr; gap: 10px;">
        <div style="grid-column: span 2;">
            NAME: <input type="text" name="name" required style="width:90%;">
            SECTION: <input type="text" name="section" required style="width:90%;">
        </div>
        <div>
            SUBJ 1: <input type="text" name="s1n" placeholder="Name" required><br>
            GRADE: <input type="number" name="s1g" min="0" max="100" required>
        </div>
        <div>
            SUBJ 2: <input type="text" name="s2n" placeholder="Name" required><br>
            GRADE: <input type="number" name="s2g" min="0" max="100" required>
        </div>
        <div>
            SUBJ 3: <input type="text" name="s3n" placeholder="Name" required><br>
            GRADE: <input type="number" name="s3g" min="0" max="100" required>
        </div>
        <button type="submit" style="grid-column: span 2;">COMMIT_TO_SYSTEM</button>
    </form>
    <br><a href="/">CANCEL</a>
    """
    return render_template_string(BASE_HTML.format(content=content))

@app.route('/add', methods=['POST'])
def add_student():
    f = request.form
    conn = sqlite3.connect(DB_FILE); cursor = conn.cursor()
    cursor.execute("""INSERT INTO students (name, section, sub1_name, sub1_grade, sub2_name, sub2_grade, sub3_name, sub3_grade) 
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""", 
                   (f['name'], f['section'], f['s1n'], int(f['s1g']), f['s2n'], int(f['s2g']), f['s3n'], int(f['s3g'])))
    conn.commit(); conn.close()
    return redirect(url_for('summary'))

@app.route('/edit/<int:id>')
def edit_form(id):
    conn = sqlite3.connect(DB_FILE); conn.row_factory = sqlite3.Row; cursor = conn.cursor()
    s = cursor.execute("SELECT * FROM students WHERE id = ?", (id,)).fetchone(); conn.close()
    content = f"""
    <h1>>> MODIFY_RECORD_{id}</h1>
    <form action="/update" method="POST">
        <input type="hidden" name="id" value="{s['id']}">
        NAME: <input type="text" name="name" value="{s['name']}" required style="width:100%;"><br><br>
        <div style="display:flex; gap:10px;">
            <input type="text" name="s1n" value="{s['sub1_name']}"> <input type="number" name="s1g" value="{s['sub1_grade']}">
        </div>
        <div style="display:flex; gap:10px;">
            <input type="text" name="s2n" value="{s['sub2_name']}"> <input type="number" name="s2g" value="{s['sub2_grade']}">
        </div>
        <div style="display:flex; gap:10px;">
            <input type="text" name="s3n" value="{s['sub3_name']}"> <input type="number" name="s3g" value="{s['sub3_grade']}">
        </div>
        <br><button type="submit" style="width:100%;">UPDATE_SYSTEM</button>
    </form>
    <br><a href="/summary">CANCEL</a>"""
    return render_template_string(BASE_HTML.format(content=content))

@app.route('/update', methods=['POST'])
def update_student():
    f = request.form
    conn = sqlite3.connect(DB_FILE); cursor = conn.cursor()
    cursor.execute("""UPDATE students SET name=?, sub1_name=?, sub1_grade=?, sub2_name=?, sub2_grade=?, sub3_name=?, sub3_grade=? 
                   WHERE id=?""", (f['name'], f['s1n'], int(f['s1g']), f['s2n'], int(f['s2g']), f['s3n'], int(f['s3g']), f['id']))
    conn.commit(); conn.close()
    return redirect(url_for('summary'))

@app.route('/delete/<int:id>')
def delete_student(id):
    conn = sqlite3.connect(DB_FILE); cursor = conn.cursor()
    cursor.execute("DELETE FROM students WHERE id = ?", (id,)); conn.commit(); conn.close()
    return redirect(url_for('summary'))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
