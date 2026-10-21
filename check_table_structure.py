
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
        print(f"\n--- {table.upper()} TABLE ---")

        cursor.execute(f"DESCRIBE `{table}`")

        columns = cursor.fetchall()

        for column in columns:
            print(
                f"Column: {column[0]}, "
                f"Type: {column[1]}, "
                f"Key: {column[3]}"
            )

    cursor.close()

except mysql.connector.Error as error:
    print("Database error:", error)

finally:
    if connection is not None and connection.is_connected():
        connection.close()
        print("\nDatabase connection closed.")

