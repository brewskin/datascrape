import psycopg2

# Connect to your postgres DB
conn = psycopg2.connect(
    host="localhost",
    database="datascrape",
    user="script_runner",
    password="home-stone-groan")

# Open a cursor to perform database operations
cur = conn.cursor()

cur.execute(
    "INSERT INTO dumps (tag, contents) VALUES (%s, %s)",
    ('hgfre11', '123sf'))
conn.commit()

# Execute a query
# cur.execute("SELECT * FROM dumps")

# Retrieve query results
cur.execute(
    """
    select
        tag, contents
    from dumps
"""
)
records = cur.fetchall()

print(records)
