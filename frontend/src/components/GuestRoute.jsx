import { Navigate, Outlet } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';

/**
 * GuestRoute — guards guest-only routes (/login, /register) against
 * already-authenticated users, sending them home. Mirror of PrivateRoute.
 *
 * This is a UX guard only; real access control is enforced by the backend.
 */
export default function GuestRoute() {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);
  const isHydrating = useAuthStore((s) => s.isHydrating);

  if (isHydrating) return null;

  if (isAuthenticated) {
    return <Navigate to="/" replace />;
  }

  return <Outlet />;
}
