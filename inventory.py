from flask import *
from database import setup_database, contect
from libery import *
from product import *





inventory_db = Blueprint("inventory", __name__)


@inventory_db.route("/import", methods=["POST"])
def excel():
    file = request.files["import"]
    df = pd.read_excel(file)

    conn = contect()
    cursor = conn.cursor()

    for index, row in df.iterrows():
        query = "INSERT INTO inventory(name, price, barcode, gst) VALUES (%s, %s, %s, %s)"
        cursor.execute(query, (row["name"], row["price"], row["barcode"], row["gst"]))

    conn.commit()   # commit once (faster ✅)

    cursor.close()
    conn.close()

    return redirect("/product")   # ✅ IMPORTANT
       

@inventory_db.route("/inventory", methods=["GET", "POST"])
def inventory():
    if request.method == "POST":
        image = request.files["file"].read()
        name = request.form.get("productname")
        price = request.form.get("price")
        barcode = request.form.get("barcode")
        gst = request.form.get("gst")
        firm_id = session.get("firm_id")
        if gst == "gst5":
            gst = "5"
        elif gst == "gst18":
            gst = "18"
        else:
            gst = "28"

        conn = contect()
        cursor = conn.cursor()

        query = "INSERT INTO inventory(name, price, image, barcode,gst,firm_id) VALUES (%s,%s, %s, %s, %s, %s)"
        cursor.execute(query, (name, price, image, barcode,gst,firm_id))

        conn.commit()
        cursor.close()
        conn.close()

    return render_template("inventory.html") 



@inventory_db.app_template_filter('b64encode')
def b64encode_filter(data):
    if data:
        return base64.b64encode(data).decode('utf-8')
    return ""

@inventory_db.route("/get-template")
def template():
 
    df = pd.DataFrame(columns=["name", "price", "barcode","gst"])
    folder_path = os.path.join(os.getcwd(), "static", "tempory")
    os.makedirs(folder_path, exist_ok=True)
    file_path = os.path.join(folder_path, "template.xlsx")
    df.to_excel(file_path, index=False)
    return send_file(file_path, as_attachment=True)