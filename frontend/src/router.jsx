import { createBrowserRouter } from 'react-router-dom';

import AuthPage from './pages/AuthPage';
import HomePage from './pages/HomePage';
import PrivateRoute from './components/PrivateRoute';

export const router = createBrowserRouter([
  { path: '/login', element: <AuthPage key="login" mode="login" /> },
  { path: '/register', element: <AuthPage key="register" mode="register" /> },
  {
    element: <PrivateRoute />,
    children: [
      { path: '/', element: <HomePage /> },
    ],
  },
]);
