import { create } from 'zustand';

import * as authApi from '../api/auth';
import { tokenStorage } from '../api/client';

export const useAuthStore = create((set) => ({
  user: null,
  isAuthenticated: false,
  isHydrating: true,

  // Restore the session on app start: a stored token only proves intent, so
  // verify it against the backend and load the user before trusting it.
  hydrate: async () => {
    if (!tokenStorage.getAccess()) {
      set({ isHydrating: false });
      return;
    }
    try {
      set({ user: await authApi.me(), isAuthenticated: true });
    } catch {
      tokenStorage.clear();
      set({ user: null, isAuthenticated: false });
    } finally {
      set({ isHydrating: false });
    }
  },

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
