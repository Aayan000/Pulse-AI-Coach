import sqlite3
from datetime import datetime, timedelta
import random

# Create test data
conn = sqlite3.connect('habits.db')
cursor = conn.cursor()

# Create table if not exists
cursor.execute('''
CREATE TABLE IF NOT EXISTS habits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sleep_hours REAL,
    water_litres REAL,
    mood INTEGER,
    timestamp DATETIME
)
''')

# Clear existing data
cursor.execute("DELETE FROM habits")

# Create 7 days of test data
for i in range(7):
    date = datetime.utcnow() - timedelta(days=6-i)
    sleep = round(7 + random.uniform(-1, 1), 1)
    water = round(2 + random.uniform(-0.5, 0.5), 1)
    mood = random.randint(3, 5)
    
    cursor.execute("""
        INSERT INTO habits (sleep_hours, water_litres, mood, timestamp)
        VALUES (?, ?, ?, ?)
    """, (sleep, water, mood, date))

conn.commit()
conn.close()
print("✅ Created 7 days of test data in habits.db")
