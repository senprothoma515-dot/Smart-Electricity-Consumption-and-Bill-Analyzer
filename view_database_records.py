
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

    tables = ["users", "monthly_consumption", "appliances"]

    for table in tables:
        print(f"\n{'=' * 45}")
        print(f"TABLE: {table.upper()}")
        print("=" * 45)

        cursor.execute(f"SELECT * FROM `{table}` LIMIT 5")

        columns = [item[0] for item in cursor.description]
        rows = cursor.fetchall()

        print("Columns:", columns)

        if rows:
            for row in rows:
                print(row)
        else:
            print("No records found.")

    cursor.close()

except mysql.connector.Error as error:
    print("Database error:", error)

finally:
    if connection is not None and connection.is_connected():
        connection.close()
        print("\nDatabase connection closed.")
