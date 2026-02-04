import sqlite3
import json
import os

def migrate():
    # This creates 'finance.db' automatically
    conn = sqlite3.connect('finance.db')
    cursor = conn.cursor()

    # Create the table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS invoices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client TEXT,
            amount REAL,
            description TEXT,
            date TEXT,
            status TEXT
        )
        
        
    ''')
   



    # This adds the column if it doesn't exist yet
    try:
        cursor.execute("ALTER TABLE invoices ADD COLUMN paid_amount REAL DEFAULT 0.0")
        conn.commit()
        print("Database updated with paid_amount column!")
    except sqlite3.OperationalError:
        print("Column already exists.")

    conn.close()

    # Move data from JSON to SQL
    if os.path.exists('finance_data.json'):
        with open('finance_data.json', 'r') as f:
            data = json.load(f)
            for inv in data.get('invoices', []):
                cursor.execute('''
                    INSERT INTO invoices (client, amount, description, date, status)
                    VALUES (?, ?, ?, ?, ?)
                ''', (inv['client'], inv['amount'], inv['description'], inv['date'], inv['status']))
        
        conn.commit()
        print("✅ Migration complete! You can now use finance.db")
    
    conn.close()

if __name__ == "__main__":
    migrate()