import { describe, it, expect, vi, beforeEach } from 'vitest';

const { post, get } = vi.hoisted(() => ({ post: vi.fn(), get: vi.fn() }));
vi.mock('./client', () => ({ default: { post, get } }));

import { register, login, refresh, logout, me } from './auth';

beforeEach(() => {
  post.mockReset();
  get.mockReset();
});

describe('auth API', () => {
  it('register posts credentials and returns the response body', async () => {
    post.mockResolvedValue({ data: { access: 'a', refresh: 'r' } });

    const data = await register({ username: 'u', email: 'e@x.io', password: 'p' });

    expect(post).toHaveBeenCalledWith('users/register/', {
      username: 'u',
      email: 'e@x.io',
      password: 'p',
    });
    expect(data).toEqual({ access: 'a', refresh: 'r' });
  });

  it('me fetches the current user', async () => {
    get.mockResolvedValue({ data: { username: 'u', avatar: null } });

    const data = await me();

    expect(get).toHaveBeenCalledWith('users/me/');
    expect(data).toEqual({ username: 'u', avatar: null });
  });

  it('login posts username/password and returns the body', async () => {
    post.mockResolvedValue({ data: { access: 'a', refresh: 'r' } });

    const data = await login({ username: 'u', password: 'p' });

    expect(post).toHaveBeenCalledWith('users/login/', { username: 'u', password: 'p' });
    expect(data).toEqual({ access: 'a', refresh: 'r' });
  });

  it('refresh posts the refresh token', async () => {
    post.mockResolvedValue({ data: { access: 'a2', refresh: 'r2' } });

    const data = await refresh('r1');

    expect(post).toHaveBeenCalledWith('users/token/refresh/', { refresh: 'r1' });
    expect(data).toEqual({ access: 'a2', refresh: 'r2' });
  });

  it('logout posts the refresh token and returns nothing', async () => {
    post.mockResolvedValue({ status: 205 });

    const result = await logout('r1');

    expect(post).toHaveBeenCalledWith('users/logout/', { refresh: 'r1' });
    expect(result).toBeUndefined();
  });
});
