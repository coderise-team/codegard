import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';

import AuthPage from './AuthPage';

const { navigate, login, register } = vi.hoisted(() => ({
  navigate: vi.fn(),
  login: vi.fn(),
  register: vi.fn(),
}));

vi.mock('react-router-dom', async (importOriginal) => {
  const actual = await importOriginal();
  return { ...actual, useNavigate: () => navigate };
});

vi.mock('../store/authStore', () => ({
  useAuthStore: (selector) => selector({ login, register, isAuthenticated: false }),
}));

const renderInRouter = (ui) => render(<MemoryRouter>{ui}</MemoryRouter>);

beforeEach(() => {
  vi.clearAllMocks();
  login.mockResolvedValue(undefined);
  register.mockResolvedValue(undefined);
});

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

  it('submits login with the email mapped to username, then redirects', async () => {
    const { container } = renderInRouter(<AuthPage />);

    fireEvent.change(screen.getByRole('textbox'), { target: { value: 'a@b.io' } });
    fireEvent.change(container.querySelector('input[type="password"]'), {
      target: { value: 'secret' },
    });
    fireEvent.click(screen.getByRole('button', { name: 'Login' }));

    await waitFor(() =>
      expect(login).toHaveBeenCalledWith({ username: 'a@b.io', password: 'secret' }),
    );
    await waitFor(() => expect(navigate).toHaveBeenCalledWith('/', { replace: true }));
  });

  it('shows a backend error and does not redirect on failed login', async () => {
    login.mockRejectedValue({ response: { data: { detail: 'No active account found' } } });
    const { container } = renderInRouter(<AuthPage />);

    fireEvent.change(screen.getByRole('textbox'), { target: { value: 'a@b.io' } });
    fireEvent.change(container.querySelector('input[type="password"]'), {
      target: { value: 'x' },
    });
    fireEvent.click(screen.getByRole('button', { name: 'Login' }));

    expect(await screen.findByText('No active account found')).toBeInTheDocument();
    expect(navigate).not.toHaveBeenCalled();
  });

  it('surfaces DRF field errors (no detail) on failed register', async () => {
    register.mockRejectedValue({
      response: { data: { username: ['A user with that username already exists.'] } },
    });
    renderInRouter(<AuthPage mode="register" />);

    fireEvent.click(screen.getByRole('button', { name: 'Create account' }));

    expect(
      await screen.findByText('A user with that username already exists.'),
    ).toBeInTheDocument();
    expect(navigate).not.toHaveBeenCalled();
  });

  it('navigates to /register when the switch link is clicked', () => {
    renderInRouter(<AuthPage />);

    fireEvent.click(screen.getByRole('button', { name: 'Register' }));

    expect(navigate).toHaveBeenCalledWith('/register');
  });
});
