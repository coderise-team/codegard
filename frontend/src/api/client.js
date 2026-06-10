import axios from 'axios';

const ACCESS_KEY = 'access';
const REFRESH_KEY = 'refresh';

const baseURL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000/api';

const AUTH_PATHS = ['users/login/', 'users/register/', 'users/token/refresh/'];

export const tokenStorage = {
  getAccess: () => localStorage.getItem(ACCESS_KEY),
  getRefresh: () => localStorage.getItem(REFRESH_KEY),
  set: ({ access, refresh }) => {
    if (access) localStorage.setItem(ACCESS_KEY, access);
    if (refresh) localStorage.setItem(REFRESH_KEY, refresh);
  },
  clear: () => {
    localStorage.removeItem(ACCESS_KEY);
    localStorage.removeItem(REFRESH_KEY);
  },
};

const client = axios.create({ baseURL });

client.interceptors.request.use((config) => {
  const token = tokenStorage.getAccess();
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// Shared so concurrent 401s trigger one refresh (backend blacklists rotated tokens).
let refreshPromise = null;

async function refreshAccessToken() {
  const refresh = tokenStorage.getRefresh();
  if (!refresh) throw new Error('No refresh token');
  // Bare axios call so this request skips the interceptors below.
  const { data } = await axios.post(`${baseURL}/users/token/refresh/`, {
    refresh,
  });
  tokenStorage.set(data);
  return data.access;
}

const isAuthPath = (url = '') => AUTH_PATHS.some((path) => url.includes(path));

client.interceptors.response.use(
  (response) => response,
  async (error) => {
    const { config, response } = error;

    const shouldRefresh =
      response?.status === 401 &&
      config &&
      !config._retry &&
      !isAuthPath(config.url) &&
      Boolean(tokenStorage.getRefresh());

    if (!shouldRefresh) return Promise.reject(error);

    config._retry = true;
    try {
      refreshPromise = refreshPromise ?? refreshAccessToken();
      const access = await refreshPromise;
      config.headers.Authorization = `Bearer ${access}`;
      return client(config);
    } catch (refreshError) {
      tokenStorage.clear();
      if (window.location.pathname !== '/login') {
        window.location.href = '/login';
      }
      return Promise.reject(refreshError);
    } finally {
      refreshPromise = null;
    }
  },
);

export default client;
