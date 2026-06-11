import { describe, it, expect, vi, beforeEach } from 'vitest';

const { authApi, tokenStorage } = vi.hoisted(() => ({
  authApi: { login: vi.fn(), register: vi.fn(), logout: vi.fn() },
  tokenStorage: {
    getAccess: vi.fn(),
    getRefresh: vi.fn(),
    set: vi.fn(),
    clear: vi.fn(),
  },
}));

vi.mock('../api/auth', () => authApi);
vi.mock('../api/client', () => ({ tokenStorage }));

import { useAuthStore } from './authStore';

const store = () => useAuthStore.getState();

beforeEach(() => {
  vi.clearAllMocks();
  tokenStorage.getAccess.mockReturnValue(null);
  tokenStorage.getRefresh.mockReturnValue(null);
  useAuthStore.setState({ user: null, isAuthenticated: false });
});

describe('authStore', () => {
  it('login stores tokens and authenticates without a user', async () => {
    authApi.login.mockResolvedValue({ access: 'a', refresh: 'r' });

    await store().login({ username: 'u', password: 'p' });

    expect(authApi.login).toHaveBeenCalledWith({ username: 'u', password: 'p' });
    expect(tokenStorage.set).toHaveBeenCalledWith({ access: 'a', refresh: 'r' });
    expect(store().isAuthenticated).toBe(true);
    expect(store().user).toBeNull();
  });

  it('register stores tokens, sets the user and authenticates', async () => {
    authApi.register.mockResolvedValue({
      user: { id: 1, username: 'u' },
      access: 'a',
      refresh: 'r',
    });

    await store().register({ username: 'u', email: 'e', password: 'p' });

    expect(tokenStorage.set).toHaveBeenCalled();
    expect(store().user).toEqual({ id: 1, username: 'u' });
    expect(store().isAuthenticated).toBe(true);
  });

  it('logout calls the API, clears tokens and resets state', async () => {
    tokenStorage.getRefresh.mockReturnValue('r');
    authApi.logout.mockResolvedValue();
    useAuthStore.setState({ user: { id: 1 }, isAuthenticated: true });

    await store().logout();

    expect(authApi.logout).toHaveBeenCalledWith('r');
    expect(tokenStorage.clear).toHaveBeenCalled();
    expect(store().user).toBeNull();
    expect(store().isAuthenticated).toBe(false);
  });

  it('logout skips the server call when there is no refresh token', async () => {
    tokenStorage.getRefresh.mockReturnValue(null);

    await store().logout();

    expect(authApi.logout).not.toHaveBeenCalled();
    expect(tokenStorage.clear).toHaveBeenCalled();
    expect(store().isAuthenticated).toBe(false);
  });

  it('logout still clears local state when the server call fails', async () => {
    tokenStorage.getRefresh.mockReturnValue('r');
    authApi.logout.mockRejectedValue(new Error('network'));
    useAuthStore.setState({ user: { id: 1 }, isAuthenticated: true });

    await store().logout();

    expect(tokenStorage.clear).toHaveBeenCalled();
    expect(store().isAuthenticated).toBe(false);
  });
});
