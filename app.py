
from flask import Flask, request, render_template_string, url_for
import sqlite3

app = Flask(__name__)

DB = "users.db"


def init_db():
    with sqlite3.connect(DB) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                username TEXT,
                password TEXT
            )
        """)
        conn.execute("DELETE FROM users")
        conn.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            ("admin", "admin123")
        )


STYLE = """
<style>
* { box-sizing: border-box; }

body {
    font-family: Arial, sans-serif;
    background: gray;
    margin: 0;
    color: #1e293b;
}

.container {
    width: 90%;
    max-width: 460px;
    margin: 20vh auto;
    background: white;
    padding: 35px;
    border-radius: 16px;
    box-shadow: 0 8px 30px rgba(0,0,0,0.08);
    text-align: center;
}

h1 { margin-bottom: 10px; }

.subtitle {
    color: #64748b;
    margin-bottom: 30px;
}

.btn {
    display: block;
    padding: 15px;
    margin: 14px 0;
    color: white;
    text-decoration: none;
    border-radius: 9px;
    font-size: 16px;
    border: none;
    cursor: pointer;
    width: 100%;
}

.danger { background: #dc3545; }
.success { background: #198754; }
.primary { background: #2563eb; }

.btn:hover { opacity: 0.88; }

.back {
    display: inline-block;
    margin-top: 22px;
    color: #64748b;
    text-decoration: none;
}

input {
    width: 100%;
    padding: 13px;
    margin: 9px 0;
    border: 1px solid #cbd5e1;
    border-radius: 8px;
    font-size: 15px;
}

.message {
    margin-top: 20px;
    padding: 12px;
    background: #f1f5f9;
    border-radius: 8px;
}

.info {
    font-size: 13px;
    color: #64748b;
    margin-top: 20px;
}
</style>
"""


MENU = """
<!DOCTYPE html>
<html lang="sk">
<head>
<meta charset="UTF-8">
<title>SQL Injection</title>
""" + STYLE + """
</head>
<body>
<div class="container">
    <h1>Zadanie 2 - SQL Injection</h1>
    <p class="subtitle">Prihlásenie ako demonštrácia SQL Injection</p>
    <p class="info">
        Porovnanie zraniteľnej aplikácie
        a aplikácie chránenej parametrizovaným SQL dopytom.
    </p>

    <label>Zvoľte si verziu:</label>
    <a href="{{ url_for('vulnerable') }}" class="btn danger">
        Nezabezpečená verzia
    </a>

    <a href="{{ url_for('secure') }}" class="btn success">
        Zabezpečená verzia
    </a>

</div>
</body>
</html>
"""


LOGIN = """
<!DOCTYPE html>
<html lang="sk">
<head>
<meta charset="UTF-8">
<title>{{ mode }} – SQL Injection</title>
""" + STYLE + """
</head>
<body>
<div class="container">
    <h1>{{ mode }}</h1>
    <p class="subtitle">Injection na vyskušanie: <b>' OR 1=1 --</b> </p>

    <form method="POST">
        <input
            type="text"
            name="username"
            placeholder="Používateľské meno"
            required
        >

        <input
            type="password"
            name="password"
            placeholder="Heslo"
        >

        <button type="submit" class="btn {{ color }}">
            Prihlásiť sa
        </button>
    </form>

    {% if message %}
        <div class="message">{{ message }}</div>
    {% endif %}

    <a href="{{ url_for('home') }}" class="back">
        ← Späť na hlavné menu
    </a>
</div>
</body>
</html>
"""


@app.route("/")
def home():
    return render_template_string(MENU)


@app.route("/vulnerable", methods=["GET", "POST"])
def vulnerable():
    message = ""

    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")

        query = (
            f"SELECT * FROM users WHERE username = '{username}' "
            f"AND password = '{password}'"
        )

        try:
            with sqlite3.connect(DB) as conn:
                user = conn.execute(query).fetchone()

            message = (
                "Prihlásenie úspešné!"
                if user else "Nesprávne prihlasovacie údaje."
            )
        except sqlite3.Error:
            message = "Chyba SQL dopytu."

    return render_template_string(
        LOGIN,
        mode="Nezabezpečená verzia",
        color="danger",
        message=message
    )


@app.route("/secure", methods=["GET", "POST"])
def secure():
    message = ""

    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")

        query = (
            "SELECT * FROM users "
            "WHERE username = ? AND password = ?"
        )

        with sqlite3.connect(DB) as conn:
            user = conn.execute(query, (username, password)).fetchone()

        message = (
            "Prihlásenie úspešné!"
            if user else "Nesprávne prihlasovacie údaje."
        )

    return render_template_string(
        LOGIN,
        mode="Zabezpečená verzia",
        color="success",
        message=message
    )


if __name__ == "__main__":
    init_db()
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False
    )
