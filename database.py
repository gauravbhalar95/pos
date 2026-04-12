import mysql.connector as myconn


def contect():
    conn = myconn.connect(host="127.0.0.1",user="root",password="1234",database="website")
    return conn



def setup_database():
    # Step 1: Connect to MySQL (without database)
    conn = contect()

    cursor = conn.cursor()

    # Step 2: Create database
    cursor.execute("CREATE DATABASE IF NOT EXISTS website")

    # Step 3: Select database
    cursor.execute("USE website")

    # Step 4: Create login table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS login(
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(255),
        password VARCHAR(255),
        pin INT
    )
    """)

    # Step 5: Create inventory table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS inventory(
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255),
        price INT,
        image LONGBLOB,
        barcode BIGINT,
        gst INT
    )
    """)

    # Step 6: Create sales table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sales(
        id INT NOT NULL AUTO_INCREMENT,
        date DATETIME DEFAULT CURRENT_TIMESTAMP,
        total_amount DECIMAL(10, 2) DEFAULT NULL,
        gst VARCHAR(255) DEFAULT NULL,
        grand_total INT DEFAULT NULL,
        PRIMARY KEY (id)
    )
    """)

    # Step 7: Create sales_items table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sales_items(
        id INT NOT NULL AUTO_INCREMENT,
        sale_id INT,
        product_id INT,
        quantity INT,
        price DECIMAL(10, 2),
        product_name VARCHAR(255),
        total INT,
        PRIMARY KEY (id),
        FOREIGN KEY (sale_id) REFERENCES sales(id) ON DELETE CASCADE,
        FOREIGN KEY (product_id) REFERENCES inventory(id) ON DELETE CASCADE
    )
    """)

    # Step 8: Commit changes
    conn.commit()

    # Step 9: Close connection
    cursor.close()
    conn.close()



# Run setup
setup_database()