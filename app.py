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
# Using {content} as a placeholder for our sub-pages
BASE_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>MAE_LOU_TERMINAL</title>
    <style>
        body {{ background: #020406; color: #4cc9f0; font-family: 'Courier New', monospace; padding: 20px; }}
        .container {{ max-width: 800px; margin: auto; border: 1px solid #4cc9f0; padding: 20px; box-shadow: 0 0 15px rgba(76, 201, 240, 0.2); }}
        h1 {{ border-bottom: 1px solid #4cc9f0; padding-bottom: 10px; letter-spacing: 3px; text-align:center; }}
        .search-box {{ margin-bottom: 20px; display: flex; gap: 10px; }}
        .student-card {{ border: 1px solid #222; padding: 15px; margin: 10px 0; background: rgba(255,255,255,0.05); border-left: 5px solid #4cc9f0; }}
        .pass {{ color: #00ff41; }} .fail {{ color: #ff4d4d; }}
        input, button {{ background: #000; color: #4cc9f0; border: 1px solid #4cc9f0; padding: 10px; font-family: inherit; }}
        button {{ cursor: pointer; font-weight: bold; }}
        button:hover {{ background: #4cc9f0; color: #000; }}
        .nav-links {{ margin-bottom: 15px; font-size: 0.9rem; }}
        a {{ color: #ffd700; text-decoration: none; }}
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
        {% if search_val %}<a href="/" style="align-self:center;">[CLEAR]</a>{% endif %}
    </form>

    <hr>
    {% for s in students %}
    <div class="student-card">
        <strong>NAME: {{ s['name'] }}</strong><br>
        SECTION: {{ s['section'] }} | GRADE: {{ s['grade'] }} 
        <span class="{{ 'pass' if s['grade'] >= 75 else 'fail' }}">
            ({{ 'PASSED' if s['grade'] >= 75 else 'FAILED' }})
        </span>
        <div style="margin-top:10px; font-size:0.8rem;">
             <a href="/delete/{{ s['id'] }}" style="color:#ff4d4d;">[DELETE_ENTRY]</a>
        </div>
    </div>
    {% else %}
    <p style="text-align:center; color: #888;">NO_RECORDS_FOUND_IN_SECTOR</p>
    {% endfor %}
    """
    # Injecting sub-content into the BASE_HTML then rendering Jinja variables
    return render_template_string(BASE_HTML.format(content=content), students=rows, search_val=search_query)

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

@app.route('/add', methods=['POST'])
def add_student():
    try:
        name = request.form.get("name")
        grade = int(request.form.get("grade", 0))
        section = request.form.get("section")
        
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO students (name, grade, section) VALUES (?, ?, ?)", (name, grade, section))
        conn.commit()
        conn.close()
        return redirect(url_for('home'))
    except Exception as e:
        return f"DATABASE_ERROR: {str(e)}", 500

@app.route('/delete/<int:id>')
def delete_student(id):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM students WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('home'))

@app.route('/summary')
def summary():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT grade FROM students")
    grades = [row[0] for row in cursor.fetchall()]
    conn.close()

    if not grades:
        return jsonify({"status": "EMPTY_DATABASE"})

    avg = sum(grades) / len(grades)
    passed = len([g for g in grades if g >= 75])
    
    return jsonify({
        "average": round(avg, 2),
        "total": len(grades),
        "passed": passed,
        "failed": len(grades) - passed
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True) # Enabled debug mode to help you see errors
