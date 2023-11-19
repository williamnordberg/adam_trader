import psycopg2

# Connect to the PostgreSQL database
conn = psycopg2.connect(
    dbname="my_datbasea",
    user="delta",
    password="Ea123123",
    host="localhost"
)

# Create a cursor object
cur = conn.cursor()

# Query to retrieve data
cur.execute("SELECT * FROM my_table")

# Fetch all records
records = cur.fetchall()
for record in records:
    print(record)

    # Close the cursor and connection
cur.close()
conn.close()
