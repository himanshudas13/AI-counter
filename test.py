import pandas as pd
import sqlite3

# Connect to the SQLite database
conn = sqlite3.connect('bookings.db')

# Read the tickets table into a pandas DataFrame
tickets_df = pd.read_sql_query("SELECT * FROM tickets", conn)

# Print the DataFrame
print(tickets_df)

# Close the connection
conn.close()