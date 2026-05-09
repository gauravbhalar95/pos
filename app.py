from inventory import inventory_db, excel, inventory, b64encode_filter, template
from flask import *
from auth import auth_db,forget, login, register, dashboard, addfirm
from billing import billing_db, billing, get_product,gst, get_image, save_bill, print_invoice, genpdf
from database import setup_database, contect
from libery import *
from product import product_db, product_id, product_iu, edit
from receipt import receipt_db, report, print_recipt
from devloper import devloperlogin, devloperhome, devloper_db
from subscriptions import subscription,sub_db
from datetime import timedelta, datetime
from flask_cors import CORS
import gunicorn


app = Flask(__name__, static_folder="static")
app.secret_key = os.urandom(24)
CORS(app)


app.register_blueprint(inventory_db)
app.register_blueprint(auth_db)
app.register_blueprint(billing_db)
app.register_blueprint(product_db)
app.register_blueprint(receipt_db)
app.register_blueprint(devloper_db)
app.register_blueprint(sub_db)

if __name__ == "__main__":
    app.run(debug=True,host="0.0.0.0", port=5000)
