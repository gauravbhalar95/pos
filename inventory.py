from flask import Blueprint, request, session, redirect, render_template, send_file
from database import contect
from auth import login_required
from libery import *
import os

inventory_db = Blueprint("inventory", __name__)

@inventory_db.route("/import", methods=["POST"])
@login_required
def excel():
    file = request.files.get("import")
    firm_id = session.get("firm_id")
    if not file or not firm_id:
        return "File and firm are required", 400
    if not (file.filename or "").lower().endswith((".xlsx", ".xls")):
        return "Only Excel files are allowed", 400
    df = pd.read_excel(file)
    required = {"name", "price", "barcode", "gst"}
    if not required.issubset(df.columns):
        return "Excel must contain name, price, barcode and gst columns", 400
    conn = contect(); cursor = conn.cursor()
    try:
        for _, row in df.iterrows():
            gst = int(row["gst"])
            if gst not in (0, 5, 12, 18, 28):
                raise ValueError("Invalid GST")
            cursor.execute("INSERT INTO inventory(name,price,barcode,gst,firm_id) VALUES (%s,%s,%s,%s,%s)",
                           (str(row["name"]).strip(), row["price"], row["barcode"], gst, firm_id))
        conn.commit()
    except Exception:
        conn.rollback()
        return "Import failed", 400
    finally:
        cursor.close(); conn.close()
    return redirect("/product")

@inventory_db.route("/inventory", methods=["GET", "POST"])
@login_required
def inventory():
    firm_id = session.get("firm_id")
    if request.method == "POST":
        image_file = request.files.get("file")
        name = (request.form.get("productname") or "").strip()
        price = request.form.get("price")
        barcode = request.form.get("barcode")
        gst_value = request.form.get("gst")
        gst_map = {"gst5": 5, "gst18": 18, "gst28": 28, "0": 0, "5": 5, "18": 18, "28": 28}
        if not firm_id or not name or not price or gst_value not in gst_map:
            return "Invalid product data", 400
        image = image_file.read() if image_file else None
        if image and len(image) > 5 * 1024 * 1024:
            return "Image too large", 400
        conn = contect(); cursor = conn.cursor()
        cursor.execute("INSERT INTO inventory(name,price,image,barcode,gst,firm_id) VALUES (%s,%s,%s,%s,%s,%s)",
                       (name, price, image, barcode, gst_map[gst_value], firm_id))
        conn.commit(); cursor.close(); conn.close()
    return render_template("inventory.html")

@inventory_db.app_template_filter("b64encode")
def b64encode_filter(data):
    if data:
        return base64.b64encode(data).decode("utf-8")
    return ""

@inventory_db.route("/get-template")
@login_required
def template():
    df = pd.DataFrame(columns=["name", "price", "barcode", "gst"])
    folder_path = os.path.join(os.getcwd(), "static", "tempory")
    os.makedirs(folder_path, exist_ok=True)
    file_path = os.path.join(folder_path, "template.xlsx")
    df.to_excel(file_path, index=False)
    return send_file(file_path, as_attachment=True)
