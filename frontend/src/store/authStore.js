import { create } from 'zustand';

import * as authApi from '../api/auth';
import { tokenStorage } from '../api/client';

export const useAuthStore = create((set) => ({
  user: null,
  isAuthenticated: Boolean(tokenStorage.getAccess()),

  login: async (credentials) => {
    const data = await authApi.login(credentials);
    tokenStorage.set(data);
    set({ isAuthenticated: true });
  },

  register: async (payload) => {
    const data = await authApi.register(payload);
    tokenStorage.set(data);
    set({ user: data.user, isAuthenticated: true });
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
