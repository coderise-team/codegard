import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';

import AuthPage from './AuthPage';

// AuthPage reads the router (useNavigate/useLocation), so it needs a Router.
const renderInRouter = (ui) => render(<MemoryRouter>{ui}</MemoryRouter>);

describe('AuthPage', () => {
  it('renders the login form by default', () => {
    renderInRouter(<AuthPage />);

    expect(screen.getByRole('heading', { name: 'Login' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Login' })).toBeInTheDocument();
    expect(screen.getByText(/don't have an account\?/i)).toBeInTheDocument();
  });

  it('renders the register form when mode is "register"', () => {
    renderInRouter(<AuthPage mode="register" />);

    expect(screen.getByRole('heading', { name: 'Register' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Create account' })).toBeInTheDocument();
    expect(screen.getByText(/already have an account\?/i)).toBeInTheDocument();
  });
});
