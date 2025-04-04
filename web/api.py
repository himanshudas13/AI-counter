import os
import sqlite3
from dotenv import load_dotenv
import pandas as pd

class MyTravels:
    def __init__(self):
        load_dotenv()

    def book_ticket(self, name, phone, source, destination, date):
        try:
            with sqlite3.connect("bookings.db", check_same_thread=False) as conn:
                c = conn.cursor()
                c.execute("""
                    INSERT INTO tickets (name, phone, from_city, to_city, date)
                    VALUES (?, ?, ?, ?, ?)
                """, (name, phone, source, destination, date))
                ticket_id = c.lastrowid
                conn.commit()
                df = pd.read_sql_query(f"SELECT * FROM tickets", conn)
                print(df)

            return {
                "status": "success",
                "message": f"Ticket booked successfully from {source} to {destination} on {date}!",
                "ticket_id": ticket_id
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
