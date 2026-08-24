import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import './index.css'
import './animations.css'
import { SyllabusProvider } from './context/SyllabusContext'
import { BrowserRouter } from 'react-router-dom'

const rootEl = document.getElementById('root');
if (!rootEl) throw new Error('Root element not found');

ReactDOM.createRoot(rootEl).render(
  <React.StrictMode>
    <BrowserRouter>
      <SyllabusProvider>
        <App />
      </SyllabusProvider>
    </BrowserRouter>
  </React.StrictMode>,
)
