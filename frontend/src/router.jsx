import { createBrowserRouter } from 'react-router-dom';

import AuthPage from './pages/AuthPage';
import Dashboard from './pages/Dashboard';
import PrivateRoute from './components/PrivateRoute';
import GuestRoute from './components/GuestRoute';

// STUB: temporary mock fixture until each block is wired to the real API.
// Remove together with frontend/src/data/homeData.js before merge.
import homeData from './data/homeData';

export const router = createBrowserRouter([
  {
    element: <GuestRoute />,
    children: [
      { path: '/login', element: <AuthPage key="login" mode="login" /> },
      {
        path: '/register',
        element: <AuthPage key="register" mode="register" />,
      },
    ],
  },
  {
    element: <PrivateRoute />,
    children: [{ path: '/', element: <Dashboard data={homeData} /> }],
  },
]);
