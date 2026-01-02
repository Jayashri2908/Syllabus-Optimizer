import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './index.css';

import { SyllabusProvider } from './context/SyllabusContext';

ReactDOM.createRoot(document.getElementById('root')).render(
    <React.StrictMode>
        <SyllabusProvider>
            <App />
        </SyllabusProvider>
    </React.StrictMode>
);
