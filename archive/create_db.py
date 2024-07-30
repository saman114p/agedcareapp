import sqlite3
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()

# Connect to SQLite database (creates it if it doesn't exist)
conn = sqlite3.connect('users.db')

# Create a cursor
c = conn.cursor()

# Create users table
c.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
)
''')

# Insert a test user with a hashed password
username = "sam"
password = bcrypt.generate_password_hash("sam@1234").decode('utf-8')

try:
    c.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
except sqlite3.IntegrityError:
    print("User already exists")

# Commit the changes and close the connection
conn.commit()
conn.close()
