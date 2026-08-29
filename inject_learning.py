import os

with open('frontend/src/App.jsx', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Dark Mode useEffect Fix
dark_mode_effect = """
  useEffect(() => {
    if (darkMode) {
      document.documentElement.classList.remove('light-mode')
    } else {
      document.documentElement.classList.add('light-mode')
    }
  }, [darkMode])
"""
if "document.documentElement.classList.add('light-mode')" not in content:
    content = content.replace("const [darkMode, setDarkMode] = useState(false)", "const [darkMode, setDarkMode] = useState(false)\n" + dark_mode_effect)

# 2. Learning Tab Component
learning_tab = """
function LearningTab() {
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
if "function LearningTab" not in content:
    content = content.replace("function SavedJobsTab", learning_tab + "\nfunction SavedJobsTab")

with open('frontend/src/App.jsx', 'w', encoding='utf-8') as f:
    f.write(content)
print("Added LearningTab and DarkMode fix")
