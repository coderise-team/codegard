import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { createMemoryRouter, RouterProvider } from 'react-router-dom';

import PrivateRoute from './PrivateRoute';

const auth = vi.hoisted(() => ({ isAuthenticated: false, isHydrating: false }));
vi.mock('../store/authStore', () => ({
  useAuthStore: (selector) =>
    selector({
      isAuthenticated: auth.isAuthenticated,
      isHydrating: auth.isHydrating,
    }),
}));

const renderRoutes = () => {
  const router = createMemoryRouter(
    [
      { path: '/login', element: <div>Login Page</div> },
      {
        element: <PrivateRoute />,
        children: [{ path: '/', element: <div>Protected</div> }],
      },
    ],
    { initialEntries: ['/'] }
  );
  return render(<RouterProvider router={router} />);
};

describe('PrivateRoute', () => {
  it('renders the nested route when authenticated', () => {
    auth.isAuthenticated = true;
    auth.isHydrating = false;
    renderRoutes();
    expect(screen.getByText('Protected')).toBeInTheDocument();
  });

  it('redirects to /login when not authenticated', () => {
    auth.isAuthenticated = false;
    auth.isHydrating = false;
    renderRoutes();
    expect(screen.getByText('Login Page')).toBeInTheDocument();
    expect(screen.queryByText('Protected')).not.toBeInTheDocument();
  });

  it('renders nothing while the session is hydrating', () => {
    auth.isAuthenticated = false;
    auth.isHydrating = true;
    renderRoutes();
    expect(screen.queryByText('Protected')).not.toBeInTheDocument();
    expect(screen.queryByText('Login Page')).not.toBeInTheDocument();
  });
});
