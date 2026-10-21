
import mysql.connector
from mysql.connector import Error


def get_connection():
    """Create and return a MySQL database connection."""
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Prothoma@777",
            database="smart_electricity_db"
        )

        if connection.is_connected():
            return connection

    except Error as error:
        print("Database connection failed:", error)

    return None
