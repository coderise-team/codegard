import React from 'react'
import { render } from '@testing-library/react'
import { MemoryRouter, Routes, Route } from 'react-router-dom'
import { useAuthStore } from '../store/authStore'
import PrivateRoute from './PrivateRoute'

describe('PrivateRoute', () => {
  beforeEach(() => {
    useAuthStore.setState({ token: null })
  })

  it('redirects to /login if not authenticated', () => {
    const { container } = render(
      <MemoryRouter initialEntries={['/private']}>
        <Routes>
          <Route path="/private" element={
            <PrivateRoute>
              <div>Private</div>
            </PrivateRoute>
          } />
          <Route path="/login" element={<div>Login</div>} />
        </Routes>
      </MemoryRouter>
    )
    expect(container.innerHTML).toMatch(/Login/)
  })

  it('renders children if authenticated', () => {
    useAuthStore.setState({ token: 'abc' })
    const { container } = render(
      <MemoryRouter initialEntries={['/private']}>
        <Routes>
          <Route path="/private" element={
            <PrivateRoute>
              <div>Private</div>
            </PrivateRoute>
          } />
        </Routes>
      </MemoryRouter>
    )
    expect(container.innerHTML).toMatch(/Private/)
  })
})

