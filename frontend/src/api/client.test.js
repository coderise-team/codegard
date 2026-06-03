import axios from 'axios'
import MockAdapter from 'axios-mock-adapter'
import client from './client'
import { useAuthStore } from '../store/authStore'

describe('client JWT interceptor', () => {
  let mock

  beforeEach(() => {
    mock = new MockAdapter(axios)
    useAuthStore.setState({
      token: 'access',
      refreshToken: 'refresh',
      setToken: (a, r) => useAuthStore.setState({ token: a, refreshToken: r }),
      logout: jest.fn()
    })
    localStorage.setItem('token', 'access')
    localStorage.setItem('refresh', 'refresh')
  })

  afterEach(() => {
    mock.restore()
    localStorage.clear()
  })

  it('adds Authorization header', async () => {
    mock.onGet('/test').reply((config) => {
      expect(config.headers.Authorization).toBe('Bearer access')
      return [200, {}]
    })
    await client.get('/test')
  })

  it('refreshes token on 401', async () => {
    mock.onGet('/private').replyOnce(401)
    mock.onPost(/\/auth\/refresh/).reply(200, { access: 'new_access', refresh: 'new_refresh' })
    mock.onGet('/private').reply(200, { ok: true })

    let called = false
    useAuthStore.setState({
      ...useAuthStore.getState(),
      setToken: (a, r) => {
        useAuthStore.setState({ token: a, refreshToken: r })
        called = true
      }
    })

    const res = await client.get('/private')
    expect(res.data.ok).toBe(true)
    expect(called).toBe(true)
    expect(useAuthStore.getState().token).toBe('new_access')
  })

  it('logout on refresh fail', async () => {
    mock.onGet('/private').replyOnce(401)
    mock.onPost(/\/auth\/refresh/).reply(400)
    useAuthStore.setState({ ...useAuthStore.getState(), logout: jest.fn() })

    await expect(client.get('/private')).rejects.toBeTruthy()
    expect(useAuthStore.getState().logout).toHaveBeenCalled()
  })
})

