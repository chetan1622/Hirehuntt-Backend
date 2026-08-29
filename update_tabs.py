import os

with open('frontend/src/App.jsx', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add 'learning' to valid tabs
content = content.replace("setActiveTab('profile')", "setActiveTab('jobs')") # Default to jobs on login

# 2. Modify nav-tabs to include Bottom Tabs
old_tabs = """
              {!isAdmin ? (
                <div className="nav-tabs">
                  <div className={`nav-tab ${activeTab === 'profile' ? 'active' : ''}`} onClick={() => setActiveTab('profile')}>
                    Profile
                  </div>
                  <div className={`nav-tab ${activeTab === 'logs' ? 'active' : ''}`} onClick={() => setActiveTab('logs')}>
                    Jobs
                  </div>
                  <div className={`nav-tab ${activeTab === 'saved' ? 'active' : ''}`} onClick={() => setActiveTab('saved')}>
                    Saved
                  </div>
                </div>
              ) : null}
"""
new_tabs = """
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
"""
content = content.replace(old_tabs.strip(), new_tabs.strip())

# 3. Add Learning Tab to Router
content = content.replace("{activeTab === 'saved' && <SavedJobsTab userId={userId} toast={showToast} />}", "{activeTab === 'saved' && <SavedJobsTab userId={userId} toast={showToast} />}\n              {activeTab === 'learning' && <LearningTab />}")

with open('frontend/src/App.jsx', 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated Bottom Navigation Tabs")
