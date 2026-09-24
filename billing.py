from flask import Blueprint, request, session, render_template, jsonify, Response, send_file, redirect
from decimal import Decimal, InvalidOperation
from database import contect
from auth import login_required
from libery import *
import os

billing_db = Blueprint("billing", __name__)

@billing_db.route("/billing")
@login_required
def billing():
    firm_id = session.get("firm_id")
    if not firm_id:
        return redirect("/firm")
    conn = contect(); cursor = conn.cursor()
    cursor.execute("SELECT * FROM inventory WHERE firm_id=%s", (firm_id,))
    products = cursor.fetchall()
    cursor.close(); conn.close()
    return render_template("billing.html", products=products)

@billing_db.route("/get-product/<barcode>")
@login_required
def get_product(barcode):
    conn = contect(); cursor = conn.cursor()
    cursor.execute("SELECT id,name,price,barcode,gst FROM inventory WHERE barcode=%s AND firm_id=%s",
                   (barcode, session.get("firm_id")))
    product = cursor.fetchone()
    cursor.close(); conn.close()
    if not product:
        return jsonify({"error": "Not found"}), 404
    return jsonify({"id": product[0], "name": product[1], "price": float(product[2]),
                    "barcode": product[3], "gst": float(product[4] or 0)})

@billing_db.route("/get-gst/<path:name>")
@login_required
def gst(name):
    conn = contect(); cursor = conn.cursor()
    cursor.execute("SELECT name,gst,price,barcode,id FROM inventory WHERE name=%s AND firm_id=%s",
                   (name, session.get("firm_id")))
    data = cursor.fetchone()
    cursor.close(); conn.close()
    if not data:
        return jsonify({"error": "Not found"}), 404
    return jsonify({"name": data[0], "gst": float(data[1] or 0), "price": float(data[2] or 0),
                    "barcode": data[3], "id": data[4]})

@billing_db.route("/image/<int:id>")
@login_required
def get_image(id):
    conn = contect(); cursor = conn.cursor()
    cursor.execute("SELECT image FROM inventory WHERE id=%s AND firm_id=%s", (id, session.get("firm_id")))
    img = cursor.fetchone()
    cursor.close(); conn.close()
    if not img or not img[0]:
        return "Not found", 404
    return Response(img[0], mimetype="image/jpeg")

@billing_db.route("/save-bill", methods=["POST"])
@login_required
def save_bill():
    firm_id = session.get("firm_id")
    data = request.get_json(silent=True) or {}
    items = data.get("items") or []
    if not firm_id or not items or len(items) > 200:
        return jsonify({"error": "Invalid bill"}), 400

    conn = contect(); cursor = conn.cursor()
    try:
        total = Decimal("0"); gst_total = Decimal("0"); validated = []
        for item in items:
            try:
                product_id = int(item.get("id")); quantity = int(item.get("qty"))
            except (TypeError, ValueError):
                raise ValueError("Invalid product or quantity")
            if quantity <= 0 or quantity > 10000:
                raise ValueError("Invalid quantity")
            cursor.execute("SELECT id,name,price,gst FROM inventory WHERE id=%s AND firm_id=%s",
                           (product_id, firm_id))
            product = cursor.fetchone()
            if not product:
                raise ValueError("Product does not belong to the selected firm")
            price = Decimal(str(product[2])); rate = Decimal(str(product[3] or 0))
            line = price * quantity
            line_gst = (line * rate / Decimal("100")).quantize(Decimal("0.01"))
            total += line; gst_total += line_gst
            validated.append((product, quantity, price, line))
        grand = total + gst_total
        cursor.execute("INSERT INTO sales(total_amount,gst,grand_total,firm_id) VALUES (%s,%s,%s,%s)",
                       (total, gst_total, grand, firm_id))
        sale_id = cursor.lastrowid
        for product, quantity, price, line in validated:
            cursor.execute("""INSERT INTO sales_items
                (sale_id,product_id,product_name,price,quantity,total,firm_id)
                VALUES (%s,%s,%s,%s,%s,%s,%s)""",
                (sale_id, product[0], product[1], price, quantity, line, firm_id))
        conn.commit()
        return jsonify({"message": "Bill Saved", "sale_id": sale_id})
    except (ValueError, InvalidOperation) as exc:
        conn.rollback(); return jsonify({"error": str(exc)}), 400
    except Exception:
        conn.rollback(); return jsonify({"error": "Unable to save bill"}), 500
    finally:
        cursor.close(); conn.close()

@billing_db.route("/print/<int:id>")
@login_required
def print_invoice(id):
    firm_id = session.get("firm_id")
    conn = contect(); cursor = conn.cursor()
    cursor.execute("SELECT * FROM sales WHERE id=%s AND firm_id=%s", (id, firm_id))
    invoice = cursor.fetchone()
    if not invoice:
        cursor.close(); conn.close(); return "Not found", 404
    cursor.execute("SELECT * FROM sales_items WHERE sale_id=%s AND firm_id=%s", (id, firm_id))
    items = cursor.fetchall()
    cursor.execute("SELECT * FROM firm WHERE id=%s AND user_id=%s", (firm_id, session.get("user")))
    header = cursor.fetchone()
    cursor.close(); conn.close()
    return render_template("invoice.html", invoice=invoice, items=items, header=header)

@billing_db.route("/billing/<int:sale_id>")
@login_required
def genpdf(sale_id):
    firm_id = session.get("firm_id")
    conn = contect(); cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM sales WHERE id=%s AND firm_id=%s", (sale_id, firm_id))
    bill = cursor.fetchone()
    if not bill:
        cursor.close(); conn.close(); return "Not found", 404
    cursor.execute("SELECT * FROM sales_items WHERE sale_id=%s AND firm_id=%s", (sale_id, firm_id))
    billdata = cursor.fetchall()
    cursor.execute("SELECT firm FROM firm WHERE id=%s AND user_id=%s", (firm_id, session.get("user")))
    firm = cursor.fetchone()
    folder = os.path.join("static", "tempory"); os.makedirs(folder, exist_ok=True)
    filepath = os.path.join(folder, f"bill_{sale_id}.pdf")
    width, height = A5
    c = canvas.Canvas(filepath, pagesize=A5)
    c.drawString(50, height-50, str(firm["firm"] if firm else "POS"))
    c.drawString(50, height-70, f"Bill No: {bill['id']}")
    c.drawString(50, height-90, f"Date: {bill['date']}")
    y = height-120
    for item in billdata:
        c.drawString(50,y,str(item["product_name"])); c.drawString(150,y,str(item["quantity"]))
        c.drawString(200,y,str(item["price"])); c.drawString(260,y,str(item["total"])); y -= 20
    c.drawString(50,y-10,f"Subtotal: {bill['total_amount']}")
    c.drawString(50,y-30,f"GST: {bill['gst']}")
    c.drawString(50,y-50,f"Grand Total: {bill['grand_total']}")
    c.save(); cursor.close(); conn.close()
    return send_file(filepath, as_attachment=True)
