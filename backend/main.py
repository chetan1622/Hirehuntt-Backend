import os
import httpx
import google.generativeai as genai
import json
import smtplib
import random
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks

from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from backend import config
from backend.database import engine, Base, init_db, get_db, User, Profile, Log, Review, JobMatchHistory, SavedJob, SessionLocal
from backend.linkedin_scraper import scrape_linkedin_jobs
from backend.career_scraper import scrape_career_sites
from backend.resume_matcher import ResumeMatcher
from backend.notifier import send_email_report

app = FastAPI(title="Job Hunt Automation API")

from fastapi.staticfiles import StaticFiles
import os

app.mount("/uploads", StaticFiles(directory=config.UPLOAD_DIR), name="uploads")

# Enable CORS for the React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=".*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Database on startup
@app.on_event("startup")
def startup_event():
    init_db()
    
    # Auto-create admin if it doesn't exist (fixes ephemeral storage wipes)
    db = SessionLocal()
    if not db.query(User).filter(User.username == "admin1622").first():
        new_admin = User(username="admin1622", password_hash="Atul@7276", is_admin=1)
        db.add(new_admin)
        db.commit()
        db.refresh(new_admin)
        new_profile = Profile(
            user_id=new_admin.id,
            plan_type='admin',
            payment_status='paid',
            subscription_ends_at=datetime.utcnow() + timedelta(days=3650)
        )
        db.add(new_profile)
        db.commit()
    db.close()

    # Start the background scheduler
    scheduler = BackgroundScheduler()
    # 2 AM daily - delete accounts inactive for 30+ days (skip admins)
    scheduler.add_job(auto_delete_inactive_users, CronTrigger(hour=2, minute=0))
    # 8 AM daily - send job emails to all approved users
    scheduler.add_job(daily_job_email_all_users, CronTrigger(hour=8, minute=0))
    scheduler.start()

# Pydantic schemas
class JobMatch(BaseModel):
    title: str
    company: str
    location: str
    link: str
    score: float
    description: str

class SavedJobCreate(BaseModel):
    title: str
    company: str
    location: str
    link: str

class UserCreate(BaseModel):
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

class ChangePassword(BaseModel):
    old_password: str
    new_password: str



class UserLogin(BaseModel):
    username: str
    password: str

class PaymentSubmit(BaseModel):
    transaction_id: str

class ProfileUpdate(BaseModel):
    name: str
    qualification: str
    searching_roles: List[str]
    experience: str
    job_level: str = "Any Level"
    location: str
    receiver_email: str
    skills: str = ""

class ReviewSubmit(BaseModel):
    review_text: str
    rating: int = 5

class ChoosePlan(BaseModel):
    plan: str  # 'trial' or 'premium'

class AtsCheckRequest(BaseModel):
    resume_text: str
    jd_text: str

# Auth endpoints

# In-memory caches for OTPs
registration_cache = {}
otp_cache = {}

