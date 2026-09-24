from database import contect
from flask import Blueprint, request, session, redirect, render_template, url_for, send_file
from auth import login_required
from libery import *
import os

receipt_db = Blueprint("receipt", __name__)

@receipt_db.route("/receipt", methods=["POST", "GET"])
@login_required
def report():
    firm_id = session.get("firm_id")
    conn = contect(); cursor = conn.cursor()
    cursor.execute("SELECT * FROM sales WHERE firm_id=%s AND is_deleted=FALSE ORDER BY id DESC", (firm_id,))
    receiptall = cursor.fetchall()

    items_by_sale = {}
    for sale in receiptall:
        cursor.execute("SELECT * FROM sales_items WHERE sale_id=%s AND firm_id=%s", (sale[0], firm_id))
        items_by_sale[sale[0]] = cursor.fetchall()

    if request.method == "POST" and request.form.get("val") == "True":
        df = pd.DataFrame(receiptall)
        folder = os.path.join(os.getcwd(), "static", "tempory")
        os.makedirs(folder, exist_ok=True)
        path = os.path.join(folder, "report.xlsx")
        df.to_excel(path, index=False)
        cursor.close(); conn.close()
        return send_file(path, as_attachment=True)

    cursor.close(); conn.close()
    return render_template("report.html", recipet=receiptall, items_by_sale=items_by_sale)

@receipt_db.route("/print/<int:id>")
@login_required
def print_recipt(id):
    firm_id = session.get("firm_id")
    conn = contect(); cursor = conn.cursor()
    cursor.execute("SELECT * FROM sales WHERE id=%s AND firm_id=%s AND is_deleted=FALSE", (id, firm_id))
    sale_bill = cursor.fetchone()
    if not sale_bill:
        cursor.close(); conn.close(); return "Not found", 404
    cursor.execute("SELECT * FROM sales_items WHERE sale_id=%s AND firm_id=%s", (id, firm_id))
    sales_item = cursor.fetchall()
    cursor.close(); conn.close()

    p = Usb(0x04b8, 0x0202, 0, profile="TM-T88III")
    p.text("==== RECEIPT ====\n")
    p.text(f"Bill ID: {sale_bill[0]}\n")
    p.text(f"Date-Time: {sale_bill[1]}\n")
    for item in sales_item:
        p.text(f"{item[2]}  x{item[3]}  Rs.{item[4]}\n")
    p.text(f"Total: {sale_bill[2]}\nGST: {sale_bill[3]}\nGrand Total: {sale_bill[4]}\n")
    p.cut()
    return "Printed Successfully"

@receipt_db.route("/delete/<int:id>", methods=["POST"])
@login_required
def delete(id):
    conn = contect(); cursor = conn.cursor()
    cursor.execute("UPDATE sales SET is_deleted=TRUE WHERE id=%s AND firm_id=%s", (id, session.get("firm_id")))
    conn.commit(); cursor.close(); conn.close()
    return redirect(url_for("receipt.report"))
