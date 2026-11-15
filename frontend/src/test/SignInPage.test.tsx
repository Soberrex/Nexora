import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'

import { createFakeAuthAdapter } from '@/test/fakeAuth'
import { mockApi, renderRoute } from '@/test/render'

describe('SignInPage', () => {
  beforeEach(() => {
    mockApi({
      '/api/v1/health': { body: { status: 'ok', version: '0.1.0' } },
      '/api/v1/me/organizations': { body: { data: [{ id: 'org-1', name: 'Org A', role: 'technician' }] } },
    })
  })

  it('redirects signed-out users to sign in, then back after signing in', async () => {
    const adapter = createFakeAuthAdapter()
    renderRoute('/incidents', { adapter })
    expect(await screen.findByRole('heading', { name: 'Sign in to Nexora' })).toBeInTheDocument()
    await userEvent.type(screen.getByLabelText('Email'), 'tech@a.io')
    await userEvent.type(screen.getByLabelText('Password'), 'correct-horse')
    await userEvent.click(screen.getByRole('button', { name: 'Sign in' }))
    expect(await screen.findByRole('heading', { level: 1, name: 'Incidents' })).toBeInTheDocument()
  })

  it('shows a readable error for wrong credentials', async () => {
    renderRoute('/sign-in', { adapter: createFakeAuthAdapter() })
    await userEvent.type(await screen.findByLabelText('Email'), 'tech@a.io')
    await userEvent.type(screen.getByLabelText('Password'), 'wrong-password')
    await userEvent.click(screen.getByRole('button', { name: 'Sign in' }))
    expect(await screen.findByRole('alert')).toHaveTextContent('Incorrect email or password')
  })

  it('can switch to creating an account', async () => {
    const adapter = createFakeAuthAdapter()
    renderRoute('/sign-in', { adapter })
    await userEvent.click(await screen.findByRole('button', { name: 'Create an account' }))
    await userEvent.type(screen.getByLabelText('Email'), 'new@a.io')
    await userEvent.type(screen.getByLabelText('Password'), 'any-password-1')
    await userEvent.click(screen.getByRole('button', { name: 'Create account' }))
    expect(await screen.findByRole('heading', { level: 1, name: 'Overview' })).toBeInTheDocument()
    expect(adapter.current()?.email).toBe('new@a.io')
  })
})
