import create from 'zustand'

export const useAuthStore = create((set) => ({
  token: localStorage.getItem('token'),
  refreshToken: localStorage.getItem('refresh'),
  user: null,
  setToken: (token, refreshToken) => {
    localStorage.setItem('token', token)
    if (refreshToken) localStorage.setItem('refresh', refreshToken)
    set({ token, refreshToken })
  },
  setUser: (user) => set({ user }),
  logout: () => {
    localStorage.removeItem('token')
    localStorage.removeItem('refresh')
    set({ token: null, refreshToken: null, user: null })
  },
}))

