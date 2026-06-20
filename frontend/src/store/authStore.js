import { create } from 'zustand';

import * as authApi from '../api/auth';
import { tokenStorage } from '../api/client';

export const useAuthStore = create((set) => ({
  user: null,
  isAuthenticated: Boolean(tokenStorage.getAccess()),

  login: async (credentials) => {
    tokenStorage.set(await authApi.login(credentials));
    set({ user: await authApi.me(), isAuthenticated: true });
  },

  register: async (payload) => {
    tokenStorage.set(await authApi.register(payload));
    set({ user: await authApi.me(), isAuthenticated: true });
  },

  logout: async () => {
    const refresh = tokenStorage.getRefresh();
    try {
      if (refresh) await authApi.logout(refresh);
    } catch {
      // Server-side logout is best-effort; clear local state regardless.
    }
    tokenStorage.clear();
    set({ user: null, isAuthenticated: false });
  },
}));
