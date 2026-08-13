import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from backend.database import SessionLocal, User, Profile
from datetime import datetime, timedelta

def create_admin():
    db = SessionLocal()
    
    # Check if admin already exists
    existing = db.query(User).filter(User.username == "admin1622").first()
    if existing:
        print("Admin user 'admin1622' already exists.")
        db.close()
        return

    # Create admin user
    new_user = User(username="admin1622", password_hash="Atul@7276", is_admin=1)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Create profile with premium plan
    new_profile = Profile(
        user_id=new_user.id,
        plan_type='admin',
        payment_status='paid',
        subscription_ends_at=datetime.utcnow() + timedelta(days=3650) # 10 years access
    )
    db.add(new_profile)
    db.commit()
    
    print("Successfully created admin user 'admin1622'.")
    db.close()

if __name__ == "__main__":
    create_admin()
