from flask import *
from database import setup_database, contect
from libery import *


auth_db = Blueprint("auth", __name__)

#@app.before_request
#def check():
#         allowed_route=["login","register","subcription","static"]
#         if request.endpoint in allowed_route:
#             return
#         if "user_id" not in session:
#             return redirect("/login")
#         if session.get("role") == "admin":
#            return  # bypass
#         if not is_sub_active(session["user_id"]):
#             return redirect("/subcription")

#def is_subscription_active(user_id):
#    cursor.execute("""
#        SELECT end_date FROM subscriptions
#        WHERE user_id=%s AND status='active'
#        ORDER BY end_date DESC LIMIT 1
#    """, (user_id,))
    
#    sub = cursor.fetchone()

#    if not sub:
#        return False

#    return sub["end_date"] > datetime.now()

#@app.route("/subscription", methods=["POST","GET"])
#def subscriptions():
#    if request.methods=="POST":
#        data = request.form.get("sub")
#        if data == "400":
#            timedate(180)
#        elif data == "750":
#            timedate(750)
#        else:
#            timedate(10)
#    return render_template("subscription.html")
    



@auth_db.route("/", methods = ["POST","GET"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        pin = request.form.get("pin")
        conn = contect()
        cursor = conn.cursor()
        qurey = "select * from login where username=%s and password=%s or pin=%s"
        cursor.execute(qurey,(username,password,pin))
        user = cursor.fetchone()
        if (username == user) and (password == user):
            return redirect(url_for("home"))
        elif (password == user) or (pin == user):
            return redirect(url_for("home"))
        else:
            return redirect(url_for("register")) 
    return render_template("login.html")

@auth_db.route("/register", methods = ["POST","GET"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        pin = request.form.get("pin")
        conn = contect()
        cursor = conn.cursor()
        qurey = "insert into login(username,password,pin) values (%s,%s,%s)"
        cursor.execute(qurey,(username,password,pin))
        conn.commit()
        conn.close()
    return render_template("register.html")

@auth_db.route("/home", methods = ["POST","GET"])
def home():
    now = datetime.now()
    conn = contect()
    cursor = conn.cursor()
    qurey = "SELECT firm FROM firm"
    cursor.execute(qurey)
    firmx = cursor.fetchone()
    conn.close()
    return render_template("home.html", date = now, header = firmx)

@auth_db.route("/firm", methods=["POST","GET"])
def firmselect():
    user_id = session.get("user_id")
    query = "SELECT * FROM firm WHERE user_id = %s"
    cursor.execute(query,(user_id))
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("firm.html", firm = data)
    
    


@auth_db.route("/settings", methods = ["POST","GET"])
def settings():
    if request.method == "POST":
        firm = request.form.get("firm")
        gstno = request.form.get("gstno")
        firmaddress = request.form.get("firmaddress")
        user_id = session.get("user_id")
        conn = contect()
        cursor = conn.cursor()
        query = "insert into firm(firm,gstno,firmaddress,user_id) values (%s,%s,%s,%s)"
        cursor.execute(query,(firm,gstno,firmaddress,user_id))
        conn.commit()
        cursor.close()
        
    return render_template("settings.html")