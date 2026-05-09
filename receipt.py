from database import setup_database, contect
from flask import Flask
from libery import *


receipt_db = Blueprint("receipt", __name__)

receiptall = []

@receipt_db.route("/receipt", methods=["POST", "GET"])
def report():
    firm_id = session.get("firm_id")
    conn = contect()
    cursor = conn.cursor()
    query = "SELECT * FROM sales WHERE firm_id=%s AND is_deleted = False"
    cursor.execute(query,(firm_id,))
    receiptall = cursor.fetchall()
    for sales in receiptall:
        sale_id = sales[0]

    query2 = "SELECT * FROM sales_items WHERE sale_id=%s"
    cursor.execute(query2,(sale_id,))
    items = cursor.fetchall()
    cursor.close()
    conn.close()

    if request.method == "POST":
        dt = request.form.get("val")

        if dt == "True":
            df = pd.DataFrame(receiptall, columns=["id", "date", "amount", "im", "io", "fi"])

            folder_path = os.path.join(os.getcwd(), "static", "tempory")
            os.makedirs(folder_path, exist_ok=True)

            file_path = os.path.join(folder_path, "report.xlsx")
            df.to_excel(file_path, index=False)

            return send_file(file_path, as_attachment=True)

    return render_template("report.html", recipet=receiptall, item = items)

@receipt_db.route("/print#/<int:id>")
def print_recipt(id):
    conn = contect()
    cursor = conn.cursor()

    # Fetch correct sale
    query = "SELECT * FROM sales WHERE id=%s"
    cursor.execute(query, (id,))
    sale_bill = cursor.fetchone()

    # Fetch items
    query2 = "SELECT * FROM sales_items WHERE sale_id=%s"
    cursor.execute(query2, (id,))
    sales_item = cursor.fetchall()

    cursor.close()
    conn.close()
    p = Usb(0x04b8, 0x0202, 0, profile="TM-T88III")
    p.text("==== RECEIPT ====\n")
    p.text(f"Bill ID: {sale_bill[0]}\n")
    p.text(f"Date-Time: {sale_bill[1]}\n")
    p.text("----------------------\n")
    for item in sales_item:
        p.text(f"{item[1]}  x{item[2]}  Rs.{item[3]}\n")

    p.text("----------------------\n")
    p.text(f"Total: {sale_bill[2]}\n")
    p.text(f"GST: {sale_bill[3]}\n")
    p.text(f"Grand Total: {sale_bill[4]}\n")

    p.image("logo.gif")
    p.barcode('4006381333931', 'EAN13', 64, 2, '', '')
    p.text("\nThank you! Visit again 🙏\n")
    p.cut()

    return "Printed Successfully"

@receipt_db.route("/delete/<int:id>", methods=["POST","GET"])
def delete(id):
    if request.method == "POST":
        conn = contect()
        cursor = conn.cursor()
        qurey = "update sales set is_deleted = TRUE where id=%s"
        cursor.execute(qurey,(id,))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for("report"))