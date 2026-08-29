import os
with open('frontend/src/main.jsx', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace("import App from './App.jsx'", "import App from './App.jsx'\nimport ErrorBoundary from './ErrorBoundary.jsx'")
content = content.replace("<App />", "<ErrorBoundary><App /></ErrorBoundary>")

with open('frontend/src/main.jsx', 'w', encoding='utf-8') as f:
    f.write(content)
print("Wrapped successfully")
