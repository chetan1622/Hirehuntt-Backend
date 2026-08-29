import os
with open('frontend/src/App.jsx', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('<ErrorBoundary>', '')
content = content.replace('</ErrorBoundary>', '')

content = content.replace('<div className="app-container">', '<div className="app-container">\n      <ErrorBoundary>')
content = content.replace('</footer>', '</footer>\n      </ErrorBoundary>')

with open('frontend/src/App.jsx', 'w', encoding='utf-8') as f:
    f.write(content)
print("Tags fixed")
