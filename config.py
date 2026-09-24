import os
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DB_HOST") or os.getenv("host")
DB_USER = os.getenv("DB_USER") or os.getenv("user")
DB_PASSWORD = os.getenv("DB_PASSWORD") or os.getenv("password")
DB_NAME = os.getenv("DB_NAME") or os.getenv("database")
PORT = int(os.getenv("PORT") or os.getenv("port") or 5000)
SECRET_KEY = os.getenv("SECRET_KEY")

if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY is required. Set it in the environment.")
