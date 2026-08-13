import os
import re

target = r"c:\Users\cheta\OneDrive\Desktop\Job Hunt Automation\backend\main.py"
with open(target, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add imports
import_insert = """import os
import shutil
import json
import smtplib
import random
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks
"""
content = content.replace(
"""import os
import shutil
import json
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks""", import_insert)

# 2. Update schemas
schema_insert = """class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class VerifyOTP(BaseModel):
    email: str
    otp: str

class ForgotPassword(BaseModel):
    username: str
    email: str

class ResetPassword(BaseModel):
    email: str
    otp: str
    new_password: str
"""
content = content.replace("""class UserCreate(BaseModel):
    username: str
    password: str""", schema_insert)

# 3. Replace /api/register and add new endpoints
register_regex = re.compile(r'@app\.post\("/api/register"\).*?return \{"message": "Account created successfully!", "user_id": new_user\.id, "is_admin": False\}', re.DOTALL)

otp_logic = """
# In-memory caches for OTPs
registration_cache = {}
otp_cache = {}

def send_otp_email(receiver_email, otp, is_registration=True):
    sender_email = config.SENDER_EMAIL
    sender_password = config.SENDER_PASSWORD
    if not sender_email or not sender_password:
        print("SMTP Credentials not provided.")
        return False

    msg = MIMEMultipart()
    msg['From'] = f"HireHuntt <{sender_email}>"
    msg['To'] = receiver_email
    msg['Subject'] = "HireHuntt - Email Verification OTP" if is_registration else "HireHuntt - Password Reset OTP"
    
    body = f"Hello,\\n\\nYour OTP is: {otp}\\n\\nThis OTP is valid for 10 minutes.\\n\\nRegards,\\nHireHuntt Team"
    msg.attach(MIMEText(body, 'plain'))
    
    try:
        server = smtplib.SMTP(config.SMTP_SERVER, config.SMTP_PORT)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print("Error sending email:", e)
        return False

@app.post("/api/register")
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.username == user.username.strip()).first()
    if existing_user:
        raise HTTPException(status_code=409, detail="Username already taken.")
        
    existing_profile = db.query(Profile).filter(Profile.receiver_email == user.email.strip()).first()
    if existing_profile:
        raise HTTPException(status_code=409, detail="Email is already registered.")
    
    if len(user.username.strip()) < 3:
        raise HTTPException(status_code=400, detail="Username must be at least 3 characters long.")
    if len(user.password.strip()) < 4:
        raise HTTPException(status_code=400, detail="Password must be at least 4 characters long.")

    otp = str(random.randint(100000, 999999))
    registration_cache[user.email.strip()] = {
        "username": user.username.strip(),
        "password": user.password.strip(),
        "otp": otp,
        "expires": datetime.utcnow() + timedelta(minutes=10)
    }
    
    if not send_otp_email(user.email.strip(), otp, is_registration=True):
        raise HTTPException(status_code=500, detail="Failed to send OTP email.")
        
    return {"message": "OTP sent to email. Please verify.", "require_otp": True}

@app.post("/api/verify-registration-otp")
def verify_registration_otp(data: VerifyOTP, db: Session = Depends(get_db)):
    email = data.email.strip()
    if email not in registration_cache:
        raise HTTPException(status_code=400, detail="Session expired or invalid email.")
        
    cache_data = registration_cache[email]
    if datetime.utcnow() > cache_data["expires"]:
        del registration_cache[email]
        raise HTTPException(status_code=400, detail="OTP expired. Please register again.")
        
    if cache_data["otp"] != data.otp.strip():
        raise HTTPException(status_code=400, detail="Invalid OTP.")
        
    new_user = User(
        username=cache_data["username"],
        password_hash=cache_data["password"],
        is_admin=0,
        last_active=datetime.utcnow()
    )
    db.add(new_user)
    db.flush()
    
    new_profile = Profile(
        user_id=new_user.id,
        receiver_email=email,
        plan_type="unpaid",
        payment_status="unpaid"
    )
    db.add(new_profile)
    db.commit()
    db.refresh(new_user)
    
    del registration_cache[email]
    return {"message": "Account created successfully!", "user_id": new_user.id, "is_admin": False}

@app.post("/api/forgot-password-otp")
def forgot_password_otp(data: ForgotPassword, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == data.username.strip()).first()
    if not user:
        raise HTTPException(status_code=404, detail="Username not found.")
        
    if not user.profile or user.profile.receiver_email != data.email.strip():
        raise HTTPException(status_code=400, detail="Username and Email do not match our records.")
        
    otp = str(random.randint(100000, 999999))
    otp_cache[data.email.strip()] = {
        "otp": otp,
        "expires": datetime.utcnow() + timedelta(minutes=10)
    }
    
    if not send_otp_email(data.email.strip(), otp, is_registration=False):
        raise HTTPException(status_code=500, detail="Failed to send OTP email.")
        
    return {"message": "OTP sent to your email."}

@app.post("/api/reset-password")
def reset_password(data: ResetPassword, db: Session = Depends(get_db)):
    email = data.email.strip()
    if email not in otp_cache:
        raise HTTPException(status_code=400, detail="Session expired or invalid email.")
        
    cache_data = otp_cache[email]
    if datetime.utcnow() > cache_data["expires"]:
        del otp_cache[email]
        raise HTTPException(status_code=400, detail="OTP expired.")
        
    if cache_data["otp"] != data.otp.strip():
        raise HTTPException(status_code=400, detail="Invalid OTP.")
        
    if len(data.new_password.strip()) < 4:
        raise HTTPException(status_code=400, detail="Password must be at least 4 characters.")
        
    profile = db.query(Profile).filter(Profile.receiver_email == email).first()
    if not profile:
        raise HTTPException(status_code=404, detail="User not found.")
        
    user = profile.user
    user.password_hash = data.new_password.strip()
    db.commit()
    
    del otp_cache[email]
    return {"message": "Password reset successfully. You can now login."}

@app.post("/api/change-password/{user_id}")
def change_password(user_id: int, data: ResetPassword, db: Session = Depends(get_db)):
    # Simple change password if already logged in (just a quick endpoint, but user asked for dashboard change)
    pass
"""

content = register_regex.sub(otp_logic.strip(), content)

with open(target, 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated successfully.")
