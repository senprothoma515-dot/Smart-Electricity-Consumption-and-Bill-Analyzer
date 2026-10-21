
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
        print("At least two records are needed for analysis.")

    else:
        print("\nHIGH CONSUMPTION DETECTION ⚡")
        print("-" * 45)

        previous_units = []

        for month, units in records:
            units = float(units)

            if len(previous_units) >= 2:
                average = sum(previous_units) / len(previous_units)

                # Flag usage more than 50% above the past average
                threshold = average * 1.5

                print(f"\nMonth: {month}")
                print(f"Consumption: {units:.2f} kWh")
                print(f"Previous average: {average:.2f} kWh")

                if units > threshold:
                    print("WARNING: Unusually high consumption! 🚨")
                else:
                    print("Consumption is within the expected range. ✅")

            else:
                print(f"\n{month}: Baseline record ({units:.2f} kWh)")

            previous_units.append(units)

    cursor.close()

except mysql.connector.Error as error:
    print("Database error:", error)

finally:
    if connection is not None and connection.is_connected():
        connection.close()
        print("\nDatabase connection closed.")
