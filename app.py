import random
from flask import Flask, make_response, render_template, request, redirect, url_for, flash, session
import sqlite3, bcrypt, os
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from markupsafe import Markup
from flask import make_response, session, redirect, url_for, render_template, flash

app = Flask(__name__)
app.secret_key = "secret_key_here"  # Change this in production


# === Token serializer (for password reset) ===
def get_serializer():
    return URLSafeTimedSerializer(app.secret_key, salt="password-reset")


# === DB helpers ===
def get_db():
    return sqlite3.connect("bank.db")


def init_db():
    # Always drop and recreate table for a clean structure
    conn = get_db()
    c = conn.cursor()

    # Drop old table if exists
    # c.execute("DROP TABLE IF EXISTS users")

    # Create fresh users table
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            address TEXT NOT NULL,
            phone_no TEXT UNIQUE NOT NULL,
            email_id TEXT UNIQUE NOT NULL,
            password BLOB NOT NULL,
            repassword BLOB NOT NULL
        )
    """)

    conn.commit()
    conn.close()


# === ROUTES ===
@app.route("/")
def home():
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if "user" in session:
        return redirect(url_for("dashboard"))


    if request.method == "POST":
        email_id = request.form["email_id"].strip()
        password = request.form["password"]

        conn = get_db()
        c = conn.cursor()
        c.execute("SELECT name, phone_no, password FROM users WHERE email_id = ?", (email_id,))
        result = c.fetchone()
        conn.close()

        if result:
            name, phone_no, stored_hash = result
            if bcrypt.checkpw(password.encode("utf-8"), stored_hash):
                # ✅ Store user info in session
                session["user"] = {
                    "name": name,
                    "phone_no": phone_no,
                    "email_id": email_id
                }

                # flash("Logout successful!", "success")
                return redirect(url_for("dashboard"))

        flash("Invalid email or password!", "danger")

    return render_template("login.html")

@app.route("/logout")
def logout():
    # Remove both user and balance from session
    session.pop("user", None)
    session.pop("balance", None)
    session.pop("account_no", None)
    flash("Logout successful!", "success")
    return redirect(url_for("login"))




@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        name = request.form["name"].strip()
        address = request.form["address"].strip()
        phone_no = request.form["phone_no"].strip()
        email_id = request.form["email_id"].strip()
        password = request.form["password"]
        repassword = request.form["repassword"]

        # Validation checks
        if not (name and address and phone_no and email_id and password and repassword):
            flash("All fields are required!", "danger")
            return render_template("signup.html")

        if password != repassword:
            flash("Passwords do not match!", "danger")
            return render_template("signup.html")

        if len(password) < 8:
            flash("Password must be at least 8 characters long!", "danger")
            return render_template("signup.html")

        # Hash the passwords
        hashed_pw = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
        hashed_repw = bcrypt.hashpw(repassword.encode("utf-8"), bcrypt.gensalt())

        try:
            conn = get_db()
            c = conn.cursor()
            c.execute("""
                INSERT INTO users (name, address, phone_no, email_id, password, repassword)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (name, address, phone_no, email_id, hashed_pw, hashed_repw))
            conn.commit()
            conn.close()
            flash("Account created successfully! Please login.", "success")
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            flash("Email ID or Phone Number already exists!", "danger")

    return render_template("signup.html")


