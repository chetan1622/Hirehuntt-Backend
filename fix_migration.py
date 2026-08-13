import sqlite3
conn = sqlite3.connect('job_hunt.db')
c = conn.cursor()

# Fix admin password
c.execute("UPDATE users SET password_hash = ? WHERE username = ?", ("Atul@7276", "admin1622"))
print(f"Updated admin password. Rows affected: {c.rowcount}")

# Create reviews table
c.execute("""
    CREATE TABLE IF NOT EXISTS reviews (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER REFERENCES users(id),
        username TEXT,
        review_text TEXT,
        rating INTEGER DEFAULT 5,
        is_approved INTEGER DEFAULT 0,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
""")
print("Created reviews table")

# Add skills column if missing
try:
    c.execute("ALTER TABLE profiles ADD COLUMN skills TEXT")
    print("Added skills column")
except:
    print("skills column already exists")

conn.commit()
conn.close()
print("Migration done!")
