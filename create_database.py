import sqlite3

def create_db():
    # Connect to the SQLite database
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    # Create the users table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        profile_photo TEXT,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
    ''')
    
    # Create the contacts table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS contacts (
        user_id INTEGER,
        contact_id INTEGER,
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (contact_id) REFERENCES users(id),
        PRIMARY KEY (user_id, contact_id)
    )
    ''')
    
    # Create the messages table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sender_id INTEGER,
        receiver_id INTEGER,
        message TEXT,
        sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (sender_id) REFERENCES users(id),
        FOREIGN KEY (receiver_id) REFERENCES users(id)
    )
    ''')
    
    # Create the conversation_messages table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS conversation_messages (
        conversation_id INTEGER,
        message_id INTEGER,
        FOREIGN KEY (conversation_id) REFERENCES conversations(id),
        FOREIGN KEY (message_id) REFERENCES messages(id),
        PRIMARY KEY (conversation_id, message_id)
    )
    ''')
    
    # Create the attachments table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS attachments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        message_id INTEGER,
        file_path TEXT,
        file_type TEXT,
        FOREIGN KEY (message_id) REFERENCES messages(id)
    )
    ''')
    
    # Commit the changes and close the connection
    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_db()
    print("Database and tables created successfully.")
