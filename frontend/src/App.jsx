import { useState, useEffect, useRef } from 'react'
import { ALL_ROLES } from './roles'

const API = "https://api.hirehuntt.in/api"

const QUALIFICATIONS = [
  'B.Tech', 'M.Tech', 'BCA', 'MCA', 'B.Sc', 'M.Sc',
  'MBA', 'BBA', 'B.E', 'M.E', 'Ph.D', 'Diploma', 'Other'
]

const EXPERIENCE_LEVELS = [
  'Fresher (0-1 yr)', '1-3 years', '3-5 years',
  '5-8 years', '8-12 years', '12+ years'
]

const JOB_LEVELS = [
  'Entry Level', 'Mid Level', 'Senior / Professional',
  'Internship', 'Contract', 'Any Level'
]

// Toast notification component
function Toast({ message, visible }) {
  return <div className={`toast ${visible ? 'visible' : ''}`}>{message}</div>
}

// Auth Page (Login, Register, Forgot Password, Verification)
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

// Profile Tab
function ProfileTab({ userId, toast }) {
  const [name, setName] = useState('')
  const [qualification, setQualification] = useState('')
  const [roles, setRoles] = useState([])
  const [roleInput, setRoleInput] = useState('')
  const [skills, setSkills] = useState('')
  const [experience, setExperience] = useState('')
  const [jobLevel, setJobLevel] = useState('Any Level')
  const [location, setLocation] = useState('India')
  const [receiverEmail, setReceiverEmail] = useState('')
  const [dsUploaded, setDsUploaded] = useState(false)
  const [daUploaded, setDaUploaded] = useState(false)
  const [saving, setSaving] = useState(false)
  const [running, setRunning] = useState(false)

  const dsRef = useRef(null)
  const daRef = useRef(null)

  useEffect(() => {
    fetch(`${API}/profile/${userId}`).then(r => r.json()).then(data => {
      setName(data.name || '')
      setQualification(data.qualification || '')
      setRoles(data.searching_roles || [])
      setSkills(data.skills || '')
      setExperience(data.experience || '')
      setJobLevel(data.job_level || 'Any Level')
      setLocation(data.location || 'India')
      setReceiverEmail(data.receiver_email || '')
      setDsUploaded(data.ds_resume_uploaded)
      setDaUploaded(data.da_resume_uploaded)
    }).catch(() => {})
  }, [userId])

  const toggleRole = (role) => {
    setRoles(prev => prev.includes(role) ? prev.filter(r => r !== role) : [...prev, role])
  }

  const handleAddRole = (e) => {
    if (e.key === 'Enter' && roleInput.trim()) {
      e.preventDefault()
      const newRole = roleInput.trim()
      if (!roles.includes(newRole)) {
        setRoles([...roles, newRole])
      }
      setRoleInput('')
    }
  }

  const saveProfile = async () => {
    setSaving(true)
    try {
      const res = await fetch(`${API}/profile/${userId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name, qualification, searching_roles: roles,
          experience, job_level: jobLevel, receiver_email: receiverEmail, skills, location
        })
      })
      if (res.ok) toast('Profile saved successfully! ✅')
      else toast('Failed to save profile ❌')
    } catch { toast('Network error') }
    setSaving(false)
  }

  const uploadResume = async (type, file) => {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('profile_type', type)
    try {
      const res = await fetch(`${API}/upload-resume/${userId}`, { method: 'POST', body: formData })
      if (res.ok) {
        if (type === 'ds') setDsUploaded(true)
        else setDaUploaded(true)
        toast(`${type.toUpperCase()} Resume uploaded! ✅`)
      } else toast('Upload failed ❌')
    } catch { toast('Network error') }
  }

  const runMatching = async () => {
    setRunning(true)
    try {
      const res = await fetch(`${API}/run-matching/${userId}`, { method: 'POST' })
      const data = await res.json()
      if (res.ok) {
        toast('Pipeline started... You will receive an email shortly 📧')
      } else if (res.status === 429) {
        toast('✉️ Email already sent today! Check your inbox.')
      } else if (res.status === 403) {
        toast('⚠️ Subscription expired. Please pay to continue.')
      } else {
        toast(data.detail || 'Error starting pipeline')
      }
    } catch { toast('Network error') }
    setRunning(false)
  }

  return (
    <>
      <div className="section-card">
        <h3>👤 Personal Details</h3>
        <div className="form-group">
          <label>Full Name</label>
          <input type="text" placeholder="e.g. Chetan Patil" value={name}
            onChange={(e) => setName(e.target.value)} />
        </div>
        <div className="form-group">
          <label>Qualification</label>
          <select value={qualification} onChange={(e) => setQualification(e.target.value)}>
            <option value="">Select Qualification</option>
            {QUALIFICATIONS.map(q => <option key={q} value={q}>{q}</option>)}
          </select>
        </div>
        <div className="form-group">
          <label>Experience Level</label>
          <select value={experience} onChange={(e) => setExperience(e.target.value)}>
            <option value="">Select Experience</option>
            {EXPERIENCE_LEVELS.map(e => <option key={e} value={e}>{e}</option>)}
          </select>
        </div>
        <div className="form-group">
          <label>Job Type / Level</label>
          <select value={jobLevel} onChange={(e) => setJobLevel(e.target.value)}>
            {JOB_LEVELS.map(l => <option key={l} value={l}>{l}</option>)}
          </select>
        </div>
        <div className="form-group">
          <label>Location (Country)</label>
          <select value={location} onChange={(e) => setLocation(e.target.value)}>
            <option value="India">India</option>
            <option value="USA">USA</option>
            <option value="UK">UK</option>
            <option value="Canada">Canada</option>
            <option value="Australia">Australia</option>
            <option value="Remote">Remote</option>
          </select>
        </div>
      </div>

      <div className="section-card">
        <h3>🔍 Job Roles</h3>
        <p style={{ fontSize: '12px', color: 'var(--text-muted)', marginBottom: '12px' }}>
          Select from suggestions or type your own and press Enter.
        </p>
                <div className="form-group" style={{display: 'flex', gap: 8}}>
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
        </div>
        <div className="role-chips">
          {roles.map(role => (
            <div key={role} className="role-chip selected" onClick={() => toggleRole(role)}>
              {role} ✕
            </div>
          ))}
        </div>
      </div>

      <div className="section-card">
        <h3>💡 Keywords & Skills (Optional)</h3>
        <p style={{ fontSize: '12px', color: 'var(--text-muted)', marginBottom: '12px' }}>
          Enter key tools, skills, or keywords (e.g., Python, React, AWS) to improve matching accuracy.
        </p>
        <div className="form-group">
          <input 
            type="text" 
            placeholder="e.g. Python, SQL, React, AWS" 
            value={skills}
            onChange={(e) => setSkills(e.target.value)}
          />
        </div>
      </div>

      <div className="section-card">
        <h3>📄 Upload Resume</h3>
        <div className={`upload-box ${dsUploaded ? 'uploaded' : ''}`}
          onClick={() => dsRef.current?.click()}>
          <div className="upload-icon">{dsUploaded ? '✅' : '📤'}</div>
          <div className="upload-label">Your Resume (PDF)</div>
          {!dsUploaded && <div className="upload-hint">Click to upload or drag & drop</div>}
          {dsUploaded && <div className="upload-status">Uploaded successfully</div>}
          <input ref={dsRef} type="file" accept=".pdf" style={{ display: 'none' }}
            onChange={(e) => e.target.files[0] && uploadResume('ds', e.target.files[0])} />
        </div>
        
        {dsUploaded && (
          <button 
            className="btn-secondary" 
            style={{marginTop: '15px', width: '100%', padding: '12px'}}
            onClick={() => dsRef.current?.click()}
          >
            🔄 Resubmit / Upload Another Resume
          </button>
        )}
      </div>

      <div className="section-card">
        <h3>📧 Receiver Email</h3>
        <div className="form-group">
          <label>Email Address</label>
          <input type="email" placeholder="your_email@gmail.com" value={receiverEmail}
            onChange={(e) => setReceiverEmail(e.target.value)} />
        </div>
      </div>

      <ChangePassword userId={userId} />

      <button className="btn-primary" onClick={saveProfile} disabled={saving}>
        {saving && <span className="spinner"></span>}
        Save Profile
      </button>
      <button className="btn-run" onClick={runMatching} disabled={running}>
        {running && <span className="spinner"></span>}
        🚀 Run Job Match & Email Me
      </button>
      <p style={{ fontSize: 11, color: 'var(--text-muted)', textAlign: 'center', marginTop: 6 }}>
        ℹ️ You can run this once per day. Daily auto-email goes out at 8:00 AM.
      </p>
    </>
  )
}

// Logs Tab
function LogsTab({ userId }) {
  const [logs, setLogs] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetch(`${API}/logs/${userId}`).then(r => r.json()).then(data => {
      setLogs(data)
      setLoading(false)
    }).catch(() => setLoading(false))
  }, [userId])

  const refresh = () => {
    setLoading(true)
    fetch(`${API}/logs/${userId}`).then(r => r.json()).then(data => {
      setLogs(data)
      setLoading(false)
    }).catch(() => setLoading(false))
  }

  if (loading) {
    return (
      <div className="empty-state">
        <div className="spinner" style={{ width: 24, height: 24, borderWidth: 3 }}></div>
        <p style={{ marginTop: 12 }}>Loading logs...</p>
      </div>
    )
  }

  return (
    <>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
        <h3 style={{ fontFamily: 'var(--font-heading)', fontSize: 16, fontWeight: 600 }}>📬 Email History</h3>
        <button className="btn-secondary" style={{ width: 'auto', padding: '8px 14px', fontSize: 12 }} onClick={refresh}>
          Refresh
        </button>
      </div>

      {logs.length === 0 ? (
        <div className="empty-state">
          <div className="empty-icon">📭</div>
          <p>No emails sent yet.<br />Go to Profile tab and click "Run Job Match".</p>
        </div>
      ) : (
        logs.map(log => (
          <div className="log-card" key={log.id}>
            <div className="log-header">
              <span className="log-date">📅 {log.timestamp}</span>
              <span className={`log-status ${log.status}`}>{log.status}</span>
            </div>
            <div className="log-count">
              {log.matched_count} <span>companies matched</span>
            </div>
            <div className="log-companies">
              {log.companies.length > 0 ? log.companies.join(', ') : 'No companies'}
            </div>
          </div>
        ))
      )}
    </>
  )
}

// Feedback Tab
function FeedbackTab({ userId, toast }) {
  const [reviewText, setReviewText] = useState('')
  const [rating, setRating] = useState(5)
  const [submitting, setSubmitting] = useState(false)
  const [submitted, setSubmitted] = useState(false)

  const handleSubmit = async () => {
    if (!reviewText.trim()) {
      toast('Please write your review ✍️')
      return
    }
    setSubmitting(true)
    try {
      const res = await fetch(`${API}/review/${userId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ review_text: reviewText.trim(), rating })
      })
      if (res.ok) {
        setSubmitted(true)
        toast('Review submitted! Will be visible after admin approval ✅')
      } else {
        toast('Failed to submit review ❌')
      }
    } catch { toast('Network error') }
    setSubmitting(false)
  }

  if (submitted) {
    return (
      <div className="empty-state">
        <div style={{ fontSize: 48, marginBottom: 12 }}>🎉</div>
        <p>Thank you for your feedback!<br />Your review will be visible once approved by admin.</p>
      </div>
    )
  }

  return (
    <div className="section-card">
      <h3>💬 Share Your Feedback</h3>
      <p style={{ fontSize: 12, color: 'var(--text-muted)', marginBottom: 16 }}>
        Your review helps us improve and helps others decide!
      </p>
      
      <div className="form-group">
        <label>Rating</label>
        <div className="star-rating">
          {[1, 2, 3, 4, 5].map(s => (
            <span key={s} className={`star ${s <= rating ? 'active' : ''}`} onClick={() => setRating(s)}>
              {s <= rating ? '★' : '☆'}
            </span>
          ))}
        </div>
      </div>
      
      <div className="form-group">
        <label>Your Review</label>
        <textarea
          placeholder="Share your experience with Hire Huntt..."
          value={reviewText}
          onChange={(e) => setReviewText(e.target.value)}
          rows={4}
          style={{ resize: 'vertical', minHeight: 80 }}
        />
      </div>
      
      <button className="btn-primary" onClick={handleSubmit} disabled={submitting}>
        {submitting && <span className="spinner"></span>}
        Submit Review
      </button>
    </div>
  )
}

