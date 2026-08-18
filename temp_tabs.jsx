// Saved Jobs Tab
function SavedJobsTab({ userId }) {
  const [savedJobs, setSavedJobs] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetch(`${API}/saved-jobs/${userId}`)
      .then(r => r.json())
      .then(data => {
        setSavedJobs(data || [])
        setLoading(false)
      })
      .catch(() => setLoading(false))
  }, [userId])

  const handleDelete = async (jobId) => {
    try {
      const res = await fetch(`${API}/saved-jobs/${userId}/${jobId}`, { method: 'DELETE' })
      if (res.ok) {
        setSavedJobs(savedJobs.filter(j => j.id !== jobId))
      }
    } catch (e) {
      console.log('Error deleting job', e)
    }
  }

  if (loading) return <div style={{ textAlign: 'center', padding: 40 }}>Loading saved jobs...</div>
  if (savedJobs.length === 0) return <div style={{ textAlign: 'center', padding: 40, color: '#6B7280' }}>No saved jobs yet.</div>

  return (
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: 16 }}>
      {savedJobs.map(job => (
        <div key={job.id} className="card" style={{ display: 'flex', flexDirection: 'column', padding: 16 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 8 }}>
            <h4 style={{ margin: 0, fontSize: 16, color: '#111827', flex: 1 }}>{job.title}</h4>
            <span style={{ background: '#E0E7FF', color: '#4338CA', padding: '4px 8px', borderRadius: 4, fontSize: 11, fontWeight: 600, marginLeft: 8 }}>
              {job.type}
            </span>
          </div>
          <p style={{ margin: '0 0 4px', fontSize: 14, color: '#4B5563', fontWeight: 500 }}>{job.company}</p>
          <p style={{ margin: '0 0 12px', fontSize: 13, color: '#6B7280', display: 'flex', alignItems: 'center', gap: 4 }}>
            <span>📍</span> {job.location}
          </p>
          <div style={{ marginTop: 'auto', display: 'flex', gap: 8 }}>
            <button onClick={() => window.open(job.link, '_system')} style={{
              flex: 1, background: 'var(--accent-indigo)', color: 'white', padding: '8px 0', borderRadius: 6, border: 'none', fontWeight: 600, fontSize: 13, cursor: 'pointer'
            }}>Apply</button>
            <button onClick={() => handleDelete(job.id)} style={{
              flex: 1, background: '#FEE2E2', color: '#B91C1C', padding: '8px 0', borderRadius: 6, border: 'none', fontWeight: 600, fontSize: 13, cursor: 'pointer'
            }}>Remove</button>
          </div>
        </div>
      ))}
    </div>
  )
}

// Interview Prep Tab
function InterviewPrepTab() {
  return (
    <div style={{ padding: '0 0 20px 0' }}>
      <h3 style={{ margin: '0 0 16px', fontSize: 18, color: '#111827' }}>Common Interview Questions</h3>
      
      <div style={{ background: '#FFFBEB', padding: 16, borderRadius: 8, marginBottom: 20, border: '1px solid #FDE68A' }}>
        <h4 style={{ margin: '0 0 12px', color: '#B45309', fontSize: 16 }}>HR / General Questions</h4>
        {GENERAL_INTERVIEW_DATA.map((item, idx) => (
          <div key={idx} style={{ marginBottom: 16, paddingBottom: 16, borderBottom: idx !== GENERAL_INTERVIEW_DATA.length - 1 ? '1px solid #FDE68A' : 'none' }}>
            <p style={{ margin: '0 0 8px', fontWeight: 600, color: '#92400E', fontSize: 14 }}>Q: {item.q}</p>
            <p style={{ margin: 0, fontSize: 13, color: '#B45309', lineHeight: 1.5 }}>A: {item.a}</p>
          </div>
        ))}
      </div>

      {Object.entries(INTERVIEW_DATA).map(([role, qaList]) => (
        <div key={role} style={{ background: 'white', padding: 16, borderRadius: 8, marginBottom: 20, boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
          <h4 style={{ margin: '0 0 12px', color: '#111827', fontSize: 16 }}>{role}</h4>
          {qaList.map((item, idx) => (
            <div key={idx} style={{ marginBottom: 16, paddingBottom: 16, borderBottom: idx !== qaList.length - 1 ? '1px solid #E5E7EB' : 'none' }}>
              <p style={{ margin: '0 0 8px', fontWeight: 600, color: '#374151', fontSize: 14 }}>Q: {item.q}</p>
              <p style={{ margin: 0, fontSize: 13, color: '#6B7280', lineHeight: 1.5 }}>A: {item.a}</p>
            </div>
          ))}
        </div>
      ))}
    </div>
  )
}
