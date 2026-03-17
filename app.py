from flask import Flask, jsonify, request, render_template_string, redirect, url_for
import sqlite3

app = Flask(__name__)
DB_FILE = "registry_v3.db"

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
    <title>ML_CORE_TERMINAL</title>
    <style>
        :root {{
            --bg: #05070a;
            --panel: #0d1117;
            --accent: #4cc9f0;
            --gold: #f9c74f;
            --pass: #00f5d4;
            --fail: #f94144;
            --text: #e0e6ed;
        }}
        body {{ background: var(--bg); color: var(--text); font-family: 'Segoe UI', 'Courier New', monospace; padding: 40px 20px; margin: 0; }}
        .container {{ 
            max-width: 900px; margin: auto; border: 1px solid rgba(76, 201, 240, 0.3); 
            padding: 30px; background: var(--panel); border-radius: 12px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.5), 0 0 20px rgba(76, 201, 240, 0.1); 
        }}
        .logo-area {{ text-align: center; margin-bottom: 20px; }}
        h1 {{ 
            color: var(--accent); letter-spacing: 5px; text-align:center; 
            text-transform: uppercase; font-size: 1.5rem; margin-top: 10px;
            text-shadow: 0 0 10px rgba(76, 201, 240, 0.5);
        }}
        input, button {{ 
            background: #161b22; color: var(--text); border: 1px solid #30363d; 
            padding: 12px; border-radius: 6px; font-family: inherit; transition: 0.3s;
        }}
        input:focus {{ outline: none; border-color: var(--accent); box-shadow: 0 0 8px rgba(76, 201, 240, 0.4); }}
        button {{ 
            background: var(--accent); color: var(--bg); border: none; cursor: pointer; 
            font-weight: bold; text-transform: uppercase; letter-spacing: 1px;
        }}
        button:hover {{ filter: brightness(1.2); transform: translateY(-2px); box-shadow: 0 5px 15px rgba(76, 201, 240, 0.3); }}
        .nav-links {{ margin: 30px 0; display: flex; gap: 15px; justify-content: center; }}
        .nav-links a {{ 
            color: var(--gold); text-decoration: none; border: 1px solid var(--gold); 
            padding: 12px 20px; border-radius: 6px; font-size: 0.9rem; transition: 0.3s;
        }}
        .nav-links a:hover {{ background: var(--gold); color: var(--bg); font-weight: bold; }}
        
        .stat-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; margin-top: 25px; }}
        .stat-card {{ 
            background: rgba(255,255,255,0.03); border: 1px solid #30363d; 
            padding: 20px; text-align: center; border-radius: 8px; transition: 0.3s;
        }}
        .stat-card:hover {{ border-color: var(--accent); background: rgba(76, 201, 240, 0.05); }}
        .stat-value {{ font-size: 2rem; font-weight: 800; display: block; margin-top: 5px; }}
        .pass {{ color: var(--pass); }} .fail {{ color: var(--fail); }}
        
        table {{ width: 100%; border-collapse: separate; border-spacing: 0 8px; margin-top: 20px; }}
        th {{ padding: 15px; color: var(--accent); text-transform: uppercase; font-size: 0.75rem; letter-spacing: 1px; text-align: left; }}
        td {{ padding: 15px; background: rgba(255,255,255,0.02); border-top: 1px solid #30363d; border-bottom: 1px solid #30363d; }}
        td:first-child {{ border-left: 1px solid #30363d; border-radius: 8px 0 0 8px; }}
        td:last-child {{ border-right: 1px solid #30363d; border-radius: 0 8px 8px 0; }}
        
        .subject-tag {{ font-size: 0.65rem; color: #8b949e; text-transform: uppercase; font-weight: bold; }}
        .btn-sm {{ padding: 5px 10px; border-radius: 4px; font-size: 0.7rem; text-decoration: none; margin-left: 5px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="logo-area">
            <svg width="60" height="60" viewBox="0 0 24 24" fill="none" stroke="#4cc9f0" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <polyline points="16 18 22 12 16 6"></polyline>
                <polyline points="8 6 2 12 8 18"></polyline>
                <line x1="12" y1="2" x2="12" y2="22"></line>
            </svg>
            <h1>ML_CORE_v3</h1>
        </div>
        {content}
    </div>
    <script>
        function toggleEntries() {{
            var list = document.getElementById("entriesList");
            list.style.display = (list.style.display === "none" || list.style.display === "") ? "block" : "none";
        }}
        function filterTable() {{
            var input = document.getElementById("searchInput");
            var filter = input.value.toUpperCase();
            var tr = document.querySelectorAll("#studentTable tr:not(:first-child)");
            document.getElementById("entriesList").style.display = "block";
            tr.forEach(row => {{
                var name = row.cells[0].innerText.toUpperCase();
                row.style.display = name.includes(filter) ? "" : "none";
            }});
        }}
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    content = """
    <div style="text-align:center; padding: 40px 0;">
        <p style="color: #8b949e;">CONNECTED TO DATABASE: REGISTRY_V3.DB</p>
        <div class="nav-links">
            <a href="/add_form">INITIALIZE_ENTRY</a>
            <a href="/summary">ACCESS_ANALYTICS</a>
        </div>
    </div>
    """
    return render_template_string(BASE_HTML.format(content=content))

@app.route('/summary')
def summary():
    conn = sqlite3.connect(DB_FILE); conn.row_factory = sqlite3.Row
    rows = conn.execute("SELECT * FROM students").fetchall(); conn.close()

    if not rows:
        return render_template_string(BASE_HTML.format(content="<h3 style='text-align:center'>NO ACTIVE RECORDS</h3><div class='nav-links'><a href='/'>BACK</a></div>"))

    all_avg = []
    passed_count = 0
    table_rows = ""

    for s in rows:
        avg = (s['sub1_grade'] + s['sub2_grade'] + s['sub3_grade']) / 3
        all_avg.append(avg)
        status_class = "pass" if avg >= 75 else "fail"
        if avg >= 75: passed_count += 1
        
        table_rows += f"""
        <tr>
            <td><strong style="color:white">{s['name']}</strong><br><span style="color:#58a6ff; font-size:0.75rem">{s['section']}</span></td>
            <td><span class="subject-tag">{s['sub1_name']}</span><br>{s['sub1_grade']}</td>
            <td><span class="subject-tag">{s['sub2_name']}</span><br>{s['sub2_grade']}</td>
            <td><span class="subject-tag">{s['sub3_name']}</span><br>{s['sub3_grade']}</td>
            <td class="{status_class}"><strong>{round(avg, 2)}%</strong></td>
            <td>
                <a href="/edit/{s['id']}" class="btn-sm" style="border: 1px solid var(--gold); color: var(--gold);">EDIT</a>
                <a href="/delete/{s['id']}" class="btn-sm" style="border: 1px solid var(--fail); color: var(--fail);">DEL</a>
            </td>
        </tr>"""

    class_avg = sum(all_avg) / len(all_avg)
    
    content = f"""
    <div style="display: flex; gap: 10px; margin-bottom: 25px;">
        <input type="text" id="searchInput" placeholder="SEARCH STUDENT IDENTITY..." style="flex-grow: 1;">
        <button onclick="filterTable()">QUERY</button>
    </div>

    <div class="stat-grid">
        <div class="stat-card"><small>SYSTEM_AVG</small><span class="stat-value" style="color:var(--gold);">{round(class_avg, 2)}%</span></div>
        <div class="stat-card" style="cursor:pointer; border-color: var(--accent);" onclick="toggleEntries()"><small>RECORDS</small><span class="stat-value">{len(rows)}</span></div>
        <div class="stat-card"><small>STATUS_PASS</small><span class="stat-value pass">{passed_count}</span></div>
        <div class="stat-card"><small>STATUS_FAIL</small><span class="stat-value fail">{len(rows)-passed_count}</span></div>
    </div>

    <div id="entriesList">
        <table id="studentTable">
            <tr><th>NAME / UNIT</th><th>SUB_1</th><th>SUB_2</th><th>SUB_3</th><th>TOTAL_AVG</th><th>ACTIONS</th></tr>
            {table_rows}
        </table>
    </div>
    <div class="nav-links"><a href="/">TERMINATE_SESSION</a></div>
    """
    return render_template_string(BASE_HTML.format(content=content))

@app.route('/add_form')
def add_form():
    content = """
    <h2 style="text-align:center; color: var(--accent);">INITIALIZE_RECORD</h2>
    <form action="/add" method="POST" style="display:grid; grid-template-columns: 1fr 1fr; gap: 20px;">
        <div style="grid-column: span 2;">
            <label class="subject-tag">IDENTIFICATION NAME</label><br>
            <input type="text" name="name" required style="width:97%;">
        </div>
        <div style="grid-column: span 2;">
            <label class="subject-tag">ASSIGNED SECTION</label><br>
            <input type="text" name="section" required style="width:97%;">
        </div>
        <div>
            <label class="subject-tag">SUBJECT 01</label><br>
            <input type="text" name="s1n" placeholder="Name" required style="width:80%;">
            <input type="number" name="s1g" placeholder="Grade" min="0" max="100" required style="width:80%;">
        </div>
        <div>
            <label class="subject-tag">SUBJECT 02</label><br>
            <input type="text" name="s2n" placeholder="Name" required style="width:80%;">
            <input type="number" name="s2g" placeholder="Grade" min="0" max="100" required style="width:80%;">
        </div>
        <div style="grid-column: span 2;">
            <label class="subject-tag">SUBJECT 03</label><br>
            <input type="text" name="s3n" placeholder="Name" required style="width:39%;">
            <input type="number" name="s3g" placeholder="Grade" min="0" max="100" required style="width:39%;">
        </div>
        <button type="submit" style="grid-column: span 2; padding: 15px;">COMMIT_TO_DATABASE</button>
    </form>
    <div class="nav-links"><a href="/" style="border-color: var(--fail); color: var(--fail);">ABORT</a></div>
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
    conn = sqlite3.connect(DB_FILE); conn.row_factory = sqlite3.Row
    s = conn.execute("SELECT * FROM students WHERE id = ?", (id,)).fetchone(); conn.close()
    content = f"""
    <h2 style="text-align:center; color: var(--gold);">MODIFY_RECORD_ID_{id}</h2>
    <form action="/update" method="POST">
        <input type="hidden" name="id" value="{s['id']}">
        <label class="subject-tag">NAME</label><br>
        <input type="text" name="name" value="{s['name']}" required style="width:97%; margin-bottom:15px;">
        <div style="display:grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px;">
            <div><input type="text" name="s1n" value="{s['sub1_name']}"><input type="number" name="s1g" value="{s['sub1_grade']}"></div>
            <div><input type="text" name="s2n" value="{s['sub2_name']}"><input type="number" name="s2g" value="{s['sub2_grade']}"></div>
            <div><input type="text" name="s3n" value="{s['sub3_name']}"><input type="number" name="s3g" value="{s['sub3_grade']}"></div>
        </div>
        <button type="submit" style="width:100%; margin-top:20px;">UPDATE_CORE_DATA</button>
    </form>
    <div class="nav-links"><a href="/summary">BACK</a></div>"""
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
