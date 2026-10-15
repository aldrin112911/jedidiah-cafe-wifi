import os, sqlite3, secrets, time
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, abort

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", secrets.token_hex(32))
DB_PATH = os.environ.get("DB_PATH", "wifi_timer.db")
ADMIN_USER = os.environ.get("ADMIN_USER", "admin")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "ChangeMe123!")

def db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with db() as c:
        c.execute("""CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            minutes INTEGER NOT NULL,
            started_at REAL NOT NULL,
            ends_at REAL NOT NULL,
            status TEXT NOT NULL DEFAULT 'active'
        )""")

@app.before_request
def ensure_db():
    init_db()

def is_admin():
    return session.get("admin") is True

@app.route("/", methods=["GET"])
def home():
    return redirect(url_for("dashboard") if is_admin() else url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    error = ""
    if request.method == "POST":
        user = request.form.get("username", "")
        password = request.form.get("password", "")
        if secrets.compare_digest(user, ADMIN_USER) and secrets.compare_digest(password, ADMIN_PASSWORD):
            session["admin"] = True
            return redirect(url_for("dashboard"))
        error = "Mali ang username o password."
    return render_template("login.html", error=error)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/dashboard")
def dashboard():
    if not is_admin():
        return redirect(url_for("login"))
    with db() as c:
        rows = c.execute("SELECT * FROM customers ORDER BY id DESC").fetchall()
    return render_template("dashboard.html", customers=[dict(r) for r in rows])

@app.route("/api/customers", methods=["GET"])
def api_customers():
    if not is_admin():
        return jsonify({"error":"Unauthorized"}), 401
    with db() as c:
        rows = c.execute("SELECT * FROM customers ORDER BY id DESC").fetchall()
    now = time.time()
    result = []
    for r in rows:
        item = dict(r)
        item["remaining"] = max(0, int(item["ends_at"] - now))
        if item["status"] == "active" and item["remaining"] <= 0:
            with db() as c:
                c.execute("UPDATE customers SET status='expired' WHERE id=?", (item["id"],))
            item["status"] = "expired"
        result.append(item)
    return jsonify(result)

@app.route("/api/customers", methods=["POST"])
def add_customer():
    if not is_admin():
        return jsonify({"error":"Unauthorized"}), 401
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()
    try:
        minutes = int(data.get("minutes", 30))
    except (TypeError, ValueError):
        minutes = 30
    if not name or minutes < 1 or minutes > 1440:
        return jsonify({"error":"Maglagay ng pangalan at oras mula 1 hanggang 1440 minuto."}), 400
    now = time.time()
    with db() as c:
        c.execute("INSERT INTO customers(name, minutes, started_at, ends_at, status) VALUES(?,?,?,?, 'active')",
                  (name, minutes, now, now + minutes*60))
    return jsonify({"ok":True})

@app.route("/api/customers/<int:cid>/extend", methods=["POST"])
def extend_customer(cid):
    if not is_admin():
        return jsonify({"error":"Unauthorized"}), 401
    data = request.get_json(silent=True) or {}
    try:
        minutes = int(data.get("minutes", 15))
    except (TypeError, ValueError):
        minutes = 15
    if minutes < 1 or minutes > 1440:
        return jsonify({"error":"Invalid minutes"}), 400
    with db() as c:
        row = c.execute("SELECT * FROM customers WHERE id=?", (cid,)).fetchone()
        if not row:
            return jsonify({"error":"Customer not found"}), 404
        new_end = max(time.time(), row["ends_at"]) + minutes*60
        c.execute("UPDATE customers SET ends_at=?, status='active' WHERE id=?", (new_end, cid))
    return jsonify({"ok":True})

@app.route("/api/customers/<int:cid>/stop", methods=["POST"])
def stop_customer(cid):
    if not is_admin():
        return jsonify({"error":"Unauthorized"}), 401
    with db() as c:
        c.execute("UPDATE customers SET status='stopped' WHERE id=?", (cid,))
    return jsonify({"ok":True})

@app.route("/customer")
def customer_page():
    # Demo landing page only. It does not authenticate or control Wi-Fi access.
    return render_template("customer.html")

@app.route("/health")
def health():
    return {"status":"ok"}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False)
