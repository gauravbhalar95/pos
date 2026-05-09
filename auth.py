from flask import *
from database import setup_database, contect
from libery import *
from datetime import datetime, timedelta



auth_db = Blueprint("auth", __name__)

    
@auth_db.route("/login", methods=["POST", "GET"])
def login():

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")
        pin = request.form.get("pin")

        check_box = request.form.get("true")

        # Remember me
        session.permanent = True if check_box else False

        conn = contect()
        cursor = conn.cursor()

        # Get user by username
        query = "SELECT * FROM login WHERE username=%s"
        cursor.execute(query, (username,))

        user = cursor.fetchone()

        conn.close()

        if user:

            db_id = user[0]
            db_username = user[1]
            db_password = user[2]
            db_pin = user[3]
            if check_password_hash(db_password, password) or db_pin == pin:
                session["user"] = db_id
                return redirect("/add_firm")
            else:
                return redirect("/login")

    return render_template("login.html")

@auth_db.route("/securty", methods=["POST","GET"])
def securtyq():
    user_id = session.get("user")
    if request.method == "POST":
        father = request.form.get("father")
        teacher = request.form.get("teacher")
        pet = request.form.get("pet")
        conn = contect()
        cursor = conn.cursor()
        qurey = "UPDATE login SET father=%s,teacher=%s,pet=%s WHERE id=%s"
        cursor.execute(qurey,(father,teacher,pet,user_id))
        conn.commit()
        cursor.close()
        conn.close()
    return render_template("securty.html")

@auth_db.route("/forgetpassword", methods=["POST","GET"])
def forget():
    if request.method == "POST":
        username = request.form.get("username")
        current_password = request.form.get("current")
        new_password = request.form.get("new")
        re_password = request.form.get("re-enter")
        father = request.form.get("father")
        mother = request.form.get("mother")
        teacher = request.form.get("teacher")
        if (new_password == re_password) and (current_password != "") :
            conn = contect()
            cursor = conn.cursor()
            qurey = "update login set password = %s where username = %s"
            cursor.execute(qurey,(new_password,username,))
            conn.commit()
            cursor.close()
            conn.close()
        elif (new_password == re_password) and (current_password == "") :
            conn = contect()
            cursor = conn.cursor()
            qurey = "select * from login where username = %s" 
            cursor.execute(qurey,(username,))
            details = cursor.fetchone()
            cursor.close()
            conn.close()
            if details:
                username1 = details[1]
                father1 = details[4]
                mother1 = details[5]
                teacher1 = details[6]
                if (username1==username) and (father1==father) and (mother1==mother) and (teacher1==teacher):
                    conn = contect()
                    cursor = conn.cursor()
                    qurey = "update login set password = %s where username = %s"
                    cursor.execute(qurey,(new_password,username,))
                    conn.commit()
                    cursor.close()
                    conn.close()


    return render_template("/forgetpassword.html")


@auth_db.route("/register", methods=["POST", "GET"])
def register():

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        pin = request.form.get("pin")

        hashed_password = generate_password_hash(password)

        conn = contect()
        cursor = conn.cursor()

        # Check existing username
        cursor.execute(
            "SELECT * FROM login WHERE username=%s",
            (username,)
        )

        user = cursor.fetchone()

        if user:
            flash("Please select unique username")
            conn.close()
            return redirect("/register")

        # Insert new user
        query = """
            INSERT INTO login(username, password, pin)
            VALUES (%s, %s, %s)
        """

        cursor.execute(query, (username, hashed_password, pin))

        conn.commit()
        conn.close()

        return redirect("/login")

    return render_template("register.html")

@auth_db.route("/logout")
def logout():
    session.pop("user_id",None)
    return redirect("/login")

@auth_db.route("/home", methods = ["POST","GET"])
def dashboard():
    #if "user" not in session:
    #   return redirect("/login")
    #if "user" in session:
        now = datetime.now()
        return render_template("home.html", date = now, pos = "👑King Pos")

@auth_db.route("/firm", methods=["POST","GET"])
def firmselect():
    #if "user" not in session:
    #   return redirect("/login")
    user_id = session.get("user")
    conn = contect()
    cursor = conn.cursor()
    query = "SELECT * FROM firm WHERE user_id = %s"
    cursor.execute(query,(user_id,))
    data = cursor.fetchall()
    cursor.close()
    conn.close() 
    if request.method == "POST":
        firm_id = request.form.get("firm_id")
        session["firm_id"]=firm_id   
        return redirect("/home")
    return render_template("firm.html", firm = data)
    
    
@auth_db.route("/add_firm", methods = ["POST","GET"])
def addfirm():
    #if "user" not in session:
    #   return redirect("/login")
    if request.method == "POST":
        firm = request.form.get("firm")
        gstno = request.form.get("gstno")
        firmaddress = request.form.get("firmaddress")
        user_id = session.get("user")
        conn = contect()
        cursor = conn.cursor()
        query = "insert into firm(firm,gstno,firmaddress,user_id) values (%s,%s,%s,%s)"
        cursor.execute(query,(firm,gstno,firmaddress,user_id))
        conn.commit()
        cursor.close()
        return redirect("firm")
        
    return render_template("add_firm.html")