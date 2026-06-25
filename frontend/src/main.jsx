import React from 'react';
import ReactDOM from 'react-dom/client';
import { RouterProvider } from 'react-router-dom';

import './styles/variables.css';
import './styles/global.css';
import { router } from './router';
import { useAuthStore } from './store/authStore';

// Restore the session before first paint; guards wait on isHydrating.
useAuthStore.getState().hydrate();

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <RouterProvider router={router} />
  </React.StrictMode>
);
