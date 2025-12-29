# [DETECTOR / ASSISTANT] - Database Initialization Script
import sqlite3
import os

DB_NAME = "neurosentry.db"

# Ensure the file is created in the current directory
db_path = os.path.join(os.getcwd(), DB_NAME)
print(f"Initializing database at: {db_path}")

try:
    # Connect (this will create the file)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # --- Create the 'scan_history' table ---
    # Stores the results of every scan
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS scan_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        scan_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        is_threat BOOLEAN NOT NULL,
        confidence REAL,
        explanation TEXT,
        findings_json TEXT 
    );
    """)
    print("Table 'scan_history' created successfully.")

    # --- Create the 'threat_intel' table ---
    # Stores known-bad indicators
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS threat_intel (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        indicator_type TEXT NOT NULL, -- e.g., 'hash', 'ip', 'domain'
        indicator_value TEXT NOT NULL UNIQUE,
        description TEXT 
    );
    """)
    print("Table 'threat_intel' created successfully.")

    # --- Optional: Add a few dummy threat indicators ---
    try:
        cursor.execute("INSERT INTO threat_intel (indicator_type, indicator_value, description) VALUES (?, ?, ?)", 
                       ('hash', 'e1012f46a800d3d3b06385756a1b15b3', 'Known credential theft tool hash'))
        cursor.execute("INSERT INTO threat_intel (indicator_type, indicator_value, description) VALUES (?, ?, ?)", 
                       ('ip', '198.51.100.42', 'Known C2 server IP address'))
        print("Inserted dummy threat intelligence.")
    except sqlite3.IntegrityError:
        print("Dummy threat intelligence already exists.")

    conn.commit()

except Exception as e:
    print(f"An error occurred: {e}")
finally:
    if conn:
        conn.close()
        print("Database initialized and connection closed.")