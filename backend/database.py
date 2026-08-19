import os
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from datetime import datetime

# Persistent DB Support
DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL:
    # SQLAlchemy 1.4+ requires postgresql:// instead of postgres://
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    SQLALCHEMY_DATABASE_URL = DATABASE_URL
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
else:
    # Railway Volume Support
    VOLUME_PATH = os.getenv("RAILWAY_VOLUME_MOUNT_PATH", ".")
    db_path = os.path.join(VOLUME_PATH, "job_hunt.db")
    SQLALCHEMY_DATABASE_URL = f"sqlite:///{db_path}"
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password_hash = Column(String)
    is_admin = Column(Integer, default=0)
    fcm_token = Column(String, nullable=True)
    last_active = Column(DateTime, nullable=True)  # Track last login for auto-delete
    
    profile = relationship("Profile", back_populates="user", uselist=False)
    logs = relationship("Log", back_populates="user")
    sent_jobs = relationship("SentJob", back_populates="user")
    reviews = relationship("Review", back_populates="user")
    job_history = relationship("JobMatchHistory", back_populates="user")
    saved_jobs = relationship("SavedJob", back_populates="user")

class Profile(Base):
    __tablename__ = "profiles"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    name = Column(String, nullable=True)
    qualification = Column(String, nullable=True)
    searching_roles = Column(String, nullable=True) # Comma-separated roles (e.g. "Data Scientist, Data Analyst")
    location = Column(String, default="India")
    experience = Column(String, nullable=True)
    job_level = Column(String, default="Any Level")
    skills = Column(String, nullable=True)
    receiver_email = Column(String, nullable=True)
    ds_resume_path = Column(String, nullable=True)
    da_resume_path = Column(String, nullable=True)
    
    plan_type = Column(String, default="trial")
    trial_ends_at = Column(DateTime, nullable=True)
    subscription_ends_at = Column(DateTime, nullable=True)
    payment_status = Column(String, default="unpaid")
    transaction_id = Column(String, nullable=True)
    payment_screenshot = Column(String, nullable=True)
    
    user = relationship("User", back_populates="profile")

class Log(Base):
    __tablename__ = "logs"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    timestamp = Column(DateTime, default=datetime.utcnow)
    matched_count = Column(Integer, default=0)
    companies = Column(String, nullable=True) # Comma-separated companies
    status = Column(String) # "success" or "failed"
    
    user = relationship("User", back_populates="logs")

class SentJob(Base):
    """Tracks job links already sent to users to avoid duplicates."""
    __tablename__ = "sent_jobs"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    job_link = Column(Text)
    sent_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="sent_jobs")

class Review(Base):
    """User reviews/feedback. Admin approves before public display."""
    __tablename__ = "reviews"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    username = Column(String)
    review_text = Column(Text)
    rating = Column(Integer, default=5)
    is_approved = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="reviews")

class JobMatchHistory(Base):
    """Stores the daily job matches for a user to display in the app."""
    __tablename__ = "job_match_history"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    date = Column(DateTime, default=datetime.utcnow)
    jobs_json = Column(Text) # JSON string of the jobs array
    
    user = relationship("User", back_populates="job_history")

class SavedJob(Base):
    """Stores individual jobs that the user has bookmarked."""
    __tablename__ = "saved_jobs"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String)
    company = Column(String)
    location = Column(String)
    link = Column(String)
    saved_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="saved_jobs")

def init_db():
    Base.metadata.create_all(bind=engine)
    try:
        from sqlalchemy import text
        with engine.begin() as conn:
            conn.execute(text("ALTER TABLE users ADD COLUMN fcm_token VARCHAR;"))
    except Exception as e:
        pass

    db = SessionLocal()
    try:
        admin_user = db.query(User).filter(User.username == "admin1622").first()
        if not admin_user:
            new_admin = User(
                username="admin1622",
                password_hash="Atul@7276",
                is_admin=1,
                last_active=datetime.utcnow()
            )
            db.add(new_admin)
            db.flush()
            admin_profile = Profile(
                user_id=new_admin.id,
                name="System Admin",
                plan_type="admin",
                payment_status="paid"
            )
            db.add(admin_profile)
            db.commit()
    finally:
        db.close()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
