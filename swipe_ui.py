import os

with open('frontend/src/App.jsx', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace JobHistoryTab to be a Tinder-style swiper
old_job_tab_start = "function JobHistoryTab({ userId }) {"
old_job_tab_end = "function SavedJobsTab({ userId, toast }) {"

start_idx = content.find(old_job_tab_start)
end_idx = content.find(old_job_tab_end)

if start_idx != -1 and end_idx != -1:
    new_job_tab = """function JobHistoryTab({ userId }) {
  const [jobs, setJobs] = useState([])
  const [currentIndex, setCurrentIndex] = useState(0)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetch(`${API}/job-history/${userId}`).then(r => r.json()).then(data => {
      setJobs(data)
      setLoading(false)
    }).catch(() => setLoading(false))
  }, [userId])

  const handleSwipe = (direction) => {
    // If direction is right, we should technically save it. For now we just move to next.
    if (direction === 'right') {
      const job = jobs[currentIndex];
      fetch(`${API}/save-job`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ user_id: userId, job_title: job.title || job.company, job_url: job.link || '#', company: job.company })
      }).catch(()=>{})
    }
    setCurrentIndex(prev => prev + 1)
  }

  if (loading) return <div style={{ textAlign: 'center', padding: 40 }}><span className="spinner"></span></div>
  if (currentIndex >= jobs.length) return <div className="no-more-cards">No more jobs today! 🚀<br/><br/><span style={{fontSize: 14}}>Come back tomorrow for fresh recommendations.</span></div>

  const job = jobs[currentIndex]

  return (
    <div className="swipe-container">
      <div className="swipe-card">
        <div className="card-header">
          <h3>{job.title || job.company}</h3>
          <div className="card-company">{job.company || 'Unknown Company'}</div>
        </div>
        
        <div className="card-details">
          <p><strong>Status:</strong> {job.status}</p>
          <p><strong>Applied via:</strong> {job.applied_via || 'Direct'}</p>
          <p><strong>Date:</strong> {new Date(job.timestamp).toLocaleDateString()}</p>
          {job.link && <p style={{marginTop: 10}}><a href={job.link} target="_blank" rel="noreferrer" style={{color: 'var(--accent-indigo)'}}>View Job Post ➔</a></p>}
        </div>

        <div className="swipe-actions">
          <button className="btn-pass" onClick={() => handleSwipe('left')} title="Pass">✕</button>
          <button className="btn-save" onClick={() => handleSwipe('right')} title="Save & Apply">💚</button>
        </div>
      </div>
    </div>
  )
}

"""
    content = content[:start_idx] + new_job_tab + content[end_idx:]
    with open('frontend/src/App.jsx', 'w', encoding='utf-8') as f:
        f.write(content)
    print("JobHistoryTab swapped to Swipe UI")
