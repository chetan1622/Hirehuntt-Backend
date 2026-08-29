import os

with open('frontend/src/App.jsx', 'r', encoding='utf-8') as f:
    content = f.read()

old_tabs = """              {!isAdmin ? (
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
              ) : null}"""

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
              ) : null}"""

content = content.replace(old_tabs, new_tabs)

with open('frontend/src/App.jsx', 'w', encoding='utf-8') as f:
    f.write(content)
print("Profile tab moved to first")
