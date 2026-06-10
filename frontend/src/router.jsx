import { createBrowserRouter } from 'react-router-dom';

import AuthPage from './pages/AuthPage';
import HomePage from './pages/HomePage';

export const router = createBrowserRouter([
  { path: '/', element: <HomePage /> },
  { path: '/login', element: <AuthPage defaultMode="login" /> },
  { path: '/register', element: <AuthPage defaultMode="register" /> },
]);