# === Forgot Password ===
@app.route("/forgot_password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email_id = request.form["email_id"].strip()

        conn = get_db()
        c = conn.cursor()
        c.execute("SELECT id FROM users WHERE email_id = ?", (email_id,))
        user = c.fetchone()
        conn.close()

        if user:
            s = get_serializer()
            token = s.dumps({"email_id": email_id})
            reset_url = url_for("reset_password", token=token, _external=True)

            # Dev: print reset link
            print(f"[DEV] Password reset link for {email_id}: {reset_url}")

            flash(
                Markup(f'<a class="reset-link" href="{reset_url}">Reset Password Link</a>'),
                "info"
            )

        flash("If this email exists, a reset link has been generated.", "info")
        return redirect(url_for("login"))

    return render_template("forgot_password.html")


@app.route("/reset_password/<token>", methods=["GET", "POST"])
def reset_password(token):
    s = get_serializer()
    try:
        data = s.loads(token, max_age=900)  # 15 minutes
        email_id = data.get("email_id")
    except SignatureExpired:
        flash("Reset link has expired. Please request a new one.", "danger")
        return redirect(url_for("forgot_password"))
    except BadSignature:
        flash("Invalid reset link.", "danger")
        return redirect(url_for("forgot_password"))

    if request.method == "POST":
        new_pw = request.form["password"]
        confirm_pw = request.form["confirm_password"]

        if not new_pw or len(new_pw) < 8:
            flash("Password must be at least 8 characters.", "danger")
            return render_template("reset_password.html", email_id=email_id)

        if new_pw != confirm_pw:
            flash("Passwords do not match.", "danger")
            return render_template("reset_password.html", email_id=email_id)

        hashed_pw = bcrypt.hashpw(new_pw.encode("utf-8"), bcrypt.gensalt())
        hashed_repw = bcrypt.hashpw(confirm_pw.encode("utf-8"), bcrypt.gensalt())

        conn = get_db()
        c = conn.cursor()
        c.execute("UPDATE users SET password = ?, repassword = ? WHERE email_id = ?", (hashed_pw, hashed_repw, email_id))
        conn.commit()
        conn.close()

        flash("Password has been reset. Please login.", "success")
        return redirect(url_for("login"))

    return render_template("reset_password.html", email_id=email_id)


# === DASHBOARD ===
@app.route("/dashboard")
def dashboard():
    user = session.get("user")
    if not user:
        flash("Please login first!", "warning")
        return redirect(url_for("login"))

    if "balance" not in session:
        session["balance"] = random.randint(100000, 300000)

    if "account_no" not in session:
        session["account_no"] = "XXXX" + str(random.randint(1000, 9999))

    phone_no = user["phone_no"]
    masked_phone = "******" + phone_no[-4:]

    email = user["email_id"]
    if "@" in email:
        username, domain = email.split("@", 1)
        visible_part = username[:3]
        masked_email = visible_part + "*" * (len(username) - 3) + "@" + domain
    else:
        masked_email = email

    response = make_response(render_template(
        "dashboard.html",
        name=user["name"],
        masked_phone=masked_phone,
        masked_email=masked_email,
        balance=session["balance"],
        account_no=session["account_no"]
    ))

    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


# === TRANSACTIONS PAGE ===
@app.route("/transactions")
def transactions():
    if "user" not in session:
        return redirect(url_for("login"))

    transactions = [
        {"date": "2025-11-01", "type": "Credit", "amount": 12000, "status": "Successful"},
        {"date": "2025-11-03", "type": "Debit", "amount": 2500, "status": "Successful"},
        {"date": "2025-11-05", "type": "Debit", "amount": 800, "status": "Pending"},
    ]
    return render_template("transactions.html", transactions=transactions)


# === FUND TRANSFER PAGE ===
@app.route("/transfer")
def transfer():
    if "user" not in session:
        return redirect(url_for("login"))
    return render_template("transfer.html")


# === PROFILE PAGE ===
@app.route("/profile")
def profile():
    user = session.get("user")
    if not user:
        return redirect(url_for("login"))

    # Mask phone number (same as dashboard)
    phone_no = user["phone_no"]
    masked_phone = "******" + phone_no[-4:]

    # Mask email
    email = user["email_id"]
    if "@" in email:
        username, domain = email.split("@", 1)
        visible_part = username[:3]
        masked_email = visible_part + "*" * (len(username) - 3) + "@" + domain
    else:
        masked_email = email

    # Ensure session account_no exists
    if "account_no" not in session:
        session["account_no"] = "XXXX" + str(random.randint(1000, 9999))

    return render_template(
        "profile.html",
        user=user,
        masked_phone=masked_phone,
        masked_email=masked_email,
        account_no=session["account_no"],
        balance=session["balance"]
    )


# === AFTER REQUEST ===
@app.after_request
def add_no_cache_headers(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


# === RUN APP ===
if __name__ == "__main__":
    if os.path.exists("bank.db"):
        print("[INFO] Existing database found. Reusing it...")
    init_db()
    app.run(debug=True)