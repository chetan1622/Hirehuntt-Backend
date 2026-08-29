import os
with open('frontend/src/main.jsx', 'r', encoding='utf-8') as f:
    content = f.read()

# Remove the broken script
if "window.onerror =" in content:
    lines = content.split('\n')
    new_lines = []
    skip = False
    for line in lines:
        if "window.onerror =" in line:
            skip = True
        if skip and "import React" in line:
            skip = False
        if not skip:
            new_lines.append(line)
    content = '\n'.join(new_lines)

global_error = """
window.onerror = function(message, source, lineno, colno, error) {
  const div = document.createElement('div');
  div.style.color = 'red';
  div.style.padding = '20px';
  div.style.zIndex = '9999';
  div.style.position = 'absolute';
  div.style.top = '0';
  div.style.background = 'white';
  div.innerHTML = "<h3>Global Error</h3><p>" + message + "</p><pre>" + (error && error.stack) + "</pre>";
  document.body.appendChild(div);
};
window.addEventListener('unhandledrejection', function(event) {
  const div = document.createElement('div');
  div.style.color = 'red';
  div.style.padding = '20px';
  div.style.zIndex = '9999';
  div.style.position = 'absolute';
  div.style.top = '0';
  div.style.background = 'white';
  div.innerHTML = "<h3>Unhandled Promise</h3><p>" + event.reason + "</p>";
  document.body.appendChild(div);
});
"""

content = global_error + "\n" + content
with open('frontend/src/main.jsx', 'w', encoding='utf-8') as f:
    f.write(content)
print("Fixed main.jsx")
