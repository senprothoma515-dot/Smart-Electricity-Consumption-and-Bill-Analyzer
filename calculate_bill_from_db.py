
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

    if records:
        print("\nMONTHLY ELECTRICITY BILL REPORT")
        print("-" * 45)

        rate_per_unit = 6
        fixed_charge = 100
        total_bill = 0

        for month, units in records:
            energy_charge = float(units) * rate_per_unit
            bill = energy_charge + fixed_charge
            total_bill += bill

            print(f"Month: {month}")
            print(f"Units consumed: {units} kWh")
            print(f"Energy charge: Rs. {energy_charge:.2f}")
            print(f"Fixed charge: Rs. {fixed_charge:.2f}")
            print(f"Estimated bill: Rs. {bill:.2f}")
            print("-" * 45)

        print(f"Total of displayed bills: Rs. {total_bill:.2f}")

    else:
        print("No consumption records found for user ID 1.")

    cursor.close()

except mysql.connector.Error as error:
    print("Database error:", error)

finally:
    if connection is not None and connection.is_connected():
        connection.close()
        print("\nDatabase connection closed.")
