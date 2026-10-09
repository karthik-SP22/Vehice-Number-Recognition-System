import sqlite3

conn = sqlite3.connect("vehicle_database.db")
cursor = conn.cursor()

# Show all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
print(cursor.fetchall())

# Show stored data
cursor.execute("SELECT * FROM vehicle_data")
rows = cursor.fetchall()

print("\nStored Vehicle Numbers:\n")

for row in rows:
    print(row)

conn.close()