
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


import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'
import ErrorBoundary from './ErrorBoundary.jsx'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <ErrorBoundary><App /></ErrorBoundary>
  </React.StrictMode>,
)
