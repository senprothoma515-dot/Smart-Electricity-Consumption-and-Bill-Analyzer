
from db_connection import get_connection


def show_monthly_consumption():
    connection = get_connection()

    if connection is None:
        print("Could not connect to the database.")
        return

    cursor = connection.cursor()

    cursor.execute("""
        SELECT month_year, units_consumed
        FROM monthly_consumption
        WHERE user_id = 1
        ORDER BY month_year
    """)

    records = cursor.fetchall()

    print("\n--- Monthly Electricity Consumption ---")

    if records:
        for month, units in records:
            print(f"{month}: {units} units")
    else:
        print("No consumption records found.")

    cursor.close()
    connection.close()


def main():
    while True:
        print("\n===== SMART ELECTRICITY ANALYZER =====")
        print("1. View monthly consumption")
        print("2. Exit")

        choice = input("Enter your choice (1-2): ")

        if choice == "1":
            show_monthly_consumption()
        elif choice == "2":
            print("Thank you for using the analyzer! ⚡")
            break
        else:
            print("Invalid choice. Please enter 1 or 2.")


if __name__ == "__main__":
    main()
