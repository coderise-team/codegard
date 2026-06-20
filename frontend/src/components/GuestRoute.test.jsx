import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { createMemoryRouter, RouterProvider } from 'react-router-dom';

import GuestRoute from './GuestRoute';

const auth = vi.hoisted(() => ({ isAuthenticated: false, isHydrating: false }));
vi.mock('../store/authStore', () => ({
  useAuthStore: (selector) =>
    selector({ isAuthenticated: auth.isAuthenticated, isHydrating: auth.isHydrating }),
}));

const renderRoutes = () => {
  const router = createMemoryRouter(
    [
      { path: '/', element: <div>Home Page</div> },
      { element: <GuestRoute />, children: [{ path: '/login', element: <div>Login</div> }] },
    ],
    { initialEntries: ['/login'] },
  );
  return render(<RouterProvider router={router} />);
};

describe('GuestRoute', () => {
  it('renders the nested route when not authenticated', () => {
    auth.isAuthenticated = false;
    auth.isHydrating = false;
    renderRoutes();
    expect(screen.getByText('Login')).toBeInTheDocument();
  });

  it('redirects home when already authenticated', () => {
    auth.isAuthenticated = true;
    auth.isHydrating = false;
    renderRoutes();
    expect(screen.getByText('Home Page')).toBeInTheDocument();
    expect(screen.queryByText('Login')).not.toBeInTheDocument();
  });

  it('renders nothing while the session is hydrating', () => {
    auth.isAuthenticated = true;
    auth.isHydrating = true;
    renderRoutes();
    expect(screen.queryByText('Home Page')).not.toBeInTheDocument();
    expect(screen.queryByText('Login')).not.toBeInTheDocument();
  });
});
