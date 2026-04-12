from flask import *
from database import setup_database, contect
from libery import *


billing_db = Blueprint("billing", __name__)

    


conn = contect()
cursor = conn.cursor()

# 🧾 Billing Page
@billing_db.route("/billing")
def billing():
    cursor.execute("SELECT * FROM inventory")
    products = cursor.fetchall()
    return render_template("billing.html", products=products)

# 📱 Barcode Scan API
@billing_db.route("/get-product/<id>")
def get_product(id):
    cursor.execute(
        "SELECT * FROM inventory WHERE id=%s",
        (id,)
    )
    product = cursor.fetchone()

    if product:
        return {"name": product[1], "price": product[2], "image": product[3], "barcode": product[4],}
    else:
        return {"error": "Not found"}
    
@billing_db.route("/get-gst")
def gst():  
    conn = contect()
    cursor = conn.cursor()
    query = "SELECT gst FROM inventory LIMIT 1"
    cursor.execute(query)
    gst = cursor.fetchone()
    cursor.close()
    conn.close()
    return jsonify(gst)


@billing_db.route("/cart", methods=["POST"])  # ✅ allow POST
def cart():
    data = request.get_json()

    if not data:
        return jsonify({"error": "No JSON received"}), 400

    item_name = data.get("name")

    query = "SELECT * FROM inventory WHERE itemname=%s"
    cursor.execute(query, (item_name,))  # ✅ tuple fix

    item = cursor.fetchone()  # ✅ get single row

    if item:
        gst_tax = item["gst"]  # works if using DictCursor
    else:
        gst_tax = 0

    return jsonify({"gst": gst_tax})


@billing_db.route("/image/<int:id>")
def get_image(id):
    cursor.execute("SELECT image FROM inventory WHERE id=%s", (id,))
    img = cursor.fetchone()
    return Response(img[0], mimetype='image/jpeg')


@billing_db.route("/save-bill", methods=["POST"])
def save_bill():
    data = request.get_json()

    conn = contect()
    cursor = conn.cursor()

    items = data["items"]
    total = data["total"]
    gst = data["gst"]
    grand = data["grand"]

    cursor.execute(
        "INSERT INTO sales (total_amount, gst, grand_total) VALUES (%s,%s,%s)",
        (total, gst, grand)
    )
    conn.commit()

    sale_id = cursor.lastrowid

    for item in items:
        cursor.execute(
            """INSERT INTO sales_items 
            (sale_id, product_name, price, quantity, total)
            VALUES (%s,%s,%s,%s,%s)""",
            (sale_id, item["name"], item["price"], item["qty"], item["total"])
        )

    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"message": "Bill Saved ✅"})





@billing_db.route("/print/<int:id>")
def print_invoice(id):
    cursor.execute("SELECT * FROM firm;")
    header = cursor.fetchone()

    cursor.execute("SELECT * FROM sales WHERE id=%s", (id,))
    invoice = cursor.fetchone()

    cursor.execute("SELECT * FROM sales_items WHERE sale_id=%s", (id,))
    items = cursor.fetchall()

    return render_template("invoice.html", invoice=invoice, items=items, header= header)

@billing_db.route("/billing/<int:sale_id>")
def genpdf(sale_id):
    conn = contect()
    cursor = conn.cursor(dictionary=True)

    # Get bill
    cursor.execute("SELECT * FROM sales WHERE id=%s", (sale_id,))
    bill = cursor.fetchone()

    # Get items
    cursor.execute("SELECT * FROM sales_items WHERE sale_id=%s", (sale_id,))
    billdata = cursor.fetchall()

    folder = os.path.join("static", "tempory")
    os.makedirs(folder, exist_ok=True)

    filepath = os.path.join(folder, f"bill_{sale_id}.pdf")

    width, height = A5
    c = canvas.Canvas(filepath, pagesize=A5)

    c.drawString(50, height - 50, str(firmx))
    c.drawString(50, height - 70, f"Bill No: {bill['id']}")
    c.drawString(50, height - 90, f"Date: {bill['date']}")

    y = height - 120
    c.drawString(50, y, "Item")
    c.drawString(150, y, "Qty")
    c.drawString(200, y, "Price")
    c.drawString(260, y, "Amount")

    y -= 10
    c.line(50, y, 350, y)

    y -= 20
    for item in billdata:
        c.drawString(50, y, str(item['product_name']))
        c.drawString(150, y, str(item['quantity']))
        c.drawString(200, y, str(item['price']))
        c.drawString(260, y, str(item['total']))
        y -= 20

    c.save()

    return send_file(filepath, as_attachment=True)