import { describe, it, expect, vi, beforeEach } from 'vitest';

const { mockClient, axiosPost } = vi.hoisted(() => {
  const client = vi.fn();
  client.interceptors = {
    request: { use: vi.fn() },
    response: { use: vi.fn() },
  };
  return { mockClient: client, axiosPost: vi.fn() };
});

vi.mock('axios', () => ({
  default: { create: () => mockClient, post: axiosPost },
}));

import { tokenStorage } from './client';

// Handlers registered on the instance at module load.
const requestHandler = mockClient.interceptors.request.use.mock.calls[0][0];
const onRejected = mockClient.interceptors.response.use.mock.calls[0][1];

beforeEach(() => {
  localStorage.clear();
  axiosPost.mockReset();
  mockClient.mockReset();
});

describe('tokenStorage', () => {
  it('set stores access and refresh', () => {
    tokenStorage.set({ access: 'a', refresh: 'r' });
    expect(localStorage.getItem('access')).toBe('a');
    expect(localStorage.getItem('refresh')).toBe('r');
  });

  it('set ignores missing fields', () => {
    tokenStorage.set({ access: 'only' });
    expect(localStorage.getItem('access')).toBe('only');
    expect(localStorage.getItem('refresh')).toBeNull();
  });

  it('clear removes both tokens', () => {
    tokenStorage.set({ access: 'a', refresh: 'r' });
    tokenStorage.clear();
    expect(tokenStorage.getAccess()).toBeNull();
    expect(tokenStorage.getRefresh()).toBeNull();
  });
});

describe('request interceptor', () => {
  it('adds a Bearer header when an access token exists', () => {
    localStorage.setItem('access', 'tok');
    const config = requestHandler({ headers: {} });
    expect(config.headers.Authorization).toBe('Bearer tok');
  });

  it('leaves headers untouched without a token', () => {
    const config = requestHandler({ headers: {} });
    expect(config.headers.Authorization).toBeUndefined();
  });
});

describe('response interceptor (401 refresh)', () => {
  it('refreshes the token once and retries the original request', async () => {
    localStorage.setItem('refresh', 'r0');
    axiosPost.mockResolvedValue({ data: { access: 'newA', refresh: 'newR' } });
    mockClient.mockResolvedValue({ data: 'retried' });

    const config = { url: 'problems/1/', headers: {} };
    const result = await onRejected({ config, response: { status: 401 } });

    expect(axiosPost).toHaveBeenCalledWith(
      expect.stringContaining('/users/token/refresh/'),
      { refresh: 'r0' }
    );
    expect(localStorage.getItem('access')).toBe('newA');
    expect(config.headers.Authorization).toBe('Bearer newA');
    expect(mockClient).toHaveBeenCalledWith(config);
    expect(result).toEqual({ data: 'retried' });
  });

  it('does not refresh on auth endpoints', async () => {
    localStorage.setItem('refresh', 'r0');
    const error = {
      config: { url: 'users/login/', headers: {} },
      response: { status: 401 },
    };

    await expect(onRejected(error)).rejects.toBe(error);
    expect(axiosPost).not.toHaveBeenCalled();
  });

  it('does not refresh without a refresh token', async () => {
    const error = {
      config: { url: 'problems/', headers: {} },
      response: { status: 401 },
    };

    await expect(onRejected(error)).rejects.toBe(error);
    expect(axiosPost).not.toHaveBeenCalled();
  });

  it('passes non-401 errors through untouched', async () => {
    const error = {
      config: { url: 'problems/', headers: {} },
      response: { status: 500 },
    };
    await expect(onRejected(error)).rejects.toBe(error);
  });

  it('shares a single refresh across concurrent 401s', async () => {
    localStorage.setItem('refresh', 'r0');
    let resolvePost;
    axiosPost.mockReturnValue(
      new Promise((res) => {
        resolvePost = res;
      })
    );
    mockClient.mockResolvedValue({ data: 'ok' });

    const p1 = onRejected({
      config: { url: 'a/', headers: {} },
      response: { status: 401 },
    });
    const p2 = onRejected({
      config: { url: 'b/', headers: {} },
      response: { status: 401 },
    });
    resolvePost({ data: { access: 'A', refresh: 'R' } });
    await Promise.all([p1, p2]);

    expect(axiosPost).toHaveBeenCalledTimes(1);
  });

  it('clears tokens when the refresh request itself fails', async () => {
    localStorage.setItem('access', 'old');
    localStorage.setItem('refresh', 'bad');
    axiosPost.mockRejectedValue(new Error('refresh failed'));
    // Already on /login so the redirect branch is skipped (avoids jsdom navigation).
    window.history.pushState({}, '', '/login');

    const error = {
      config: { url: 'problems/', headers: {} },
      response: { status: 401 },
    };
    await expect(onRejected(error)).rejects.toThrow('refresh failed');

    expect(tokenStorage.getAccess()).toBeNull();
    expect(tokenStorage.getRefresh()).toBeNull();
  });
});
