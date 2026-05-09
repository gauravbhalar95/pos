from flask import *
from libery import *
from database import setup_database, contect

devloper_db = Blueprint("devloper", __name__)

@devloper_db.route("/devregister", methods=["POST","GET"])
def devloperregister():
    if request.method == "POST":
        username =request.form.get("username")
        mobile = request.form.get("mobile")
        password = request.form.get("password")
        hashed = generate_password_hash(password)
        conn = contect()
        cursor = conn.cursor()
        qurey = "insert into devloper (username,mobile,password) values (%s,%s,%s)"
        cursor.execute(qurey(username,mobile,hashed))
        conn.commit()
        cursor.close()
        conn.close()
        return render_template("dev_register.html")

@devloper_db.route("/devloper", methods=["POST","GET"])
def devloperlogin():
    if request.method == "POST":
        username = request.form.get("username")
        mobile = request.form.get("mobile")
        password = request.form.get("password")
        conn = contect()
        cursor = conn.cursor()
        qurey = "SELECT * FROM devloper where username = %s and mobile = %s and password = %s"
        cursor.execute(qurey,(username,mobile,password))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        if user:
            db_user = user[0]
            db_mobile = user[1]
            db_password = user[2]
            if check_password_hash(db_password, password) or db_mobile == mobile:
                session.permanent=True
                session["username"]=username
                return redirect("dev_home")
            else:
                return redirect("dev_login")
    return render_template("devloper.html")

@devloper_db.route("/devloperhome", methods= ["POST","GET"])
def devloperhome():
    conn = contect()
    cursor= conn.cursor()
    qurey = "SELECT COUNT(*) FROM subscriptions WHERE  status='active'"
    cursor.execute(qurey)
    users = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    x = [users]
    y = np.array([4000])
    plt.bar(x,y)
    graph_path = "static/bar.png"
    plt.savefig(graph_path)
    plt.close()
    return render_template("dev_home.html",user=users,graph=graph_path)
@devloper_db.route("/sub/insert", methods=["POST","GET"])
def insert():
    if request.method == "POST":
        plan_name = request.form.get("plan")
        days = request.form.get("days")
        price = request.form.get("price")
        conn=contect()
        cursor = conn.cursor()
        qurey = "INSERT INTO rate (plan_name,days,price) VALUES (%s,%s,%s)"
        cursor.execute(qurey,(plan_name,days,price))
        price = cursor.fetchall()
        conn.commit()
        cursor.close()
        conn.close()
    return render_template("insert.html")
     
@devloper_db.route("/subrate", methods=["POST","GET"])
def subrate():
        conn=contect()
        cursor = conn.cursor()
        qurey = "select * from rate"
        cursor.execute(qurey,)
        price = cursor.fetchall()
        cursor.close()
        conn.close()
        return render_template("subrate.html", prices=price)
@devloper_db.route("/sub/edit/<int:id>", methods=["POST","GET"])
def devloper_edit(id):
    conn = contect()
    cursor = conn.cursor()
    if request.method == "POST":
        days = request.form.get("days")
        price = request.form.get("price")
        plan_name = request.form.get("plann")
        conn = contect()
        cursor = conn.cursor()
        qurey = "update rate set plan_name=%s,days=%s,price=%s where id=%s"
        cursor.execute(qurey,(plan_name,days,price,id))
        cursor.close()
        conn.commit()
        conn.close()
        return redirect(url_for('devloper.devloper_edit', id=id))
    qurey2 = "select * from rate where id=%s"
    cursor.execute(qurey2,(id,))
    plan = cursor.fetchone()
    cursor.close()
    conn.close()
    return render_template("devloper_edit.html", plan=plan)

    
    

    
    
        
        
    
    