// Approved Reviews Carousel (shown at bottom)
function ReviewsCarousel() {
  const [reviews, setReviews] = useState([])
  const [currentIndex, setCurrentIndex] = useState(0)

  useEffect(() => {
    fetch(`${API}/reviews/approved`).then(r => r.json()).then(data => {
      setReviews(data)
    }).catch(() => {})
  }, [])

  useEffect(() => {
    if (reviews.length > 1) {
      const interval = setInterval(() => {
        setCurrentIndex(prev => (prev + 1) % reviews.length)
      }, 5000)
      return () => clearInterval(interval)
    }
  }, [reviews.length])

  if (reviews.length === 0) return null

  const review = reviews[currentIndex]
  return (
    <div className="reviews-carousel">
      <div className="review-card-carousel">
        <div className="review-stars">{'★'.repeat(review.rating)}{'☆'.repeat(5 - review.rating)}</div>
        <p className="review-text">"{review.review_text}"</p>
        <div className="review-author">— {review.username} • {review.created_at}</div>
      </div>
      {reviews.length > 1 && (
        <div className="review-dots">
          {reviews.map((_, i) => (
            <span key={i} className={`dot ${i === currentIndex ? 'active' : ''}`} onClick={() => setCurrentIndex(i)} />
          ))}
        </div>
      )}
    </div>
  )
}

