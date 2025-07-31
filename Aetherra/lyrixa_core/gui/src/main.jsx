import React from 'react';
import { createRoot } from 'react-dom/client';
import AetherraGUI from './AetherraGUI.jsx';
import './index.css';

createRoot(document.getElementById('root')).render(
    <React.StrictMode>
        <AetherraGUI />
    </React.StrictMode>
);
