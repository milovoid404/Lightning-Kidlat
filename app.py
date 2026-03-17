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
    <title>Student Registry</title>
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
        body {{ background: var(--bg); color: var(--text); font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; padding: 40px 20px; margin: 0; }}
        .container {{ 
            max-width: 900px; margin: auto; border: 1px solid rgba(76, 201, 240, 0.2); 
            padding: 30px; background: var(--panel); border-radius: 12px;
        }}
        .logo-area {{ text-align: center; margin-bottom: 20px; }}
        h1 {{ color: var(--accent); text-align:center; font-size: 1.8rem; margin: 10px 0; }}
        
        input, button {{ 
            background: #161b22; color: var(--text); border: 1px solid #30363d; 
            padding: 12px; border-radius: 6px; font-family: inherit; transition: 0.3s;
        }}
        input:focus {{ outline: none; border-color: var(--accent); }}
        
        button {{ 
            background: var(--accent); color: var(--bg); border: none; cursor: pointer; 
            font-weight: bold;
        }}
        button:hover {{ filter: brightness(1.2); }}
        
        .nav-links {{ margin: 30px 0; display: flex; gap: 15px; justify-content: center; }}
        .nav-links a {{ 
            color: var(--gold); text-decoration: none; border: 1px solid var(--gold); 
            padding: 10px 20px; border-radius: 6px; transition: 0.3s;
        }}
        .nav-links a:hover {{ background: var(--gold); color: var(--bg); }}
        
        .stat-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; margin-top: 25px; }}
        .stat-card {{ 
            background: rgba(255,255,255,0.03); border: 1px solid #30363d; 
            padding: 15px; text-align: center; border-radius: 8px;
        }}
        .stat-value {{ font-size: 1.8rem; font-weight: bold; display: block; }}
        .pass {{ color: var(--pass); }} .fail {{ color: var(--fail); }}
        
        table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
        th {{ padding: 12px; color: var(--accent); text-align: left; border-bottom: 2px solid #30363d; }}
        td {{ padding: 12px; border-bottom: 1px solid #21262d; }}
        
        .label-text {{ font-size: 0.75rem; color: #8b949e; font-weight: bold; margin-bottom: 5px; display: block; }}
        .btn-sm {{ padding: 4px 8px; border-radius: 4px; font-size: 0.75rem; text-decoration: none; margin-left: 5px; border: 1px solid; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="logo-area">
            <svg width="50" height="50" viewBox="0 0 24 24" fill="none" stroke="#4cc9f0" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"></path>
            </svg>
            <h1>Student Registry</h1>
        </div>
        {content}
    </div>
    <script>
        function filterTable() {{
            var input = document.getElementById("searchInput");
            var filter = input.value.toUpperCase();
            var tr = document.querySelectorAll("#studentTable tr:not(:first-child)");
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
    <div style="text-align:center; padding: 20px 0;">
        <p style="color: #8b949e;">System Ready</p>
        <div class="nav-links">
            <a href="/add_form">Add New Student</a>
            <a href="/summary">View All Records</a>
        </div>
    </div>
    """
    return render_template_string(BASE_HTML.format(content=content))

@app.route('/summary')
def summary():
    conn = sqlite3.connect(DB_FILE); conn.row_factory = sqlite3.Row
    rows = conn.execute("SELECT * FROM students").fetchall(); conn.close()

    if not rows:
        return render_template_string(BASE_HTML.format(content="<p style='text-align:center'>No students found.</p><div class='nav-links'><a href='/'>Go Back</a></div>"))

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
            <td><strong>{s['name']}</strong><br><small style="color:#58a6ff">{s['section']}</small></td>
            <td>{s['sub1_grade']}</td>
            <td>{s['sub2_grade']}</td>
            <td>{s['sub3_grade']}</td>
            <td class="{status_class}"><strong>{round(avg, 2)}%</strong></td>
            <td>
                <a href="/edit/{s['id']}" class="btn-sm" style="color: var(--gold);">Edit</a>
                <a href="/delete/{s['id']}" class="btn-sm" style="color: var(--fail);">Delete</a>
            </td>
        </tr>"""

    class_avg = sum(all_avg) / len(all_avg)
    
    content = f"""
    <div style="display: flex; gap: 10px; margin-bottom: 20px;">
        <input type="text" id="searchInput" placeholder="Type student name..." style="flex-grow: 1;">
        <button onclick="filterTable()">Search</button>
    </div>

    <div class="stat-grid">
        <div class="stat-card"><small>Average</small><span class="stat-value" style="color:var(--gold);">{round(class_avg, 2)}%</span></div>
        <div class="stat-card"><small>Total</small><span class="stat-value">{len(rows)}</span></div>
        <div class="stat-card"><small>Passed</small><span class="stat-value pass">{passed_count}</span></div>
        <div class="stat-card"><small>Failed</small><span class="stat-value fail">{len(rows)-passed_count}</span></div>
    </div>

    <table id="studentTable">
        <tr><th>Student</th><th>Subj 1</th><th>Subj 2</th><th>Subj 3</th><th>Grade</th><th>Action</th></tr>
        {table_rows}
    </table>
    <div class="nav-links"><a href="/">Home</a></div>
    """
    return render_template_string(BASE_HTML.format(content=content))

@app.route('/add_form')
def add_form():
    content = """
    <h2 style="text-align:center;">New Student Entry</h2>
    <form action="/add" method="POST" style="display:grid; grid-template-columns: 1fr 1fr; gap: 15px;">
        <div style="grid-column: span 2;">
            <span class="label-text">Full Name</span>
            <input type="text" name="name" required style="width:96%;">
        </div>
        <div style="grid-column: span 2;">
            <span class="label-text">Section</span>
            <input type="text" name="section" required style="width:96%;">
        </div>
        <div>
            <span class="label-text">Subject 1 Name & Grade</span>
            <input type="text" name="s1n" placeholder="Name" required style="width:40%;">
            <input type="number" name="s1g" placeholder="0" min="0" max="100" required style="width:30%;">
        </div>
        <div>
            <span class="label-text">Subject 2 Name & Grade</span>
            <input type="text" name="s2n" placeholder="Name" required style="width:40%;">
            <input type="number" name="s2g" placeholder="0" min="0" max="100" required style="width:30%;">
        </div>
        <div style="grid-column: span 2;">
            <span class="label-text">Subject 3 Name & Grade</span>
            <input type="text" name="s3n" placeholder="Name" required style="width:19.5%;">
            <input type="number" name="s3g" placeholder="0" min="0" max="100" required style="width:14%;">
        </div>
        <button type="submit" style="grid-column: span 2; padding: 15px; margin-top: 10px;">Save Record</button>
    </form>
    <div class="nav-links"><a href="/" style="border-color: var(--fail); color: var(--fail);">Cancel</a></div>
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
    <h2 style="text-align:center;">Edit Record</h2>
    <form action="/update" method="POST">
        <input type="hidden" name="id" value="{s['id']}">
        <span class="label-text">Name</span>
        <input type="text" name="name" value="{s['name']}" required style="width:96%; margin-bottom:15px;">
        <div style="display:grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px;">
            <div><span class="label-text">Subj 1</span><input type="number" name="s1g" value="{s['sub1_grade']}" style="width:80%;"></div>
            <div><span class="label-text">Subj 2</span><input type="number" name="s2g" value="{s['sub2_grade']}" style="width:80%;"></div>
            <div><span class="label-text">Subj 3</span><input type="number" name="s3g" value="{s['sub3_grade']}" style="width:80%;"></div>
            <input type="hidden" name="s1n" value="{s['sub1_name']}">
            <input type="hidden" name="s2n" value="{s['sub2_name']}">
            <input type="hidden" name="s3n" value="{s['sub3_name']}">
        </div>
        <button type="submit" style="width:100%; margin-top:20px;">Save Changes</button>
    </form>
    <div class="nav-links"><a href="/summary">Cancel</a></div>"""
    return render_template_string(BASE_HTML.format(content=content))

@app.route('/update', methods=['POST'])
def update_student():
    f = request.form
    conn = sqlite3.connect(DB_FILE); cursor = conn.cursor()
    cursor.execute("""UPDATE students SET name=?, sub1_grade=?, sub2_grade=?, sub3_grade=? 
                   WHERE id=?""", (f['name'], int(f['s1g']), int(f['s2g']), int(f['s3g']), f['id']))
    conn.commit(); conn.close()
    return redirect(url_for('summary'))

@app.route('/delete/<int:id>')
def delete_student(id):
    conn = sqlite3.connect(DB_FILE); cursor = conn.cursor()
    cursor.execute("DELETE FROM students WHERE id = ?", (id,)); conn.commit(); conn.close()
    return redirect(url_for('summary'))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
