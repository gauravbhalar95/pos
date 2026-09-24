import mysql.connector as myconn
from config import DB_HOST, DB_USER, DB_PASSWORD, DB_NAME


def _server_connection():
    return myconn.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
    )


def contect():
    return myconn.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
    )


def setup_database():
    # The server connection is intentionally made without a database so that
    # a fresh deployment can create DB_NAME before connecting to it.
    conn = _server_connection()
    cursor = conn.cursor()
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}`")
    conn.commit()
    cursor.close()
    conn.close()

    conn = contect()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS login(
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(255) NOT NULL UNIQUE,
        password VARCHAR(255) NOT NULL,
        pin VARCHAR(255) DEFAULT NULL,
        father VARCHAR(255),
        mother VARCHAR(255),
        teacher VARCHAR(255)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS inventory(
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255),
        price DECIMAL(10,2),
        image LONGBLOB,
        barcode BIGINT,
        gst INT,
        firm_id VARCHAR(255)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sales(
        id INT NOT NULL AUTO_INCREMENT,
        date DATETIME DEFAULT CURRENT_TIMESTAMP,
        total_amount DECIMAL(10,2) DEFAULT NULL,
        gst DECIMAL(10,2) DEFAULT NULL,
        grand_total DECIMAL(10,2) DEFAULT NULL,
        PRIMARY KEY (id),
        firm_id VARCHAR(255)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sales_items(
        id INT NOT NULL AUTO_INCREMENT,
        sale_id INT,
        product_id INT,
        quantity INT,
        price DECIMAL(10,2),
        product_name VARCHAR(255),
        total DECIMAL(10,2),
        PRIMARY KEY (id),
        FOREIGN KEY (sale_id) REFERENCES sales(id) ON DELETE CASCADE,
        FOREIGN KEY (product_id) REFERENCES inventory(id) ON DELETE CASCADE,
        firm_id VARCHAR(255)
    )
    """)

    conn.commit()
    cursor.close()
    conn.close()


# Call this explicitly from the application startup, not when the module is imported.
