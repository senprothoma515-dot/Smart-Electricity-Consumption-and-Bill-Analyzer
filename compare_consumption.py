
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

    query = """
        SELECT month_year, units_consumed
        FROM monthly_consumption
        WHERE user_id = %s
        ORDER BY month_year
    """

    cursor.execute(query, (1,))
    records = cursor.fetchall()

    if len(records) < 2:
        print("At least two monthly records are needed for comparison.")
    else:
        print("\nMONTHLY CONSUMPTION COMPARISON ⚡")
        print("-" * 45)

        for i in range(1, len(records)):
            previous_month, previous_units = records[i - 1]
            current_month, current_units = records[i]

            difference = float(current_units) - float(previous_units)

            if previous_units != 0:
                percentage = difference / float(previous_units) * 100
            else:
                percentage = None

            print(f"\n{previous_month} -> {current_month}")
            print(f"Previous usage: {previous_units} kWh")
            print(f"Current usage: {current_units} kWh")

            if difference > 0:
                print(f"Usage increased by {difference:.2f} kWh")
            elif difference < 0:
                print(f"Usage decreased by {abs(difference):.2f} kWh")
            else:
                print("Usage remained the same.")

            if percentage is not None:
                print(f"Percentage change: {percentage:.2f}%")
            else:
                print("Percentage change unavailable (previous usage was zero).")

    cursor.close()

except mysql.connector.Error as error:
    print("Database error:", error)

finally:
    if connection is not None and connection.is_connected():
        connection.close()
        print("\nDatabase connection closed.")
