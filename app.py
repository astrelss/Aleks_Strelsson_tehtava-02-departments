from flask import Flask, render_template, request, redirect, url_for
import sqlite3, os

app = Flask(__name__)

DB_PATH = os.path.join(os.path.dirname(__file__), "users.sqlite")

def connect():
    return sqlite3.connect(DB_PATH)

def _ensure_schema():
    with connect() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS departments (
                id   INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            )
        """)
        conn.commit()

@app.get("/")
def home():
    return redirect(url_for("get_departments"))

@app.get("/departments")
def get_departments():
    _ensure_schema()
    with connect() as conn:
        rows = conn.execute("SELECT id, name FROM departments ORDER BY id").fetchall()
    return render_template("departments/index.html", departments=rows, error=None)

@app.get("/departments/new")
def new_department():
    return render_template("departments/new.html", error=None)

@app.post("/departments")
def add_department():
    name = (request.form.get("name") or "").strip()
    if not name:
        return render_template("departments/new.html", error="Name is required")
    _ensure_schema()
    with connect() as conn:
        try:
            conn.execute("INSERT INTO departments(name) VALUES (?)", (name,))
            conn.commit()
        except sqlite3.IntegrityError:
            return render_template("departments/new.html", error="Department already exists")
    return redirect(url_for("get_departments"))

@app.get("/departments/<int:department_id>/delete")
def delete_department(department_id: int):
    with connect() as conn:
        conn.execute("DELETE FROM departments WHERE id = ?", (department_id,))
        conn.commit()
    return redirect(url_for("get_departments"))

if __name__ == "__main__":
    app.run(port=4000)
