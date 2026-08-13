import re

target = r"c:\Users\cheta\OneDrive\Desktop\Job Hunt Automation\backend\main.py"
with open(target, 'r', encoding='utf-8') as f:
    content = f.read()

# Add ChangePassword schema
schema_patch = """class ResetPassword(BaseModel):
    email: str
    otp: str
    new_password: str

class ChangePassword(BaseModel):
    old_password: str
    new_password: str
"""
content = content.replace("""class ResetPassword(BaseModel):
    email: str
    otp: str
    new_password: str""", schema_patch)

# Replace change_password endpoint
endpoint_patch = """@app.post("/api/change-password/{user_id}")
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
"""

pattern = re.compile(r'@app\.post\("/api/change-password/\{user_id\}"\)\s*def change_password.*?pass', re.DOTALL)
content = pattern.sub(endpoint_patch.strip(), content)

with open(target, 'w', encoding='utf-8') as f:
    f.write(content)
print("Change password route updated.")
