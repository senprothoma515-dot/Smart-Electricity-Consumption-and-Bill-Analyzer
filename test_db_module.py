
from db_connection import get_connection


connection = get_connection()

if connection:
    print("Database utility module works! ✅")
    print("Connected to smart_electricity_db")

    connection.close()
    print("Connection closed.")
else:
    print("Could not connect to the database.")
