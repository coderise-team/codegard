import client from './client';

// POST users/register/ -> { access, refresh }
export async function register({ username, email, password }) {
  const { data } = await client.post('users/register/', {
    username,
    email,
    password,
  });
  return data;
}

// GET users/me/ -> { username, avatar }
export async function me() {
  const { data } = await client.get('users/me/');
  return data;
}

// POST users/login/ -> { access, refresh }. `username` accepts a username or an email.
export async function login({ username, password }) {
  const { data } = await client.post('users/login/', { username, password });
  return data;
}

// POST users/token/refresh/ -> { access, refresh }
export async function refresh(refreshToken) {
  const { data } = await client.post('users/token/refresh/', {
    refresh: refreshToken,
  });
  return data;
}

// POST users/logout/ (Bearer + refresh) -> 205, blacklists the refresh token.
export async function logout(refreshToken) {
  await client.post('users/logout/', { refresh: refreshToken });
}
