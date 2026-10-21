
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

    sql = """
        INSERT INTO monthly_consumption
        (record_id, user_id, month_year, units_consumed)
        VALUES (%s, %s, %s, %s)
    """

    values = (2, 1, "2026-10", 200)

    cursor.execute(sql, values)
    connection.commit()

    print("Electricity consumption saved successfully! ⚡")
    print("Month: October 2026")
    print("Units consumed: 200 kWh")

    cursor.close()

except mysql.connector.Error as error:
    if connection is not None and connection.is_connected():
        connection.rollback()
    print("Database error:", error)

finally:
    if connection is not None and connection.is_connected():
        connection.close()
        print("Database connection closed.")
