from flask import Blueprint, request, session, redirect, render_template, url_for
from database import contect
from auth import login_required

product_db = Blueprint("product", __name__)

@product_db.route("/product", methods=["GET", "POST"])
@login_required
def product_id():
    firm_id = session.get("firm_id")
    if not firm_id:
        return redirect("/firm")
    conn = contect(); cursor = conn.cursor()
    cursor.execute("SELECT * FROM inventory WHERE firm_id=%s", (firm_id,))
    products = cursor.fetchall()
    cursor.close(); conn.close()
    return render_template("product.html", products=products)

@product_db.route("/delete/<int:id>", methods=["POST"])
@login_required
def product_iu(id):
    conn = contect(); cursor = conn.cursor()
    cursor.execute("DELETE FROM inventory WHERE id=%s AND firm_id=%s", (id, session.get("firm_id")))
    conn.commit(); cursor.close(); conn.close()
    return redirect("/product")

@product_db.route("/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit(id):
    firm_id = session.get("firm_id")
    conn = contect(); cursor = conn.cursor()
    if request.method == "POST":
        name = (request.form.get("productname") or "").strip()
        price = request.form.get("price")
        barcode = request.form.get("barcode")
        file = request.files.get("file")
        if not name or not price:
            cursor.close(); conn.close()
            return "Name and price are required", 400
        if file and file.filename:
            image = file.read()
            if len(image) > 5 * 1024 * 1024:
                cursor.close(); conn.close()
                return "Image too large", 400
            cursor.execute("UPDATE inventory SET name=%s,price=%s,image=%s,barcode=%s WHERE id=%s AND firm_id=%s",
                           (name, price, image, barcode, id, firm_id))
        else:
            cursor.execute("UPDATE inventory SET name=%s,price=%s,barcode=%s WHERE id=%s AND firm_id=%s",
                           (name, price, barcode, id, firm_id))
        conn.commit(); cursor.close(); conn.close()
        return redirect(url_for("product.product_id"))
    cursor.execute("SELECT * FROM inventory WHERE id=%s AND firm_id=%s", (id, firm_id))
    product = cursor.fetchone()
    cursor.close(); conn.close()
    if not product:
        return "Not found", 404
    return render_template("edit.html", product=product, id=id)
