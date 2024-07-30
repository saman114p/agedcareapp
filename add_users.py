import sqlite3
from werkzeug.security import generate_password_hash

def init_db():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL
    )
    ''')
    conn.commit()
    conn.close()

def add_users():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    # Add users
    users = [
        ('sam-assistant', generate_password_hash('sam@1234'), 'care assistant'),
        ('sam-admin', generate_password_hash('sam@1234'), 'care admin')
    ]

    cursor.executemany('INSERT INTO users (username, password, role) VALUES (?, ?, ?)', users)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()  # Initialize the database and create the users table if it doesn't exist
    add_users()  # Add initial users to the database
    print("Users added successfully.")
