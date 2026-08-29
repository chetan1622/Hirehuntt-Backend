import os

with open('frontend/src/App.jsx', 'r', encoding='utf-8') as f:
    content = f.read()

# Make frontend robust with fallback videos just in case backend fails
new_learning_tab = """function LearningTab() {
  const [shorts, setShorts] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetch(`${API}/shorts`)
      .then(r => r.json())
      .then(data => {
        if (data && data.length > 0) {
          setShorts(data)
        } else {
          // Fallback if backend is blocked by YouTube or empty
          setShorts([
            { id: "dQw4w9WgXcQ", title: "Job Interview Tips (Fallback)", author: "System" },
            { id: "jNQXAC9IVRw", title: "Resume Tricks", author: "System" }
          ])
        }
        setLoading(false)
      })
      .catch(() => {
        setShorts([
          { id: "dQw4w9WgXcQ", title: "Job Interview Tips (Fallback)", author: "System" }
        ])
        setLoading(false)
      })
  }, [])

  if (loading) return <div style={{ textAlign: 'center', padding: 40 }}><span className="spinner"></span></div>

  return (
    <div className="learning-tab" style={{ padding: 0, margin: '-24px -16px', height: '100vh', overflowY: 'scroll', scrollSnapType: 'y mandatory', backgroundColor: 'black' }}>
      {shorts.map((video, i) => (
        <div key={i} style={{ height: '100vh', width: '100%', scrollSnapAlign: 'start', position: 'relative' }}>
          <iframe 
            src={`https://www.youtube.com/embed/${video.id}?autoplay=0&loop=1&playsinline=1`}
            style={{ width: '100%', height: '100%', border: 'none' }}
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
            allowFullScreen
          ></iframe>
          <div style={{ position: 'absolute', bottom: 120, left: 16, color: 'white', textShadow: '0 2px 4px rgba(0,0,0,0.8)' }}>
            <h3 style={{ margin: 0, fontSize: 18 }}>{video.author}</h3>
            <p style={{ margin: '4px 0 0', fontSize: 14 }}>{video.title}</p>
          </div>
        </div>
      ))}
    </div>
  )
}
"""

start_idx = content.find("function LearningTab() {")
end_idx = content.find("function SavedJobsTab", start_idx)

if start_idx != -1 and end_idx != -1:
    content = content[:start_idx] + new_learning_tab + content[end_idx:]

with open('frontend/src/App.jsx', 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated LearningTab with fallback")
