import { Navigate, Outlet, useLocation } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';

/**
 * PrivateRoute — guards nested routes that require authentication.
 * Unauthenticated users are redirected to /login, with the attempted
 * location preserved so they can be returned there after signing in.
 *
 * This is a UX guard only; real access control is enforced by the backend.
 */
export default function PrivateRoute() {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);
  const location = useLocation();

  if (!isAuthenticated) {
    return <Navigate to="/login" replace state={{ from: location }} />;
  }

  return <Outlet />;
}
