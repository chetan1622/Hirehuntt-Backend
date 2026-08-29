import os
import re

with open('frontend/src/App.jsx', 'r', encoding='utf-8') as f:
    content = f.read()

# Locate the Navigation Tabs block
start_marker = "{/* Navigation Tabs */}"
end_marker = "{/* Tab Content */}"

start_idx = content.find(start_marker)
end_idx = content.find(end_marker)

if start_idx != -1 and end_idx != -1:
    new_tabs = """{/* Navigation Tabs */}
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
    content = content[:start_idx] + new_tabs + content[end_idx:]

with open('frontend/src/App.jsx', 'w', encoding='utf-8') as f:
    f.write(content)

print("Tabs overhauled completely.")
