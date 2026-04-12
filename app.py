from inventory import inventory_db, excel, inventory, b64encode_filter, template
from flask import *
from auth import auth_db, login, register, home, settings
from billing import billing_db, billing, get_product,gst, get_image, save_bill, cart, print_invoice, genpdf
from database import setup_database, contect
from libery import *
from product import product_db, product_id, product_iu, edit

app = Flask(__name__, static_folder="static")

app.register_blueprint(inventory_db)
app.register_blueprint(auth_db)
app.register_blueprint(billing_db)
app.register_blueprint(product_db)

if __name__ == "__main__":
    app.run(debug=True, port=8000)
