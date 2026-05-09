from flask import *
from database import setup_database, contect
from libery import *



product_db = Blueprint("product",__name__)


@product_db.route("/product", methods=["GET", "POST"])
def product_id():
    firm_id = session.get("firm_id")
    conn = contect()
    cursor = conn.cursor()
    query = "SELECT * FROM inventory WHERE firm_id=%s"
    cursor.execute(query,(firm_id,))
    products = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template("product.html", products=products)

@product_db.route("/delete/<int:id>", methods = ["GET","POST"])
def product_iu(id):
    if request.method == "GET":
        conn = contect()
        cursor = conn.cursor()
        qurey = "delete from inventory where id = %s"
        cursor.execute(qurey,(id,))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect("/product")
    return render_template("inventory.html")

@product_db.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):
    conn = contect()
    cursor = conn.cursor()

    if request.method == "POST":
        name = request.form.get("productname")
        price = request.form.get("price")
        barcode = request.form.get("barcode")

        file = request.files.get("file")

        if file and file.filename != "":
            image = file.read()
            query = "UPDATE inventory SET name=%s, price=%s, image=%s, barcode=%s WHERE id=%s"
            cursor.execute(query, (name, price, image, barcode, id))
        else:
            query = "UPDATE inventory SET name=%s, price=%s, barcode=%s WHERE id=%s"
            cursor.execute(query, (name, price, barcode, id))

        conn.commit()
        cursor.close()
        conn.close()

        return redirect(url_for("product.product_id"))

    cursor.execute("SELECT * FROM inventory WHERE id=%s", (id,))
    product = cursor.fetchone()

    cursor.close()
    conn.close()

    return render_template("edit.html", product=product, id=id)