import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { createMemoryRouter, RouterProvider } from 'react-router-dom';

import PrivateRoute from './PrivateRoute';

const auth = vi.hoisted(() => ({ isAuthenticated: false }));
vi.mock('../store/authStore', () => ({
  useAuthStore: (selector) => selector({ isAuthenticated: auth.isAuthenticated }),
}));

const renderRoutes = () => {
  const router = createMemoryRouter(
    [
      { path: '/login', element: <div>Login Page</div> },
      { element: <PrivateRoute />, children: [{ path: '/', element: <div>Protected</div> }] },
    ],
    { initialEntries: ['/'] },
  );
  return render(<RouterProvider router={router} />);
};

describe('PrivateRoute', () => {
  it('renders the nested route when authenticated', () => {
    auth.isAuthenticated = true;
    renderRoutes();
    expect(screen.getByText('Protected')).toBeInTheDocument();
  });

  it('redirects to /login when not authenticated', () => {
    auth.isAuthenticated = false;
    renderRoutes();
    expect(screen.getByText('Login Page')).toBeInTheDocument();
    expect(screen.queryByText('Protected')).not.toBeInTheDocument();
  });
});
