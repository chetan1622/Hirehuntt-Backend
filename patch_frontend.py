import re

target = r"c:\Users\cheta\OneDrive\Desktop\Job Hunt Automation\frontend\src\App.jsx"
with open(target, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Replace AuthPage entirely
auth_page_new = """// Auth Page (Login, Register, Forgot Password, Verification)
function AuthPage({ onLogin }) {
  const [view, setView] = useState('register') // 'login', 'register', 'verify', 'forgot', 'reset'
  const [username, setUsername] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [otp, setOtp] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [showConfirm, setShowConfirm] = useState(false)
  
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  const handleRegister = async (e) => {
    e.preventDefault()
    if (!username.trim() || !password.trim() || !email.trim()) return setError('Please fill in all fields')
    if (password !== confirmPassword) return setError('Passwords do not match')
    setLoading(true); setError(''); setSuccess('')

    try {
      const res = await fetch(`${API}/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username: username.trim(), email: email.trim(), password: password.trim() })
      })
      const data = await res.json()
      if (!res.ok) { setError(data.detail || 'Registration failed'); setLoading(false); return; }
      if (data.require_otp) { setSuccess(data.message); setView('verify') }
    } catch (err) { setError('Network error.') }
    setLoading(false)
  }

  const handleVerify = async (e) => {
    e.preventDefault()
    if (!otp.trim()) return setError('Please enter the OTP')
    setLoading(true); setError(''); setSuccess('')

    try {
      const res = await fetch(`${API}/verify-registration-otp`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: email.trim(), otp: otp.trim() })
      })
      const data = await res.json()
      if (!res.ok) { setError(data.detail || 'Verification failed'); setLoading(false); return; }
      onLogin(data.user_id, data.username, data.is_admin)
    } catch (err) { setError('Network error.') }
    setLoading(false)
  }

  const handleLogin = async (e) => {
    e.preventDefault()
    if (!username.trim() || !password.trim()) return setError('Please fill in all fields')
    setLoading(true); setError(''); setSuccess('')
    try {
      const res = await fetch(`${API}/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username: username.trim(), password: password.trim() })
      })
      const data = await res.json()
      if (!res.ok) { setError(data.detail || 'Invalid username or password'); setLoading(false); return; }
      onLogin(data.user_id, username.trim(), data.is_admin)
    } catch (err) { setError('Network error.') }
    setLoading(false)
  }

  const handleForgot = async (e) => {
    e.preventDefault()
    if (!username.trim() || !email.trim()) return setError('Please provide Username and Email')
    setLoading(true); setError(''); setSuccess('')
    try {
      const res = await fetch(`${API}/forgot-password-otp`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username: username.trim(), email: email.trim() })
      })
      const data = await res.json()
      if (!res.ok) { setError(data.detail || 'Failed to send OTP'); setLoading(false); return; }
      setSuccess(data.message); setView('reset')
    } catch (err) { setError('Network error.') }
    setLoading(false)
  }

  const handleReset = async (e) => {
    e.preventDefault()
    if (!otp.trim() || !password.trim() || !confirmPassword.trim()) return setError('Fill all fields')
    if (password !== confirmPassword) return setError('Passwords do not match')
    setLoading(true); setError(''); setSuccess('')
    try {
      const res = await fetch(`${API}/reset-password`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: email.trim(), otp: otp.trim(), new_password: password.trim() })
      })
      const data = await res.json()
      if (!res.ok) { setError(data.detail || 'Failed to reset password'); setLoading(false); return; }
      setSuccess(data.message); setView('login')
    } catch (err) { setError('Network error.') }
    setLoading(false)
  }

  return (
    <div className="auth-wrapper">
      <div className="auth-logo">
        <div style={{display:"flex", alignItems:"center", justifyContent:"center", gap: 10}}>
          <img src="/h_logo.jpg" alt="Logo" style={{height: 32, borderRadius: 6}}/> Hire Huntt
        </div>
        <span>Smart Job Matching & Resume Analysis</span>
      </div>
      
      <div className="auth-card">
        { (view === 'login' || view === 'register') && (
          <div style={{ display: 'flex', background: 'rgba(255,255,255,0.05)', borderRadius: 10, padding: 4, marginBottom: 20, gap: 4 }}>
            <button
              onClick={() => {setView('login'); setError(''); setSuccess('')}}
              style={{
                flex: 1, padding: '8px 0', border: 'none', borderRadius: 8, cursor: 'pointer', fontSize: 13, fontWeight: 600,
                background: view === 'login' ? 'var(--accent-indigo)' : 'transparent',
                color: view === 'login' ? '#fff' : 'var(--text-muted)'
              }}>🔑 Login</button>
            <button
              onClick={() => {setView('register'); setError(''); setSuccess('')}}
              style={{
                flex: 1, padding: '8px 0', border: 'none', borderRadius: 8, cursor: 'pointer', fontSize: 13, fontWeight: 600,
                background: view === 'register' ? 'var(--accent-indigo)' : 'transparent',
                color: view === 'register' ? '#fff' : 'var(--text-muted)'
              }}>✨ Create Account</button>
          </div>
        )}

        <h2>
          {view === 'register' ? 'Create New Account' : 
           view === 'login' ? 'Welcome Back' : 
           view === 'verify' ? 'Verify Email' : 
           view === 'forgot' ? 'Forgot Password' : 'Reset Password'}
        </h2>

        {error && <p style={{ color: '#ef4444', fontSize: '12px', marginBottom: '10px', background: 'rgba(239,68,68,0.08)', padding: '8px 10px', borderRadius: 6 }}>{error}</p>}
        {success && <p style={{ color: '#10b981', fontSize: '12px', marginBottom: '10px' }}>{success}</p>}

        {view === 'register' && (
          <form onSubmit={handleRegister}>
            <div className="form-group"><label>Username</label><input type="text" value={username} onChange={e => setUsername(e.target.value)} placeholder="Choose a username"/></div>
            <div className="form-group"><label>Email Address</label><input type="email" value={email} onChange={e => setEmail(e.target.value)} placeholder="your_email@gmail.com"/></div>
            <div className="form-group">
              <label>Password</label>
              <div style={{display:'flex', position:'relative'}}>
                <input type={showPassword ? "text" : "password"} value={password} onChange={e => setPassword(e.target.value)} style={{flex: 1}} placeholder="Create a password"/>
                <span onClick={() => setShowPassword(!showPassword)} style={{position:'absolute', right:10, top:10, cursor:'pointer'}}>👁️</span>
              </div>
            </div>
            <div className="form-group">
              <label>Confirm Password</label>
              <div style={{display:'flex', position:'relative'}}>
                <input type={showConfirm ? "text" : "password"} value={confirmPassword} onChange={e => setConfirmPassword(e.target.value)} style={{flex: 1}} placeholder="Re-enter password"/>
                <span onClick={() => setShowConfirm(!showConfirm)} style={{position:'absolute', right:10, top:10, cursor:'pointer'}}>👁️</span>
              </div>
            </div>
            <button className="btn-primary" type="submit" disabled={loading}>{loading ? '⏳' : 'Send Verification OTP'}</button>
          </form>
        )}

        {view === 'verify' && (
          <form onSubmit={handleVerify}>
            <div className="form-group"><label>Enter OTP sent to {email}</label><input type="text" value={otp} onChange={e => setOtp(e.target.value)} placeholder="6-digit OTP"/></div>
            <button className="btn-primary" type="submit" disabled={loading}>{loading ? '⏳' : 'Verify & Login'}</button>
          </form>
        )}

        {view === 'login' && (
          <form onSubmit={handleLogin}>
            <div className="form-group"><label>Username</label><input type="text" value={username} onChange={e => setUsername(e.target.value)} placeholder="Enter your username"/></div>
            <div className="form-group">
              <label>Password</label>
              <div style={{display:'flex', position:'relative'}}>
                <input type={showPassword ? "text" : "password"} value={password} onChange={e => setPassword(e.target.value)} style={{flex: 1}} placeholder="Enter your password"/>
                <span onClick={() => setShowPassword(!showPassword)} style={{position:'absolute', right:10, top:10, cursor:'pointer'}}>👁️</span>
              </div>
            </div>
            <button className="btn-primary" type="submit" disabled={loading}>{loading ? '⏳' : '🔑 Login'}</button>
            <p style={{ textAlign: 'center', fontSize: 12, marginTop: 14 }}>
              <span style={{ color: 'var(--accent-indigo)', cursor: 'pointer' }} onClick={() => setView('forgot')}>Forgot Password?</span>
            </p>
          </form>
        )}

        {view === 'forgot' && (
          <form onSubmit={handleForgot}>
            <div className="form-group"><label>Username</label><input type="text" value={username} onChange={e => setUsername(e.target.value)}/></div>
            <div className="form-group"><label>Registered Email</label><input type="email" value={email} onChange={e => setEmail(e.target.value)}/></div>
            <button className="btn-primary" type="submit" disabled={loading}>{loading ? '⏳' : 'Send Reset OTP'}</button>
            <p style={{ textAlign: 'center', fontSize: 12, marginTop: 14 }}><span style={{ color: 'var(--accent-indigo)', cursor: 'pointer' }} onClick={() => setView('login')}>Back to Login</span></p>
          </form>
        )}

        {view === 'reset' && (
          <form onSubmit={handleReset}>
            <div className="form-group"><label>OTP</label><input type="text" value={otp} onChange={e => setOtp(e.target.value)}/></div>
            <div className="form-group">
              <label>New Password</label>
              <div style={{display:'flex', position:'relative'}}>
                <input type={showPassword ? "text" : "password"} value={password} onChange={e => setPassword(e.target.value)} style={{flex: 1}}/>
                <span onClick={() => setShowPassword(!showPassword)} style={{position:'absolute', right:10, top:10, cursor:'pointer'}}>👁️</span>
              </div>
            </div>
            <div className="form-group">
              <label>Confirm New Password</label>
              <div style={{display:'flex', position:'relative'}}>
                <input type={showConfirm ? "text" : "password"} value={confirmPassword} onChange={e => setConfirmPassword(e.target.value)} style={{flex: 1}}/>
                <span onClick={() => setShowConfirm(!showConfirm)} style={{position:'absolute', right:10, top:10, cursor:'pointer'}}>👁️</span>
              </div>
            </div>
            <button className="btn-primary" type="submit" disabled={loading}>{loading ? '⏳' : 'Save New Password'}</button>
          </form>
        )}
      </div>
    </div>
  )
}
"""

auth_pattern = re.compile(r'// Auth Page \(Login \+ Register\).*?function ProfileTab', re.DOTALL)
content = auth_pattern.sub(auth_page_new + '\n// Profile Tab\nfunction ProfileTab', content)

# 2. Update role input to have an 'Add' button
role_input_new = """        <div className="form-group" style={{display: 'flex', gap: 8}}>
          <div style={{flex: 1}}>
            <input 
              type="text" 
              list="role-options"
              placeholder="Type a role and click Add" 
              value={roleInput}
              onChange={(e) => setRoleInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter') {
                  e.preventDefault();
                  if (roleInput.trim()) { toggleRole(roleInput.trim()); setRoleInput(''); }
                }
              }}
            />
            <datalist id="role-options">
              {ALL_ROLES.map(r => <option key={r} value={r} />)}
            </datalist>
          </div>
          <button className="btn-primary" style={{width: 'auto', padding: '0 16px', borderRadius: 8, height: '44px'}} onClick={() => { if(roleInput.trim()) { toggleRole(roleInput.trim()); setRoleInput(''); } }}>+ Add</button>
        </div>"""

role_pattern = re.compile(r'<div className="form-group">\s*<input\s*type="text"\s*list="role-options"[\s\S]*?</datalist>\s*</div>', re.DOTALL)
content = role_pattern.sub(role_input_new, content)

# 3. Inject Change Password functionality in ProfileTab
# We will inject a ChangePassword component before "Save Profile"
change_pwd_component = """
// Change Password Component
function ChangePassword({ userId }) {
  const [oldPassword, setOldPassword] = useState('')
  const [newPassword, setNewPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [msg, setMsg] = useState('')
  
  const submit = async () => {
    if (!oldPassword || !newPassword) return setMsg('Fill all fields')
    setLoading(true); setMsg('')
    try {
      const res = await fetch(`${API}/change-password/${userId}`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ old_password: oldPassword, new_password: newPassword, email: '', otp: '' })
      })
      const data = await res.json()
      setMsg(res.ok ? 'Password updated!' : data.detail)
    } catch(e) { setMsg('Error updating') }
    setLoading(false)
  }
  
  return (
    <div className="section-card" style={{marginTop: 20}}>
      <h3>🔒 Change Password</h3>
      <div className="form-group"><input type="password" placeholder="Current Password" value={oldPassword} onChange={e=>setOldPassword(e.target.value)} /></div>
      <div className="form-group"><input type="password" placeholder="New Password" value={newPassword} onChange={e=>setNewPassword(e.target.value)} /></div>
      <button className="btn-primary" onClick={submit} disabled={loading}>{loading ? '⏳' : 'Update Password'}</button>
      {msg && <p style={{fontSize: 12, color: 'var(--accent-indigo)', marginTop: 8}}>{msg}</p>}
    </div>
  )
}
"""

if "function ChangePassword" not in content:
    content = content.replace("function App() {", change_pwd_component + "\nfunction App() {")

# Add the ChangePassword component to ProfileTab UI
profile_tab_patch = """        </div>
      </div>

      <ChangePassword userId={userId} />

      <button className="btn-primary" onClick={saveProfile} disabled={saving}>"""
content = content.replace("""        </div>
      </div>

      <button className="btn-primary" onClick={saveProfile} disabled={saving}>""", profile_tab_patch)


with open(target, 'w', encoding='utf-8') as f:
    f.write(content)
print("Frontend updated successfully!")
