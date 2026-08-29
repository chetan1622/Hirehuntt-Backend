import os

with open('frontend/src/App.jsx', 'r', encoding='utf-8') as f:
    content = f.read()

# Remove the old nav-tabs entirely and replace it
lines = content.split('\n')
new_lines = []
skip = False
for line in lines:
    if "className=\"nav-tabs\"" in line:
        skip = True
        new_lines.append("""
              {!isAdmin ? (
                <div className="nav-tabs">
                  <div className={`nav-tab ${activeTab === 'logs' ? 'active' : ''}`} onClick={() => setActiveTab('logs')}>
                    <span className="icon">💼</span>
                    Jobs
                  </div>
                  <div className={`nav-tab ${activeTab === 'saved' ? 'active' : ''}`} onClick={() => setActiveTab('saved')}>
                    <span className="icon">⭐</span>
                    Saved
                  </div>
                  <div className={`nav-tab ${activeTab === 'learning' ? 'active' : ''}`} onClick={() => setActiveTab('learning')}>
                    <span className="icon">📚</span>
                    Learn
                  </div>
                  <div className={`nav-tab ${activeTab === 'profile' ? 'active' : ''}`} onClick={() => setActiveTab('profile')}>
                    <span className="icon">👤</span>
                    Profile
                  </div>
                </div>
              ) : null}
""")
    if skip:
        if "Tab Content" in line or "{activeTab ===" in line:
            skip = False
    
    if not skip:
        new_lines.append(line)

with open('frontend/src/App.jsx', 'w', encoding='utf-8') as f:
    f.write('\n'.join(new_lines))

print("Fixed tabs!")
