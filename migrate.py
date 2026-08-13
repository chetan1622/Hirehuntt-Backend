import sqlite3
from datetime import datetime, timedelta

def migrate():
    conn = sqlite3.connect('job_hunt.db')
    cursor = conn.cursor()

    try:
        cursor.execute("ALTER TABLE users ADD COLUMN is_admin BOOLEAN DEFAULT 0;")
    except Exception as e:
        print(f"users.is_admin might already exist: {e}")

    try:
        cursor.execute("ALTER TABLE profiles ADD COLUMN plan_type VARCHAR DEFAULT 'trial';")
        cursor.execute("ALTER TABLE profiles ADD COLUMN trial_ends_at DATETIME;")
        cursor.execute("ALTER TABLE profiles ADD COLUMN subscription_ends_at DATETIME;")
        cursor.execute("ALTER TABLE profiles ADD COLUMN payment_status VARCHAR DEFAULT 'unpaid';")
        cursor.execute("ALTER TABLE profiles ADD COLUMN transaction_id VARCHAR;")
    except Exception as e:
        print(f"profiles columns might already exist: {e}")

    # Seed Admin User
    admin_username = "admin1622"
    admin_password = "chetangpatil1622@gmail.com"
    
    cursor.execute("SELECT id FROM users WHERE username = ?", (admin_username,))
    admin_exists = cursor.fetchone()
    
    if not admin_exists:
        cursor.execute(
            "INSERT INTO users (username, password_hash, is_admin) VALUES (?, ?, 1)",
            (admin_username, admin_password)
        )
        admin_id = cursor.lastrowid
        cursor.execute(
            "INSERT INTO profiles (user_id, plan_type) VALUES (?, 'admin')",
            (admin_id,)
        )
        print(f"Created admin user '{admin_username}'")
    else:
        cursor.execute(
            "UPDATE users SET is_admin = 1 WHERE id = ?",
            (admin_exists[0],)
        )
        print(f"Updated admin user '{admin_username}' to have admin privileges")

    conn.commit()
    conn.close()

if __name__ == "__main__":
    migrate()
