import os

with open('frontend/src/App.jsx', 'r', encoding='utf-8') as f:
    content = f.read()

# Add LearningTab rendering
if "{activeTab === 'learning' && <LearningTab />}" not in content:
    content = content.replace("{activeTab === 'saved' && <SavedJobsTab userId={userId} />}", 
                              "{activeTab === 'saved' && <SavedJobsTab userId={userId} />}\n        {activeTab === 'learning' && <LearningTab />}")

# Fix navigation tab order with text
old_tabs = """              {!isAdmin ? (
                <div className="nav-tabs">
                  <div className={`nav-tab ${activeTab === 'profile' ? 'active' : ''}`} onClick={() => setActiveTab('profile')}>
                    <span className="icon">👤</span>
                    Profile
                  </div>
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
                </div>
              ) : null}"""

# I'll just rewrite the whole nav-tabs block cleanly
start_idx = content.find("              {!isAdmin ? (")
end_idx = content.find("              ) : null}", start_idx)

if start_idx != -1 and end_idx != -1:
    new_tabs = """              {!isAdmin ? (
                <div className="nav-tabs">
                  <div className={`nav-tab ${activeTab === 'profile' ? 'active' : ''}`} onClick={() => setActiveTab('profile')}>
                    <span className="icon">👤</span>
                    Profile
                  </div>
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
                </div>
"""
    content = content[:start_idx] + new_tabs + content[end_idx:]

with open('frontend/src/App.jsx', 'w', encoding='utf-8') as f:
    f.write(content)

print("Fixed JSX rendering for LearningTab and Nav order")
