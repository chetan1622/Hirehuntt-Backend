import os

with open('frontend/src/App.jsx', 'r', encoding='utf-8') as f:
    content = f.read()

target = "const [footerModal, setFooterModal] = useState(null) // null, 'about', 'contact', 'terms'"
replacement = target + "\n  const [darkMode, setDarkMode] = useState(false)"

content = content.replace(target, replacement)

with open('frontend/src/App.jsx', 'w', encoding='utf-8') as f:
    f.write(content)

print("darkMode defined")
