import mysql.connector
from mysql.connector import Error


def get_connection():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Archana_2006",
            database="studenthub"
        )

        if connection.is_connected():
            return connection

    except Error as e:
        print("Database Connection Error:", e)
        return None