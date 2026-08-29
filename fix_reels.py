import os

with open('frontend/src/App.jsx', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Create ReelsTab Component
reels_tab = """function ReelsTab() {
  const [shorts, setShorts] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetch(`${API}/shorts`)
      .then(r => r.json())
      .then(data => {
        if (data && data.length > 0) {
          setShorts(data)
        } else {
          setShorts([
            { id: "dQw4w9WgXcQ", title: "Job Interview Tips", author: "System" }
          ])
        }
        setLoading(false)
      })
      .catch(() => {
        setShorts([{ id: "dQw4w9WgXcQ", title: "Job Interview Tips", author: "System" }])
        setLoading(false)
      })
  }, [])

  if (loading) return <div style={{ textAlign: 'center', padding: 40 }}><span className="spinner"></span></div>

  return (
    <div className="reels-tab" style={{ padding: 0, margin: '-24px -16px', height: '100vh', overflowY: 'scroll', scrollSnapType: 'y mandatory', backgroundColor: 'black' }}>
      {shorts.map((video, i) => (
        <div key={i} style={{ height: '100vh', width: '100%', scrollSnapAlign: 'start', position: 'relative' }}>
          {/* Transparent Overlay to prevent clicking and redirecting to YouTube */}
          <div style={{position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', zIndex: 10}} 
               onClick={(e) => {
                 // We can implement play/pause here if we use YouTube API, but for now it just blocks clicks.
               }}>
          </div>
          <iframe 
            src={`https://www.youtube.com/embed/${video.id}?autoplay=1&mute=0&controls=0&modestbranding=1&rel=0&playsinline=1&loop=1&playlist=${video.id}`}
            style={{ width: '100%', height: '100%', border: 'none', pointerEvents: 'none' }}
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
            allowFullScreen
          ></iframe>
          <div style={{ position: 'absolute', bottom: 120, left: 16, right: 16, color: 'white', textShadow: '0 2px 4px rgba(0,0,0,0.8)', zIndex: 20 }}>
            <h3 style={{ margin: 0, fontSize: 18 }}>{video.author}</h3>
            <p style={{ margin: '4px 0 0', fontSize: 14 }}>{video.title}</p>
          </div>
        </div>
      ))}
    </div>
  )
}
"""

# Replace the current LearningTab (which has the shorts logic) back to the old static LearningTab
old_static_learning = """function LearningTab() {
  const resources = [
    { title: 'Top 50 React Interview Questions', type: 'Interview Prep', link: 'https://reactjs.org' },
    { title: 'How to write a killer Resume', type: 'Resume Tips', link: 'https://novoresume.com' },
    { title: 'Mastering JavaScript Closures', type: 'Coding', link: 'https://developer.mozilla.org' },
    { title: 'System Design Basics', type: 'Architecture', link: 'https://github.com/donnemartin/system-design-primer' }
  ];

  return (
    <div className="learning-tab">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
        <h2>Learning Hub 📚</h2>
      </div>
      <p style={{color: 'var(--text-secondary)', marginBottom: 20, fontSize: 14}}>Boost your skills to crack the next interview!</p>
      
      <div style={{ display: 'grid', gap: 16 }}>
        {resources.map((res, i) => (
          <div key={i} className="job-card" style={{ display: 'flex', flexDirection: 'column', gap: 8 }} onClick={() => window.open(res.link, '_blank')}>
            <span style={{ fontSize: 12, color: 'var(--accent-indigo)', fontWeight: 'bold' }}>{res.type}</span>
            <h3 style={{ margin: 0, fontSize: 16, color: 'var(--text-primary)' }}>{res.title}</h3>
            <span style={{ fontSize: 13, color: 'var(--text-muted)' }}>Read Article ➔</span>
          </div>
        ))}
      </div>
    </div>
  )
}
"""

# First, extract current LearningTab and replace with the old static one + ReelsTab
start_idx = content.find("function LearningTab() {")
end_idx = content.find("function SavedJobsTab", start_idx)

if start_idx != -1 and end_idx != -1:
    content = content[:start_idx] + old_static_learning + "\n" + reels_tab + "\n" + content[end_idx:]

# Update the Nav Tabs to include Reels instead of replacing it, or add as 5th tab
nav_start = content.find('<div className="nav-tabs">')
nav_end = content.find('</div>\n              ) : null}', nav_start)

if nav_start != -1 and nav_end != -1:
    new_tabs = """<div className="nav-tabs" style={{ display: 'flex', justifyContent: 'space-around', alignItems: 'center', width: '100%' }}>
                  <div className={`nav-tab ${activeTab === 'profile' ? 'active' : ''}`} onClick={() => setActiveTab('profile')}>
                    <span className="icon">👤</span>
                    Profile
                  </div>
                  <div className={`nav-tab ${activeTab === 'logs' ? 'active' : ''}`} onClick={() => setActiveTab('logs')}>
                    <span className="icon">💼</span>
                    Jobs
                  </div>
                  <div className={`nav-tab ${activeTab === 'reels' ? 'active' : ''}`} onClick={() => setActiveTab('reels')}>
                    <span className="icon">📱</span>
                    Reels
                  </div>
                  <div className={`nav-tab ${activeTab === 'saved' ? 'active' : ''}`} onClick={() => setActiveTab('saved')}>
                    <span className="icon">⭐</span>
                    Saved
                  </div>
                  <div className={`nav-tab ${activeTab === 'learning' ? 'active' : ''}`} onClick={() => setActiveTab('learning')}>
                    <span className="icon">📚</span>
                    Learn
                  </div>"""
    content = content[:nav_start] + new_tabs + content[nav_end:]

# Map the activeTab to ReelsTab
if "{activeTab === 'reels' && <ReelsTab />}" not in content:
    content = content.replace("{activeTab === 'learning' && <LearningTab />}", "{activeTab === 'learning' && <LearningTab />}\n        {activeTab === 'reels' && <ReelsTab />}")

with open('frontend/src/App.jsx', 'w', encoding='utf-8') as f:
    f.write(content)
print("Added ReelsTab and fixed iframe logic")
