import { act } from 'react-dom/test-utils'
import { useAuthStore } from './authStore'

describe('authStore', () => {
  beforeEach(() => {
    useAuthStore.setState({ token: null, refreshToken: null, user: null })
    localStorage.clear()
  })

  it('sets token and refreshToken', () => {
    act(() => {
      useAuthStore.getState().setToken('abc', 'ref')
    })
    expect(useAuthStore.getState().token).toBe('abc')
    expect(useAuthStore.getState().refreshToken).toBe('ref')
    expect(localStorage.getItem('token')).toBe('abc')
    expect(localStorage.getItem('refresh')).toBe('ref')
  })

  it('sets user', () => {
    act(() => {
      useAuthStore.getState().setUser({ id: 1 })
    })
    expect(useAuthStore.getState().user).toEqual({ id: 1 })
  })

  it('logout resets state and localStorage', () => {
    act(() => {
      useAuthStore.getState().setToken('abc', 'ref')
      useAuthStore.getState().setUser({ id: 1 })
      useAuthStore.getState().logout()
    })
    expect(useAuthStore.getState().token).toBeNull()
    expect(useAuthStore.getState().refreshToken).toBeNull()
    expect(useAuthStore.getState().user).toBeNull()
    expect(localStorage.getItem('token')).toBeNull()
    expect(localStorage.getItem('refresh')).toBeNull()
  })
})

