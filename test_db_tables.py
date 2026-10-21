
import mysql.connector

connection = None

try:
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Prothoma@777",
        database="smart_electricity_db"
    )

    cursor = connection.cursor()

    cursor.execute("SHOW TABLES")

    tables = cursor.fetchall()

    print("Connected to smart_electricity_db ⚡")
    print("\nTables found in the database:")

    for table in tables:
        print("-", table[0])

    cursor.close()

except mysql.connector.Error as error:
    print("Database error:", error)

finally:
    if connection is not None and connection.is_connected():
        connection.close()
        print("\nConnection closed.")