// Admin Tab (with Reviews management)
function AdminTab({ toast }) {
  const [users, setUsers] = useState([])
  const [reviews, setReviews] = useState([])
  const [loading, setLoading] = useState(true)
  const [activeSection, setActiveSection] = useState('users')

  const fetchUsers = () => {
    setLoading(true)
    fetch(`${API}/admin/users`)
      .then(r => r.json())
      .then(data => {
        setUsers(data)
        setLoading(false)
      })
      .catch(() => {
        toast('Failed to load users ❌')
        setLoading(false)
      })
  }

  const fetchReviews = () => {
    fetch(`${API}/admin/reviews`)
      .then(r => r.json())
      .then(data => setReviews(data))
      .catch(() => {})
  }

  useEffect(() => {
    fetchUsers()
    fetchReviews()
  }, [])

  const handleApprove = async (userId) => {
    try {
      const res = await fetch(`${API}/admin/approve/${userId}`, { method: 'POST' })
      if (res.ok) {
        toast(`User approved successfully! ✅`)
        fetchUsers()
      } else {
        toast('Failed to approve user ❌')
      }
    } catch {
      toast('Network error')
    }
  }

  const handleApproveReview = async (reviewId) => {
    try {
      const res = await fetch(`${API}/admin/review/approve/${reviewId}`, { method: 'POST' })
      if (res.ok) {
        toast('Review approved! ✅')
        fetchReviews()
      }
    } catch { toast('Network error') }
  }

  const handleRejectReview = async (reviewId) => {
    try {
      const res = await fetch(`${API}/admin/review/reject/${reviewId}`, { method: 'POST' })
      if (res.ok) {
        toast('Review rejected ❌')
        fetchReviews()
      }
    } catch { toast('Network error') }
  }

  if (loading) {
    return (
      <div className="empty-state">
        <div className="spinner" style={{ width: 24, height: 24, borderWidth: 3 }}></div>
        <p style={{ marginTop: 12 }}>Loading...</p>
      </div>
    )
  }

  return (
    <>
      {/* Sub-navigation */}
      <div style={{ display: 'flex', gap: 8, marginBottom: 16 }}>
        <button 
          className={`btn-secondary ${activeSection === 'users' ? 'active-sub' : ''}`}
          style={{ width: 'auto', padding: '8px 16px', fontSize: 12 }}
          onClick={() => setActiveSection('users')}>
          👥 Users
        </button>
        <button 
          className={`btn-secondary ${activeSection === 'reviews' ? 'active-sub' : ''}`}
          style={{ width: 'auto', padding: '8px 16px', fontSize: 12 }}
          onClick={() => setActiveSection('reviews')}>
          💬 Reviews ({reviews.filter(r => !r.is_approved).length})
        </button>
      </div>

      {activeSection === 'users' && (
        <>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
            <h3 style={{ fontFamily: 'var(--font-heading)', fontSize: 16, fontWeight: 600 }}>🛡️ User Management</h3>
            <button className="btn-secondary" style={{ width: 'auto', padding: '8px 14px', fontSize: 12 }} onClick={fetchUsers}>
              Refresh
            </button>
          </div>
          <div className="admin-table-container">
            <table className="admin-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Username</th>
                  <th>Name</th>
                  <th>Plan</th>
                  <th>Status</th>
                  <th>Screenshot</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {users.map(u => (
                  <tr key={u.user_id}>
                    <td>{u.user_id}</td>
                    <td>{u.username}</td>
                    <td>{u.name || '-'}</td>
                    <td>{u.plan_type}</td>
                    <td>
                      <span className={`status-badge ${u.payment_status}`}>
                        {u.payment_status}
                      </span>
                    </td>
                    <td>
                      {u.payment_screenshot ? (
                        <a href={`${API.replace('/api', '')}/uploads/${u.payment_screenshot}`} target="_blank" rel="noreferrer">
                          View
                        </a>
                      ) : '-'}
                    </td>
                    <td>
                      {u.payment_status === 'pending_approval' || (u.plan_type !== 'premium' && u.plan_type !== 'admin') ? (
                        <button className="btn-approve" onClick={() => handleApprove(u.user_id)}>
                          Approve
                        </button>
                      ) : (
                        '-'
                      )}
                    </td>
                  </tr>
                ))}
                {users.length === 0 && (
                  <tr>
                    <td colSpan="7" style={{ textAlign: 'center', color: 'var(--text-muted)' }}>
                      No users found.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </>
      )}

      {activeSection === 'reviews' && (
        <>
          <h3 style={{ fontFamily: 'var(--font-heading)', fontSize: 16, fontWeight: 600, marginBottom: 16 }}>💬 Review Management</h3>
          {reviews.length === 0 ? (
            <div className="empty-state">
              <p>No reviews submitted yet.</p>
            </div>
          ) : (
            reviews.map(r => (
              <div className="review-admin-card" key={r.id}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div>
                    <strong>{r.username}</strong>
                    <span style={{ marginLeft: 8, color: 'gold' }}>{'★'.repeat(r.rating)}</span>
                    <span style={{ fontSize: 11, color: 'var(--text-muted)', marginLeft: 8 }}>{r.created_at}</span>
                  </div>
                  <span className={`status-badge ${r.is_approved ? 'paid' : 'unpaid'}`}>
                    {r.is_approved ? 'Approved' : 'Pending'}
                  </span>
                </div>
                <p style={{ fontSize: 13, color: 'var(--text-secondary)', margin: '8px 0' }}>"{r.review_text}"</p>
                {!r.is_approved && (
                  <div style={{ display: 'flex', gap: 8 }}>
                    <button className="btn-approve" onClick={() => handleApproveReview(r.id)}>✅ Approve</button>
                    <button className="btn-approve" style={{ background: '#ef4444' }} onClick={() => handleRejectReview(r.id)}>❌ Reject</button>
                  </div>
                )}
              </div>
            ))
          )}
        </>
      )}
    </>
  )
}

// Terms & Conditions Page
function TermsPage({ onAccept }) {
  return (
    <div className="auth-wrapper">
      <div className="auth-logo">
        <div style={{display:"flex", alignItems:"center", justifyContent:"center", gap: 10}}><img src="/h_logo.jpg" alt="Logo" style={{height: 32, borderRadius: 6}}/> Hire Huntt</div>
        <span>Terms of Service</span>
      </div>
      <div className="terms-card">
        <h2>📜 Terms & Conditions</h2>
        <p className="terms-intro">Please read and accept our terms before proceeding.</p>
        <div className="terms-body">
          <div className="terms-item">
            <span className="terms-icon">🔐</span>
            <div>
              <strong>Account Security</strong>
              <p>Your account credentials are personal and must not be shared. You are responsible for maintaining their confidentiality.</p>
            </div>
          </div>
          <div className="terms-item">
            <span className="terms-icon">⏰</span>
            <div>
              <strong>48-Hour Session Policy</strong>
              <p>If you do not access the app for more than <strong>48 hours</strong>, you will be required to log in again for security purposes.</p>
            </div>
          </div>
          <div className="terms-item">
            <span className="terms-icon">🗑️</span>
            <div>
              <strong>30-Day Inactivity Deletion</strong>
              <p>Accounts inactive for more than <strong>30 days</strong> will be <strong>automatically and permanently deleted</strong>, along with all associated data.</p>
            </div>
          </div>
          <div className="terms-item">
            <span className="terms-icon">💳</span>
            <div>
              <strong>Payment Policy</strong>
              <p>₹199 for 3 months. You can start with a 3-day free trial. Payments are non-refundable once approved.</p>
            </div>
          </div>
          <div className="terms-item">
            <span className="terms-icon">📧</span>
            <div>
              <strong>Daily Job Alerts</strong>
              <p>Approved users receive a daily email at <strong>8:00 AM</strong> with fresh, non-repeated job openings.</p>
            </div>
          </div>
          <div className="terms-item">
            <span className="terms-icon">🔒</span>
            <div>
              <strong>Privacy</strong>
              <p>Your data is stored securely and is never shared with third parties.</p>
            </div>
          </div>
        </div>
        <button className="btn-primary" onClick={onAccept} style={{ marginTop: 8 }}>
          ✔️ I Accept — Continue
        </button>
      </div>
    </div>
  )
}

// Plan Choice Page (after registration - 3 day trial or ₹199/3months)
function PlanChoicePage({ userId, onTrialChosen, onPayChosen, onBack }) {
  const [loading, setLoading] = useState(false)

  const handleTrial = async () => {
    setLoading(true)
    try {
      const res = await fetch(`${API}/choose-plan/${userId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ plan: 'trial' })
      })
      if (res.ok) {
        onTrialChosen()
      }
    } catch {}
    setLoading(false)
  }

  return (
    <div className="auth-wrapper">
      <div className="auth-logo">
        <div style={{display:"flex", alignItems:"center", justifyContent:"center", gap: 10}}><img src="/h_logo.jpg" alt="Logo" style={{height: 32, borderRadius: 6}}/> Hire Huntt</div>
        <span>Choose Your Plan</span>
      </div>
      <div className="plan-choice-card">
        <h2>🚀 Get Started</h2>
        <p style={{ color: 'var(--text-secondary)', fontSize: 13, margin: '8px 0 24px', textAlign: 'center' }}>
          Choose how you want to begin your job hunting journey.
        </p>

        <div className="plan-options">
          {/* Free Trial */}
          <div className="plan-option trial" onClick={handleTrial}>
            <div className="plan-badge">FREE</div>
            <div className="plan-title">3-Day Free Trial</div>
            <div className="plan-desc">Try all features for 3 days. No payment needed.</div>
            <div className="plan-price">₹0</div>
            <button className="btn-secondary" disabled={loading}>
              {loading ? <span className="spinner"></span> : 'Start Free Trial'}
            </button>
          </div>

          {/* Premium */}
          <div className="plan-option premium" onClick={onPayChosen}>
            <div className="plan-badge hot">BEST VALUE</div>
            <div className="plan-title">Premium - 3 Months</div>
            <div className="plan-desc">Full access for 90 days. Daily job alerts included.</div>
            <div className="plan-price">₹199</div>
            <button className="btn-primary" style={{ marginTop: 0 }}>Pay ₹199</button>
          </div>
        </div>

        <button className="btn-back" onClick={onBack}>← Back to Login</button>
      </div>
    </div>
  )
}

// Payment Wall Page
function PaymentPage({ userId, onPaymentSubmitted, onBack }) {
  const [file, setFile] = useState(null)
  const [loading, setLoading] = useState(false)
  const [submitted, setSubmitted] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async () => {
    if (!file) {
      setError('Please upload a screenshot of your payment.')
      return
    }
    setLoading(true)
    setError('')
    try {
      const formData = new FormData()
      formData.append('file', file)
      
      const res = await fetch(`${API}/payment/submit/${userId}`, {
        method: 'POST',
        body: formData
      })
      if (res.ok) {
        setSubmitted(true)
        if (onPaymentSubmitted) onPaymentSubmitted()
      } else {
        setError('Submission failed. Please try again.')
      }
    } catch {
      setError('Network error.')
    }
    setLoading(false)
  }

  if (submitted) {
    return (
      <div className="auth-wrapper">
        <div className="payment-card">
          <div style={{ fontSize: 56, marginBottom: 16 }}>✅</div>
          <h2>Payment Submitted!</h2>
          <p style={{ color: 'var(--text-secondary)', fontSize: 14, marginTop: 8, lineHeight: 1.6 }}>
            Your payment details have been sent for verification.<br />
            <strong>You will get access once the admin approves your payment.</strong><br />
            This usually takes a few hours.
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="auth-wrapper">
      <div className="auth-logo">
        <div style={{display:"flex", alignItems:"center", justifyContent:"center", gap: 10}}><img src="/h_logo.jpg" alt="Logo" style={{height: 32, borderRadius: 6}}/> Hire Huntt</div>
        <span>Activate Your Account</span>
      </div>
      <div className="payment-card">
        <h2 style={{ textAlign: 'center', marginBottom: 4 }}>💳 Activate Premium</h2>
        <p style={{ color: 'var(--text-secondary)', fontSize: 13, margin: '0 0 20px', textAlign: 'center' }}>
          Pay ₹199 for 3 months of full access
        </p>

        {/* Step 1 - QR */}
        <div style={{ background: 'rgba(99,102,241,0.08)', border: '1px solid rgba(99,102,241,0.2)', borderRadius: 12, padding: 16, marginBottom: 16 }}>
          <div style={{ fontSize: 13, fontWeight: 700, color: 'var(--accent-indigo)', marginBottom: 12 }}>Step 1 — Scan & Pay via UPI</div>
          <div className="qr-section">
            <div className="qr-box">
              <img src="/payment_qr.jpg" alt="UPI Payment QR Code" />
            </div>
            <div className="qr-details">
              <div className="qr-detail-row">
                <span>💵 Amount</span>
                <strong style={{ color: '#10b981' }}>₹199</strong>
              </div>
              <div className="qr-detail-row">
                <span>📅 Access</span>
                <strong>90 Days</strong>
              </div>
              <div className="qr-detail-row">
                <span>📲 UPI Apps</span>
                <strong style={{ fontSize: 11 }}>PhonePe, GPay, Paytm, BHIM</strong>
              </div>
              <div style={{ marginTop: 8, fontSize: 11, color: 'var(--text-muted)', background: 'rgba(0,0,0,0.15)', padding: '6px 10px', borderRadius: 6 }}>
                ℹ️ Scan with any UPI app. Amount: ₹199
              </div>
            </div>
          </div>
        </div>

        {/* Step 2 - Screenshot */}
        <div style={{ background: 'rgba(16,185,129,0.08)', border: '1px solid rgba(16,185,129,0.2)', borderRadius: 12, padding: 16, marginBottom: 16 }}>
          <div style={{ fontSize: 13, fontWeight: 700, color: '#10b981', marginBottom: 12 }}>Step 2 — Upload Payment Screenshot</div>
          <div className="form-group" style={{ marginBottom: 0 }}>
            <input
              type="file"
              accept="image/*"
              onChange={(e) => setFile(e.target.files[0])}
            />
            <p style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 6 }}>
              📌 Ensure date, time, amount (₹199) and name are clearly visible in the screenshot.
            </p>
          </div>
          {file && <p style={{ fontSize: 12, color: '#10b981', marginTop: 6 }}>✅ Screenshot selected: {file.name}</p>}
        </div>

        {error && <p style={{ color: '#ef4444', fontSize: 12, marginBottom: 10, textAlign: 'center' }}>{error}</p>}

        <button className="btn-primary" onClick={handleSubmit} disabled={loading}>
          {loading && <span className="spinner"></span>}
          🚀 Submit & Get Approved
        </button>

        <button className="btn-back" onClick={onBack} style={{ marginTop: 10 }}>← Back</button>

        <div style={{ marginTop: 14, fontSize: 11, color: 'var(--text-muted)', textAlign: 'center', background: 'rgba(255,0,0,0.05)', padding: 10, borderRadius: 8, border: '1px solid rgba(255,0,0,0.1)' }}>
          ⏱️ Approval usually takes a few hours. For help, email: <strong>hirehuntt@gmail.com</strong>
        </div>
      </div>
    </div>
  )
}

// Change Password Component
function ChangePassword({ userId }) {
  const [oldPassword, setOldPassword] = useState('')
  const [newPassword, setNewPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [msg, setMsg] = useState('')
  const [isExpanded, setIsExpanded] = useState(false)
  
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
      if (res.ok) {
         setOldPassword('')
         setNewPassword('')
         setTimeout(() => setIsExpanded(false), 2000)
      }
    } catch(e) { setMsg('Error updating') }
    setLoading(false)
  }
  
  return (
    <div className="section-card" style={{marginTop: 20}}>
      <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center'}}>
         <h3 style={{margin: 0}}>🔒 Change Password</h3>
         <button className="btn-secondary" onClick={() => setIsExpanded(!isExpanded)} style={{padding: '6px 12px', fontSize: 12, borderRadius: 6, border: '1px solid #e5e7eb', background: '#f9fafb', cursor: 'pointer'}}>
            {isExpanded ? 'Cancel' : 'Change'}
         </button>
      </div>
      {isExpanded && (
         <div style={{marginTop: 15}}>
           <div className="form-group"><input type="password" placeholder="Current Password" value={oldPassword} onChange={e=>setOldPassword(e.target.value)} /></div>
           <div className="form-group"><input type="password" placeholder="New Password" value={newPassword} onChange={e=>setNewPassword(e.target.value)} /></div>
           <button className="btn-primary" onClick={submit} disabled={loading}>{loading ? '⏳' : 'Update Password'}</button>
           {msg && <p style={{fontSize: 12, color: 'var(--accent-indigo)', marginTop: 8}}>{msg}</p>}
         </div>
      )}
    </div>
  )
}

// Main App
export default function App() {
  const [userId, setUserId] = useState(null)
  const [username, setUsername] = useState('')
  const [isAdmin, setIsAdmin] = useState(false)
  const [paymentStatus, setPaymentStatus] = useState('unpaid')
  const [planType, setPlanType] = useState('unpaid')
  const [subStatus, setSubStatus] = useState(null) // subscription status from API
  const [activeTab, setActiveTab] = useState('profile')
  const [toastMsg, setToastMsg] = useState('')
  const [toastVisible, setToastVisible] = useState(false)
  const [termsAccepted, setTermsAccepted] = useState(false)
  const [currentScreen, setCurrentScreen] = useState('auto') // auto, plan_choice, payment
  const [footerModal, setFooterModal] = useState(null) // null, 'about', 'contact', 'terms'

  // On app load: check localStorage for saved session (48hr window)
  useEffect(() => {
    const savedTerms = localStorage.getItem('jh_terms_accepted')
    if (savedTerms === 'true') setTermsAccepted(true)

    const savedSession = localStorage.getItem('jh_session')
    if (savedSession) {
      try {
        const session = JSON.parse(savedSession)
        const loginTime = new Date(session.loginTime)
        const now = new Date()
        const hoursDiff = (now - loginTime) / (1000 * 60 * 60)
        if (hoursDiff < 48) {
          setUserId(session.userId)
          setUsername(session.username)
          setIsAdmin(session.isAdmin)
          setPaymentStatus(session.paymentStatus || 'unpaid')
          setPlanType(session.planType || 'unpaid')
          if (session.isAdmin) {
            setActiveTab('admin')
          }
        } else {
          localStorage.removeItem('jh_session')
        }
      } catch {
        localStorage.removeItem('jh_session')
      }
    }
  }, [])

  // Fetch subscription status when userId changes
  useEffect(() => {
    if (userId) {
      fetch(`${API}/subscription-status/${userId}`)
        .then(r => r.json())
        .then(data => {
          setSubStatus(data.status)
          setPlanType(data.plan_type)
          setPaymentStatus(data.payment_status)
        })
        .catch(() => {})
    }
  }, [userId])

  const showToast = (msg) => {
    setToastMsg(msg)
    setToastVisible(true)
    setTimeout(() => setToastVisible(false), 3500)
  }

  const handleLogin = async (id, name, is_admin = false) => {
    let pStatus = 'unpaid'
    let pType = 'unpaid'
    try {
      const res = await fetch(`${API}/profile/${id}`)
      if (res.ok) {
        const data = await res.json()
        pStatus = data.payment_status || 'unpaid'
        pType = data.plan_type || 'unpaid'
      }
    } catch {}

    setUserId(id)
    setUsername(name)
    setIsAdmin(is_admin)
    setPaymentStatus(pStatus)
    setPlanType(pType)
    setCurrentScreen('auto')
    if (is_admin) {
      setActiveTab('admin')
    } else {
      setActiveTab('profile')
    }

    localStorage.setItem('jh_session', JSON.stringify({
      userId: id,
      username: name,
      isAdmin: is_admin,
      paymentStatus: pStatus,
      planType: pType,
      loginTime: new Date().toISOString()
    }))
  }

  const handleLogout = () => {
    setUserId(null)
    setUsername('')
    setIsAdmin(false)
    setPaymentStatus('unpaid')
    setPlanType('unpaid')
    setSubStatus(null)
    setActiveTab('profile')
    setCurrentScreen('auto')
    localStorage.removeItem('jh_session')
  }

  const handleTermsAccept = () => {
    setTermsAccepted(true)
    localStorage.setItem('jh_terms_accepted', 'true')
  }

  // Determine if user has active access
  const hasAccess = isAdmin || planType === 'admin' || 
    subStatus === 'active' || subStatus === 'trial_active' || 
    (subStatus === null && (planType === 'premium' || planType === 'trial')) // fallback during loading

  let content;

  // Step 1: Show T&C first time
  if (!termsAccepted) {
    content = <TermsPage onAccept={handleTermsAccept} />
  }
  // Step 2: Show Login if not logged in
  else if (!userId) {
    content = <AuthPage onLogin={handleLogin} />
  }
  // If payment is pending approval, show pending screen
  else if (paymentStatus === 'pending_approval' && !isAdmin) {
    content = (
      <div className="auth-wrapper">
        <div className="payment-card">
          <div style={{ fontSize: 56, marginBottom: 16, textAlign: 'center' }}>⏳</div>
          <h2 style={{ textAlign: 'center' }}>Payment Pending Approval</h2>
          <p style={{ color: 'var(--text-secondary)', fontSize: 14, marginTop: 8, lineHeight: 1.6, textAlign: 'center' }}>
            Your payment screenshot has been submitted for verification.<br />
            <strong>You will get access once the admin approves your payment.</strong><br />
            This usually takes a few hours.
          </p>
          <button className="logout-btn" onClick={handleLogout} style={{ marginTop: 20, width: '100%' }}>Logout</button>
        </div>
      </div>
    )
  }
  // Step 3: If user explicitly chose plan_choice or payment screen
  else if (currentScreen === 'plan_choice' || (!hasAccess && currentScreen === 'auto')) {
    content = (
      <PlanChoicePage 
        userId={userId} 
        onTrialChosen={() => {
          setPlanType('trial')
          setPaymentStatus('trial_active')
          setSubStatus('trial_active')
          setCurrentScreen('auto')
          // Update session
          const session = JSON.parse(localStorage.getItem('jh_session') || '{}')
          session.paymentStatus = 'trial_active'
          session.planType = 'trial'
          localStorage.setItem('jh_session', JSON.stringify(session))
          showToast('🎉 3-day free trial activated!')
        }}
        onPayChosen={() => setCurrentScreen('payment')}
        onBack={handleLogout}
      />
    )
  }
  else if (currentScreen === 'payment') {
    content = (
      <PaymentPage 
        userId={userId} 
        onPaymentSubmitted={() => {
          setPaymentStatus('pending_approval')
          const session = JSON.parse(localStorage.getItem('jh_session') || '{}')
          session.paymentStatus = 'pending_approval'
          localStorage.setItem('jh_session', JSON.stringify(session))
        }}
        onBack={() => setCurrentScreen('plan_choice')}
      />
    )
  }
  else {
    // If subscription expired and not pending, show expired banner with pay option inside dashboard
    const isExpired = subStatus === 'expired' && paymentStatus !== 'pending_approval'
    content = (
      <>
        {/* Header */}
        <div className="header-bar">
          <div className="logo-sm" style={{display:"flex", alignItems:"center", gap: 8}}><img src="/h_logo.jpg" alt="Logo" style={{height: 24, borderRadius: 4}}/> Hire Huntt</div>
          <div className="user-badge">
            <div className="user-avatar">{username.charAt(0).toUpperCase()}</div>
            <span>{username}</span>
            <button className="logout-btn" onClick={handleLogout}>Logout</button>
          </div>
        </div>

        {/* Expired Banner */}
        {isExpired && (
          <div className="expired-banner">
            <span>⚠️ Your subscription has expired.</span>
            <button className="btn-approve" onClick={() => setCurrentScreen('plan_choice')}>
              Renew Now — ₹199/3mo
            </button>
          </div>
        )}

        {/* Navigation Tabs */}
        {!isAdmin ? (
          <div className="nav-tabs">
            <button className={`nav-tab ${activeTab === 'profile' ? 'active' : ''}`}
              onClick={() => setActiveTab('profile')}>
              ⚙️ Profile
            </button>
            <button className={`nav-tab ${activeTab === 'logs' ? 'active' : ''}`}
              onClick={() => setActiveTab('logs')}>
              📬 History
            </button>
            <button className={`nav-tab ${activeTab === 'feedback' ? 'active' : ''}`}
              onClick={() => setActiveTab('feedback')}>
              💬 Feedback
            </button>
          </div>
        ) : (
          <div className="nav-tabs">
            <button className="nav-tab active" style={{ cursor: 'default' }}>
              🛡️ Admin Dashboard
            </button>
          </div>
        )}

        {/* Tab Content */}
        {activeTab === 'profile' && <ProfileTab userId={userId} toast={showToast} />}
        {activeTab === 'logs' && <LogsTab userId={userId} />}
        {activeTab === 'feedback' && <FeedbackTab userId={userId} toast={showToast} />}
        {activeTab === 'admin' && isAdmin && <AdminTab toast={showToast} />}

        {/* Approved Reviews at bottom */}
        <ReviewsCarousel />
      </>
    )
  }

  return (
    <div className="app-container">
      {content}

      {/* Footer Links */}
      <footer className="app-footer">
        <button onClick={() => setFooterModal('about')}>About Us</button>
        <span>•</span>
        <button onClick={() => setFooterModal('contact')}>Contact Us</button>
        <span>•</span>
        <button onClick={() => setFooterModal('terms')}>Terms & Conditions</button>
      </footer>

      {/* Footer Modals */}
      {footerModal && (
        <div className="modal-backdrop" onClick={() => setFooterModal(null)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <button className="modal-close" onClick={() => setFooterModal(null)}>✕</button>
            {footerModal === 'about' && (
              <div>
                <h2>ℹ️ About Us</h2>
                <p><strong>Hire Huntt</strong> is an intelligent job search automation assistant designed to match your resume with the latest openings and send customized reports directly to your inbox.</p>
                <p>Our platform uses advanced analysis to ensure you only apply to roles that fit your skills, saving you time and boosting your success rate.</p>
              </div>
            )}
            {footerModal === 'contact' && (
              <div>
                <h2>✉️ Contact Us</h2>
                <p>We are here to support you! For any queries, payment issues, or technical assistance, feel free to write to us.</p>
                <div style={{ marginTop: 16, background: 'var(--bg-glass)', padding: 12, borderRadius: 8, border: '1px solid var(--border-glass)' }}>
                  <strong>Support Email:</strong> <a href="mailto:hirehuntt@gmail.com" style={{ color: 'var(--accent-indigo)', textDecoration: 'none' }}>hirehuntt@gmail.com</a>
                  <br />
                  <strong>Response Time:</strong> Within 24 Hours
                </div>
              </div>
            )}
            {footerModal === 'terms' && (
              <div>
                <h2>📜 Terms & Conditions</h2>
                <p>Welcome to Hire Huntt! By using our service, you agree to the following terms:</p>
                <ul style={{ paddingLeft: 20, marginTop: 8, display: 'flex', flexDirection: 'column', gap: 8 }}>
                  <li style={{ listStyleType: 'disc' }}><strong>Service:</strong> We provide daily job recommendations via email based on your profile selection and resume keywords.</li>
                  <li style={{ listStyleType: 'disc' }}><strong>Subscriptions:</strong> Premium services are billed at ₹199 for 90 days.</li>
                  <li style={{ listStyleType: 'disc' }}><strong>Refund Policy:</strong> Due to the digital nature of the service, all sales are final. Once your payment is approved and premium access is granted, <strong>payments are strictly non-refundable</strong>.</li>
                  <li style={{ listStyleType: 'disc' }}><strong>Inactivity:</strong> Accounts that remain inactive for more than 30 consecutive days will be permanently deleted to protect server space.</li>
                </ul>
              </div>
            )}
          </div>
        </div>
      )}

      <Toast message={toastMsg} visible={toastVisible} />
    </div>
  )
}
