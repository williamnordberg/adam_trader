import sqlite3

conn = sqlite3.connect('my_database.db')  # Creates or opens the database file
cursor = conn.cursor()

# Create a table with columns
cursor.execute('''
CREATE TABLE IF NOT EXISTS my_table (
    timestamp TEXT,
    factor1 REAL,
    factor2 REAL
    -- Add more columns here as needed
)
''')

# Don't forget to commit changes and close the connection
conn.commit()
conn.close()
