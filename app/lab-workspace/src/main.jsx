import React from 'react';
import { createRoot } from 'react-dom/client';
import { ReactFlowProvider } from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import './index.css';
import App from './App.jsx';
import { initAlpineBridge } from './bridge/alpineBridge.js';

initAlpineBridge();

createRoot(document.getElementById('lab-root')).render(
  <React.StrictMode>
    <ReactFlowProvider>
      <App />
    </ReactFlowProvider>
  </React.StrictMode>,
);
