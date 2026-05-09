from libery import *
from database import setup_database, contect
from datetime import *
import json

sub_db = Blueprint("subscriptions", __name__)


@sub_db.route("/subscriptions", methods=["POST","GET"])
def subscription():
    user_id = session.get("user")
    if request.method == "POST":
        data =request.get_json() 
        plan_name = data["plan"]
        days = data["days"]
        price = data["price"]

        start_date = datetime.now()
    # Convert days to integer
        days = int(days) if days else 0

        end_date = start_date + timedelta(days=days)

        conn = contect()
        cursor = conn.cursor()

        query = """
        INSERT INTO subscriptions 
        (user_id, plan_name, start_date, end_date, price)
        VALUES (%s, %s, %s, %s, %s)
        """

        cursor.execute(query, (user_id, plan_name, start_date, end_date, price))
        conn.commit()
        cursor.close()
        conn.close()
    conn = contect()
    cursor = conn.cursor()
    qureyu = "select * from rate"
    cursor.execute(qureyu)
    rate = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("subscriptions.html", new=rate)