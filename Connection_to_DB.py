import mysql.connector
from mysql.connector import Error
import tkinter as tk
from tkinter import scrolledtext


def connect_to_db():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="MySQL123...",
            database="ai_based_security_system")
        if connection.is_connected():
            print("Connected to MySQL database")
            return connection
    except Error as e:
        print(f"Error: {e}")
    return None


def insert_recognition(name, date_time):
    """ Insert recognized name and timestamp into the database """
    connection = connect_to_db()
    if connection:
        cursor = connection.cursor()

        # Check if the name was inserted recently
        check_query = """
        SELECT COUNT(*) FROM known_names
        WHERE name = %s AND date_time > NOW() - INTERVAL 10 SECOND
        """
        cursor.execute(check_query, (name, ))
        count = cursor.fetchone()[0]

        if count == 0:
            # Insert the new record
            insert_query = """
            INSERT INTO known_names (name, date_time)
            VALUES (%s, %s)
            """
            cursor.execute(insert_query, (name, date_time))
            connection.commit()
            print(f"Inserted {name} at {date_time}")

        cursor.close()
        connection.close()


def review_data(text_box):
    """ Function to review data from the database on demand """
    connection = connect_to_db()
    if connection:
        cursor = connection.cursor()

        review_query = "SELECT * FROM known_names ORDER BY date_time DESC"
        cursor.execute(review_query)
        records = cursor.fetchall()

        text_box.delete(1.0, tk.END)  # Clear the text box before displaying new data

        print("Reviewing data from database:")
        for record in records:
            text_box.insert(tk.END, f"Name: {record[1]}, Date and Time: {record[2]}\n")
            # print(f"Name: {record[1]}, Date and Time: {record[2]}")

        cursor.close()
        connection.close()


def create_gui():
    """Create the main application window."""
    root = tk.Tk()
    root.title("AI-Based Multi-Camera Campus Security System")

    # Create a button to review data
    review_button = tk.Button(root, text="Review Data", command=lambda: review_data(text_box))
    review_button.pack(pady=10)

    # Create a scrolled text box to display the results
    text_box = scrolledtext.ScrolledText(root, width=60, height=20)
    text_box.pack(padx=10, pady=10)

    # Start the GUI event loop
    root.mainloop()
