from flask import Blueprint, request, session, redirect, render_template, flash
from database import contect
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from datetime import datetime


auth_db = Blueprint("auth", __name__)


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user" not in session:
            return redirect("/login")
        return view(*args, **kwargs)
    return wrapped


@auth_db.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        username = (request.form.get("username") or "").strip()
        password = request.form.get("password") or ""
        pin = request.form.get("pin") or ""
        check_box = request.form.get("true")

        if not username or not password and not pin:
            return redirect("/login")

        session.permanent = bool(check_box)

        conn = contect()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, username, password, pin FROM login WHERE username=%s",
            (username,),
        )
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        valid_password = bool(user and check_password_hash(user[2], password))
        valid_pin = bool(user and user[3] and check_password_hash(user[3], pin))

        if valid_password or valid_pin:
            session.clear()
            session["user"] = user[0]
            return redirect("/add_firm")

        flash("Invalid username or password/PIN.")
        return redirect("/login")

    return render_template("login.html")


@auth_db.route("/securty", methods=["POST", "GET"])
@login_required
def securtyq():
    user_id = session["user"]
    if request.method == "POST":
        father = request.form.get("father")
        teacher = request.form.get("teacher")
        pet = request.form.get("pet")
        conn = contect()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE login SET father=%s, teacher=%s, mother=%s WHERE id=%s",
            (father, teacher, pet, user_id),
        )
        conn.commit()
        cursor.close()
        conn.close()
    return render_template("securty.html")


@auth_db.route("/forgetpassword", methods=["POST", "GET"])
def forget():
    if request.method == "POST":
        username = (request.form.get("username") or "").strip()
        current_password = request.form.get("current") or ""
        new_password = request.form.get("new") or ""
        re_password = request.form.get("re-enter") or ""

        if not username or not new_password or new_password != re_password:
            flash("Passwords do not match or required fields are missing.")
            return redirect("/forgetpassword")

        conn = contect()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, password FROM login WHERE username=%s",
            (username,),
        )
        user = cursor.fetchone()

        if not user or not check_password_hash(user[1], current_password):
            cursor.close()
            conn.close()
            flash("Current password is incorrect.")
            return redirect("/forgetpassword")

        new_hash = generate_password_hash(new_password)
        cursor.execute(
            "UPDATE login SET password=%s WHERE id=%s",
            (new_hash, user[0]),
        )
        conn.commit()
        cursor.close()
        conn.close()
        flash("Password changed successfully.")
        return redirect("/login")

    return render_template("forgetpassword.html")


@auth_db.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "POST":
        username = (request.form.get("username") or "").strip()
        password = request.form.get("password") or ""
        pin = request.form.get("pin") or ""

        if not username or not password:
            flash("Username and password are required.")
            return redirect("/register")

        if pin and (not pin.isdigit() or len(pin) != 4):
            flash("PIN must be exactly 4 digits.")
            return redirect("/register")

        conn = contect()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM login WHERE username=%s", (username,))
        if cursor.fetchone():
            cursor.close()
            conn.close()
            flash("Please select a unique username.")
            return redirect("/register")

        cursor.execute(
            "INSERT INTO login(username, password, pin) VALUES (%s, %s, %s)",
            (
                username,
                generate_password_hash(password),
                generate_password_hash(pin) if pin else None,
            ),
        )
        conn.commit()
        cursor.close()
        conn.close()
        return redirect("/login")

    return render_template("register.html")


@auth_db.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


@auth_db.route("/home", methods=["POST", "GET"])
@login_required
def dashboard():
    now = datetime.now()
    return render_template("home.html", date=now, pos="👑King Pos")


@auth_db.route("/firm", methods=["POST", "GET"])
@login_required
def firmselect():
    user_id = session["user"]
    conn = contect()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM firm WHERE user_id=%s", (user_id,))
    data = cursor.fetchall()

    if request.method == "POST":
        firm_id = request.form.get("firm_id")
        cursor.execute(
            "SELECT id FROM firm WHERE id=%s AND user_id=%s",
            (firm_id, user_id),
        )
        if not cursor.fetchone():
            cursor.close()
            conn.close()
            return redirect("/firm")
        session["firm_id"] = firm_id
        cursor.close()
        conn.close()
        return redirect("/home")

    cursor.close()
    conn.close()
    return render_template("firm.html", firm=data)


@auth_db.route("/add_firm", methods=["POST", "GET"])
@login_required
def addfirm():
    if request.method == "POST":
        firm = request.form.get("firm")
        gstno = request.form.get("gstno")
        firmaddress = request.form.get("firmaddress")
        user_id = session["user"]

        conn = contect()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO firm(firm,gstno,firmaddress,user_id) VALUES (%s,%s,%s,%s)",
            (firm, gstno, firmaddress, user_id),
        )
        conn.commit()
        cursor.close()
        conn.close()
        return redirect("/firm")

    return render_template("add_firm.html")
