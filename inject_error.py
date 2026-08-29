import os

with open('frontend/src/App.jsx', 'r', encoding='utf-8') as f:
    content = f.read()

error_boundary = """
class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null };
  }
  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }
  componentDidCatch(error, errorInfo) {
    console.error('ErrorBoundary caught:', error, errorInfo);
    this.setState({ errorInfo });
  }
  render() {
    if (this.state.hasError) {
      return (
        <div style={{ padding: 20, color: 'red', wordBreak: 'break-all' }}>
          <h2>App Crashed!</h2>
          <p>{this.state.error && this.state.error.toString()}</p>
          <pre style={{ fontSize: 10 }}>{this.state.errorInfo && this.state.errorInfo.componentStack}</pre>
        </div>
      );
    }
    return this.props.children;
  }
}
"""

if "class ErrorBoundary" not in content:
    if "import React" not in content:
        content = content.replace("import { useState", "import React, { useState")
    
    content = content.replace("const API =", error_boundary + "\nconst API =")
    content = content.replace('<div className="app-container">', '<div className="app-container">\n<ErrorBoundary>')
    content = content.replace('</footer>\n    </div>', '</footer>\n</ErrorBoundary>\n    </div>')

with open('frontend/src/App.jsx', 'w', encoding='utf-8') as f:
    f.write(content)
print("ErrorBoundary injected safely")
