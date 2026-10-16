
from db import get_db_connection

connection = get_db_connection()

if connection and connection.is_connected():
    print("MySQL connected successfully!")

    cursor = connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM schemes")
    result = cursor.fetchone()

    print("Total schemes:", result[0])

    cursor.close()
    connection.close()
else:
    print("Connection failed. Check your database settings.")