def send_otp_email(receiver_email, otp, is_registration=True):
    import requests
    
    sender_email = config.SENDER_EMAIL
    api_key = getattr(config, "RESEND_API_KEY", None)
    
    if not api_key:
        print("Resend API Key not provided.")
        return False

    subject = "HireHuntt - Email Verification OTP" if is_registration else "HireHuntt - Password Reset OTP"
    body = f"Hello,\n\nYour OTP is: {otp}\n\nThis OTP is valid for 10 minutes.\n\nRegards,\nHireHuntt Team"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "from": f"HireHuntt <{sender_email}>",
        "to": [receiver_email],
        "subject": subject,
        "text": body
    }

    try:
        response = requests.post("https://api.resend.com/emails", json=payload, headers=headers, timeout=10)
        if response.status_code in [200, 201]:
            print("OTP sent successfully via Resend API.")
            return True
        else:
            print(f"Error sending OTP via Resend: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"Exception sending OTP via Resend: {e}")
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
    return {"message": "Account created successfully!", "user_id": new_user.id, "username": new_user.username, "is_admin": False}

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
def change_password(user_id: int, data: ChangePassword, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    if user.password_hash != data.old_password.strip():
        raise HTTPException(status_code=400, detail="Incorrect old password")
        
    if len(data.new_password.strip()) < 4:
        raise HTTPException(status_code=400, detail="New password must be at least 4 characters")
        
    user.password_hash = data.new_password.strip()
    db.commit()
    return {"message": "Password updated successfully"}

@app.post("/api/login")
def login_user(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username, User.password_hash == user.password).first()
    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    # Update last_active timestamp on every login
    db_user.last_active = datetime.utcnow()
    db.commit()
    return {"message": "Login successful", "user_id": db_user.id, "is_admin": bool(db_user.is_admin)}


# Profile endpoints
@app.get("/api/profile/{user_id}")
def get_profile(user_id: int, db: Session = Depends(get_db)):
    profile = db.query(Profile).filter(Profile.user_id == user_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
        
    roles = []
    if profile.searching_roles:
        try:
            roles = json.loads(profile.searching_roles)
        except Exception:
            roles = [r.strip() for r in profile.searching_roles.split(",") if r.strip()]
            
    return {
        "name": profile.name or "",
        "qualification": profile.qualification or "",
        "searching_roles": roles,
        "experience": profile.experience or "",
        "location": profile.location or "India",
        "job_level": profile.job_level or "Any Level",
        "skills": profile.skills or "",
        "receiver_email": profile.receiver_email or "",
        "plan_type": profile.plan_type,
        "payment_status": profile.payment_status,
        "trial_ends_at": profile.trial_ends_at.isoformat() if profile.trial_ends_at else None,
        "subscription_ends_at": profile.subscription_ends_at.isoformat() if profile.subscription_ends_at else None,
        "ds_resume_uploaded": bool(profile.ds_resume_path),
        "da_resume_uploaded": bool(profile.da_resume_path)
    }

@app.post("/api/profile/{user_id}")
def update_profile(user_id: int, p_data: ProfileUpdate, db: Session = Depends(get_db)):
    profile = db.query(Profile).filter(Profile.user_id == user_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
        
    profile.name = p_data.name
    profile.qualification = p_data.qualification
    profile.searching_roles = json.dumps(p_data.searching_roles)
    profile.experience = p_data.experience
    profile.location = getattr(p_data, "location", "India")
    profile.job_level = getattr(p_data, "job_level", "Any Level")
    profile.skills = getattr(p_data, "skills", "")
    profile.receiver_email = p_data.receiver_email
    
    db.commit()
    return {"message": "Profile updated successfully"}

# Payment Endpoint
@app.post("/api/payment/submit/{user_id}")
def submit_payment(user_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    profile = db.query(Profile).filter(Profile.user_id == user_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
        
    file_ext = os.path.splitext(file.filename)[1]
    filename = f"user_{user_id}_payment{file_ext}"
    filepath = os.path.join(config.UPLOAD_DIR, filename)
    
    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    profile.payment_screenshot = filename
    profile.payment_status = "pending_approval"
    db.commit()
    return {"message": "Payment submitted. Waiting for Admin approval."}

# Choose Plan (3-day trial or pay ₹199)
@app.post("/api/choose-plan/{user_id}")
def choose_plan(user_id: int, data: ChoosePlan, db: Session = Depends(get_db)):
    profile = db.query(Profile).filter(Profile.user_id == user_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    if data.plan == 'trial':
        profile.plan_type = 'trial'
        profile.trial_ends_at = datetime.utcnow() + timedelta(days=3)
        profile.payment_status = 'trial_active'
        db.commit()
        return {"message": "3-day free trial activated!"}
    elif data.plan == 'premium':
        # User chose to pay - redirect to payment flow
        return {"message": "Proceed to payment", "action": "show_payment"}
    else:
        raise HTTPException(status_code=400, detail="Invalid plan")

# ============================================================
# SAVED JOBS API
# ============================================================

@app.get("/api/saved-jobs/{user_id}")
def get_saved_jobs(user_id: int, db: Session = Depends(get_db)):
    jobs = db.query(SavedJob).filter(SavedJob.user_id == user_id).order_by(SavedJob.saved_at.desc()).all()
    return jobs

@app.post("/api/saved-jobs/{user_id}")
def save_job(user_id: int, job_data: SavedJobCreate, db: Session = Depends(get_db)):
    # Avoid duplicates
    existing = db.query(SavedJob).filter(
        SavedJob.user_id == user_id, 
        SavedJob.link == job_data.link
    ).first()
    if existing:
        return {"message": "Job already saved"}
        
    new_job = SavedJob(
        user_id=user_id,
        title=job_data.title,
        company=job_data.company,
        location=job_data.location,
        link=job_data.link
    )
    db.add(new_job)
    db.commit()
    return {"message": "Job saved successfully"}

@app.delete("/api/saved-jobs/{user_id}/{job_id}")
def remove_saved_job(user_id: int, job_id: int, db: Session = Depends(get_db)):
    job = db.query(SavedJob).filter(SavedJob.id == job_id, SavedJob.user_id == user_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Saved job not found")
    
    db.delete(job)
    db.commit()
    return {"message": "Job removed successfully"}

# Admin Endpoints
@app.get("/api/admin/users")
def get_all_users(db: Session = Depends(get_db)):
    # Returns all users and their subscription status
    users = db.query(User).all()
    res = []
    for u in users:
        p = u.profile
        if not p:
            continue
        res.append({
            "user_id": u.id,
            "username": u.username,
            "name": p.name,
            "plan_type": p.plan_type,
            "payment_status": p.payment_status,
            "transaction_id": p.transaction_id,
            "payment_screenshot": p.payment_screenshot,
            "is_admin": u.is_admin
        })
    return res

@app.post("/api/admin/approve/{user_id}")
def approve_payment(user_id: int, db: Session = Depends(get_db)):
    profile = db.query(Profile).filter(Profile.user_id == user_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
        
    profile.plan_type = "premium"
    profile.payment_status = "paid"
    profile.subscription_ends_at = datetime.utcnow() + timedelta(days=90)
    db.commit()
    return {"message": f"User {user_id} approved for 90 days"}

# Resume uploads
@app.post("/api/upload-resume/{user_id}")
def upload_resume(user_id: int, profile_type: str = Form(...), file: UploadFile = File(...), db: Session = Depends(get_db)):
    profile = db.query(Profile).filter(Profile.user_id == user_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
        
    if profile_type not in ["ds", "da"]:
        raise HTTPException(status_code=400, detail="Invalid profile type. Must be 'ds' or 'da'")
        
    # Save file
    file_ext = os.path.splitext(file.filename)[1]
    filename = f"user_{user_id}_{profile_type}_resume{file_ext}"
    filepath = os.path.join(config.UPLOAD_DIR, filename)
    
    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    # Update DB
    if profile_type == "ds":
        profile.ds_resume_path = filepath
    else:
        profile.da_resume_path = filepath
        
    db.commit()
    return {"message": f"{profile_type.upper()} Resume uploaded successfully", "filename": filename}

# Email Logs
@app.get("/api/logs/{user_id}")
def get_logs(user_id: int, db: Session = Depends(get_db)):
    logs = db.query(Log).filter(Log.user_id == user_id).order_by(Log.timestamp.desc()).all()
    result = []
    for log in logs:
        companies_list = [c.strip() for c in log.companies.split(",") if c.strip()] if log.companies else []
        result.append({
            "id": log.id,
            "timestamp": log.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "matched_count": log.matched_count,
            "companies": companies_list,
            "status": log.status
        })
    return result

# Job Match History
@app.get("/api/job-history/{user_id}")
def get_job_history(user_id: int, db: Session = Depends(get_db)):
    cutoff_date = datetime.utcnow() - timedelta(days=7)
    history = db.query(JobMatchHistory).filter(
        JobMatchHistory.user_id == user_id,
        JobMatchHistory.date >= cutoff_date
    ).order_by(JobMatchHistory.date.desc()).all()
    
    if not history:
        return []
        
    result = []
    for entry in history:
        try:
            jobs = json.loads(entry.jobs_json)
        except Exception:
            jobs = []
        result.append({
            "id": entry.id,
            "date": entry.date.strftime("%B %d, %Y - %I:%M %p"),
            "jobs": jobs
        })
    return result

# Core pipeline execution (Async in background)
def run_job_hunt_pipeline(user_id: int):
    db = SessionLocal()
    try:
        profile = db.query(Profile).filter(Profile.user_id == user_id).first()
        if not profile or not profile.receiver_email:
            print(f"Skipping pipeline for user {user_id}: Profile or receiver email missing.")
            return
        
        roles = []
        if profile.searching_roles:
            try:
                roles = json.loads(profile.searching_roles)
            except Exception:
                roles = [r.strip() for r in profile.searching_roles.split(",") if r.strip()]
            
        if not roles:
            roles = ["Data Analyst"]
        
        # Load resumes
        matcher = ResumeMatcher(
            ds_resume_path=profile.ds_resume_path,
            da_resume_path=profile.da_resume_path
        )
    
        all_raw_jobs = []
        seen_links = set()
        locations = [getattr(profile, "location", "India") or "India"]
    
        # Fetch job list
        for role in roles:
            for loc in locations:
                # LinkedIn
                linkedin_jobs = scrape_linkedin_jobs(role, loc, limit=50)
                # Career Sites
                career_jobs = scrape_career_sites(role, loc, limit=3)
            
                for job in linkedin_jobs + career_jobs:
                    if job['link'] not in seen_links:
                        seen_links.add(job['link'])
                        all_raw_jobs.append(job)
                    
        # Score and match
        matched_jobs = []
        matched_companies = []
        threshold = 15 # Default threshold
    
        for job in all_raw_jobs:
            # Match using the matcher
            match_info = matcher.calculate_match(job['description'], allowed_roles=roles)
            if match_info['score'] >= threshold:
                job['match_info'] = match_info
                matched_jobs.append(job)
                if job['company'] != "N/A" and job['company'] not in matched_companies:
                    matched_companies.append(job['company'])
                
        # Sort
        matched_jobs.sort(key=lambda x: x['match_info']['score'], reverse=True)
    
        # Send Email
        success = send_email_report(matched_jobs, profile.receiver_email)
    
        # Add Log Entry
        companies_str = ", ".join(matched_companies[:8]) # Store first few matched companies
        if len(matched_companies) > 8:
            companies_str += f" (+{len(matched_companies) - 8} more)"
        
        log_entry = Log(
            user_id=user_id,
            matched_count=len(matched_jobs),
            companies=companies_str if matched_jobs else "No matched companies",
            status="success" if success else "failed"
        )
        db.add(log_entry)
        
        # Save to JobMatchHistory
        if matched_jobs:
            history_entry = JobMatchHistory(
                user_id=user_id,
                jobs_json=json.dumps(matched_jobs)
            )
            db.add(history_entry)
            
        db.commit()
    except Exception as e:
        error_msg = str(e)[:200]
        db.add(Log(user_id=user_id, matched_count=0, companies="ERROR", status=f"failed: {error_msg}"))
        db.commit()
    finally:
        db.close()

@app.post("/api/run-matching/{user_id}")
def trigger_matching(user_id: int, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    profile = db.query(Profile).filter(Profile.user_id == user_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
        
    if not profile.ds_resume_path and not profile.da_resume_path:
        raise HTTPException(status_code=400, detail="Please upload at least one resume (Data Science or Data Analyst)")
        
    if not profile.receiver_email:
        raise HTTPException(status_code=400, detail="Please configure a receiver email in your profile")
        
    # Check Subscription / Trial Status
    now = datetime.utcnow()
    has_active_trial = profile.plan_type == 'trial' and profile.trial_ends_at and profile.trial_ends_at > now
    has_active_sub = profile.plan_type == 'premium' and profile.subscription_ends_at and profile.subscription_ends_at > now
    
    if profile.plan_type != 'admin' and not has_active_trial and not has_active_sub:
        raise HTTPException(status_code=403, detail="Subscription expired. Please pay to continue using the service.")
    
    # Check if email already sent today (1 per day limit)
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    todays_log = db.query(Log).filter(
        Log.user_id == user_id,
        Log.timestamp >= today_start,
        Log.status == 'success'
    ).first()
    if todays_log:
        raise HTTPException(status_code=429, detail="Email already sent today. You can run this once per day.")
        
    # Queue the scraper pipeline task in the background
    background_tasks.add_task(run_job_hunt_pipeline, user_id)
    return {"message": "Job hunt pipeline started in the background. You will receive an email shortly."}

# ============================================================
# REVIEW / FEEDBACK ENDPOINTS
# ============================================================

@app.post("/api/ats-check")
def ats_check(request: AtsCheckRequest):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="Gemini API Key is not configured. Please add GEMINI_API_KEY to your environment variables.")
    
    genai.configure(api_key=api_key)
    
    prompt = f"""
    You are an expert ATS (Applicant Tracking System).
    Review this Job Description and this Resume.
    Return ONLY a raw JSON object with no markdown formatting or backticks.
    
    Format:
    {{
        "score": <integer from 0 to 100 representing the match percentage>,
        "missing_keywords": [<list of important skills/keywords from the JD missing in the resume>],
        "project_suggestions": [<list of 2-3 specific project ideas the candidate could build to gain the missing skills for this role>]
    }}
    
    Job Description:
    {request.jd_text}
    
    Resume:
    {request.resume_text}
    """
    
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        text = response.text.strip()
        if text.startswith("```json"):
            text = text[7:-3]
        elif text.startswith("```"):
            text = text[3:-3]
        data = json.loads(text.strip())
        return data
    except Exception as e:
        print(f"Error calling Gemini: {e}")
        raise HTTPException(status_code=500, detail="Failed to analyze resume with AI.")

@app.post("/api/review/{user_id}")
def submit_review(user_id: int, data: ReviewSubmit, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    review = Review(
        user_id=user_id,
        username=user.username,
        review_text=data.review_text,
        rating=min(max(data.rating, 1), 5)
    )
    db.add(review)
    db.commit()
    return {"message": "Review submitted! It will be visible after admin approval."}

@app.get("/api/reviews/approved")
def get_approved_reviews(db: Session = Depends(get_db)):
    reviews = db.query(Review).filter(Review.is_approved == 1).order_by(Review.created_at.desc()).all()
    return [{
        "id": r.id,
        "username": r.username,
        "review_text": r.review_text,
        "rating": r.rating,
        "created_at": r.created_at.strftime("%Y-%m-%d") if r.created_at else ""
    } for r in reviews]

@app.get("/api/admin/reviews")
def get_all_reviews(db: Session = Depends(get_db)):
    reviews = db.query(Review).order_by(Review.created_at.desc()).all()
    return [{
        "id": r.id,
        "username": r.username,
        "review_text": r.review_text,
        "rating": r.rating,
        "is_approved": r.is_approved,
        "created_at": r.created_at.strftime("%Y-%m-%d") if r.created_at else ""
    } for r in reviews]

@app.post("/api/admin/review/approve/{review_id}")
def approve_review(review_id: int, db: Session = Depends(get_db)):
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    review.is_approved = 1
    db.commit()
    return {"message": "Review approved"}

@app.post("/api/admin/review/reject/{review_id}")
def reject_review(review_id: int, db: Session = Depends(get_db)):
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    db.delete(review)
    db.commit()
    return {"message": "Review rejected and deleted"}

# Subscription status check endpoint
@app.get("/api/subscription-status/{user_id}")
def get_subscription_status(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    profile = user.profile
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    now = datetime.utcnow()
    status = "expired"
    
    if user.is_admin or profile.plan_type == 'admin':
        status = "active"
    elif profile.plan_type == 'trial' and profile.trial_ends_at and profile.trial_ends_at > now:
        status = "trial_active"
    elif profile.plan_type == 'premium' and profile.subscription_ends_at and profile.subscription_ends_at > now:
        status = "active"
    elif profile.payment_status == 'pending_approval':
        status = "pending_approval"
    
    return {
        "status": status,
        "plan_type": profile.plan_type,
        "payment_status": profile.payment_status,
        "trial_ends_at": profile.trial_ends_at.isoformat() if profile.trial_ends_at else None,
        "subscription_ends_at": profile.subscription_ends_at.isoformat() if profile.subscription_ends_at else None
    }


# ============================================================
# SCHEDULED JOBS
# ============================================================

def auto_delete_inactive_users():
    """Runs at 2 AM daily. Deletes non-admin users inactive for 30+ days."""
    print("[Scheduler] Running auto-delete for inactive users...")
    db = SessionLocal()
    try:
        cutoff = datetime.utcnow() - timedelta(days=30)
        # Find non-admin users with last_active older than 30 days (or never logged in > 30 days ago)
        inactive_users = db.query(User).filter(
            User.is_admin == 0,
            User.last_active != None,
            User.last_active < cutoff
        ).all()
        
        for user in inactive_users:
            print(f"[Scheduler] Deleting inactive user: {user.username} (last active: {user.last_active})")
            # Delete sent_jobs
            db.query(SentJob).filter(SentJob.user_id == user.id).delete()
            # Delete logs
            db.query(Log).filter(Log.user_id == user.id).delete()
            # Delete profile
            db.query(Profile).filter(Profile.user_id == user.id).delete()
            # Delete user
            db.delete(user)
        
        db.commit()
        print(f"[Scheduler] Auto-delete complete. Deleted {len(inactive_users)} inactive users.")
    except Exception as e:
        print(f"[Scheduler] Auto-delete error: {e}")
        db.rollback()
    finally:
        db.close()


def daily_job_email_all_users():
    """Runs at 8 AM daily. Sends job emails to all approved/admin users. No repeated job links."""
    print("[Scheduler] Running daily 8 AM job email for all approved users...")
    db = SessionLocal()
    try:
        # Get all premium + admin users with receiver_email configured
        approved_users = db.query(User).filter(User.is_admin == 1).all()
        premium_profiles = db.query(Profile).filter(
            Profile.plan_type.in_(["premium", "admin"]),
            Profile.payment_status == "paid",
            Profile.receiver_email != None
        ).all()
        
        # Collect all user_ids to process
        processed_ids = set()
        users_to_process = []
        
        for u in approved_users:
            if u.id not in processed_ids and u.profile and u.profile.receiver_email:
                users_to_process.append(u)
                processed_ids.add(u.id)
        
        for p in premium_profiles:
            if p.user_id not in processed_ids and p.receiver_email:
                user = db.query(User).filter(User.id == p.user_id).first()
                if user:
                    users_to_process.append(user)
                    processed_ids.add(user.id)
        
        for user in users_to_process:
            try:
                profile = user.profile
                if not profile or not profile.receiver_email:
                    continue
                
                roles = []
                if profile.searching_roles:
                    try:
                        roles = json.loads(profile.searching_roles)
                    except Exception:
                        roles = [r.strip() for r in profile.searching_roles.split(",") if r.strip()]
                if not roles:
                    roles = ["Data Analyst"]
                
                # Get already-sent job links for this user
                already_sent = set(
                    sj.job_link for sj in db.query(SentJob).filter(SentJob.user_id == user.id).all()
                )
                
                # Load matcher
                matcher = ResumeMatcher(
                    ds_resume_path=profile.ds_resume_path,
                    da_resume_path=profile.da_resume_path
                )
                
                all_raw_jobs = []
                seen_links = set()
                locations = [getattr(profile, "location", "India") or "India"]
                
                for role in roles:
                    for loc in locations:
                        linkedin_jobs = scrape_linkedin_jobs(role, loc, limit=50)
                        career_jobs = scrape_career_sites(role, loc, limit=3)
                        for job in linkedin_jobs + career_jobs:
                            if job['link'] not in seen_links and job['link'] not in already_sent:
                                seen_links.add(job['link'])
                                all_raw_jobs.append(job)
                
                # Score and filter
                matched_jobs = []
                matched_companies = []
                threshold = 15
                
                for job in all_raw_jobs:
                    match_info = matcher.calculate_match(job['description'], allowed_roles=roles)
                    if match_info['score'] >= threshold:
                        job['match_info'] = match_info
                        matched_jobs.append(job)
                        if job['company'] != "N/A" and job['company'] not in matched_companies:
                            matched_companies.append(job['company'])
                
                matched_jobs.sort(key=lambda x: x['match_info']['score'], reverse=True)
                
                if not matched_jobs:
                    print(f"[Scheduler] No new jobs for user {user.username}, skipping email.")
                    continue
                
                # Send email
                success = send_email_report(matched_jobs, profile.receiver_email)
                
                if success:
                    # Save sent job links to avoid repeats
                    for job in matched_jobs:
                        db.add(SentJob(user_id=user.id, job_link=job['link']))
                    
                    # Log entry
                    companies_str = ", ".join(matched_companies[:8])
                    if len(matched_companies) > 8:
                        companies_str += f" (+{len(matched_companies) - 8} more)"
                    
                    db.add(Log(
                        user_id=user.id,
                        matched_count=len(matched_jobs),
                        companies=companies_str,
                        status="success"
                    ))
                    db.commit()
                    print(f"[Scheduler] Email sent to {user.username} ({profile.receiver_email}) with {len(matched_jobs)} jobs.")
                else:
                    db.add(Log(user_id=user.id, matched_count=0, companies="", status="failed"))
                    db.commit()
                    
            except Exception as e:
                print(f"[Scheduler] Error processing user {user.username}: {e}")
                db.rollback()
        
        print("[Scheduler] Daily 8 AM job email complete.")
    except Exception as e:
        print(f"[Scheduler] Daily email error: {e}")
    finally:
        db.close()
