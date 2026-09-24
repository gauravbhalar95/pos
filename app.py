from flask import Flask
from config import SECRET_KEY, PORT
from inventory import inventory_db
from auth import auth_db
from billing import billing_db
from product import product_db
from receipt import receipt_db
from devloper import devloper_db
from subscriptions import sub_db
from database import setup_database


app = Flask(__name__, static_folder="static")
app.secret_key = SECRET_KEY

# Do not enable wildcard CORS globally. If an API client needs CORS, configure
# an explicit list of trusted origins instead.
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=False,  # Set True when deployed behind HTTPS.
    PERMANENT_SESSION_LIFETIME=86400,
)

app.register_blueprint(inventory_db)
app.register_blueprint(auth_db)
app.register_blueprint(billing_db)
app.register_blueprint(product_db)
app.register_blueprint(receipt_db)
app.register_blueprint(devloper_db)
app.register_blueprint(sub_db)

# Create/update the basic schema at startup.
setup_database()

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=PORT)
