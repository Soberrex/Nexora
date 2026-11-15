import { screen, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'

import { mockApi, renderRoute } from '@/test/render'

describe('AppShell', () => {
  beforeEach(() => {
    mockApi({
      '/api/v1/health': { body: { status: 'ok', version: '0.1.0' } },
      '/api/v1/me/organizations': { body: { data: [{ id: 'org-1', name: 'Org A', role: 'technician' }] } },
    })
  })

  it('renders the primary navigation with Overview active', async () => {
    renderRoute('/')
    const nav = (await screen.findAllByRole('navigation', { name: 'Primary' }))[0]!
    for (const label of ['Overview', 'Incidents', 'My Work', 'Teams', 'Workflows', 'Knowledge Base', 'AI Assistant', 'Reports']) {
      expect(within(nav).getByRole('link', { name: label })).toBeInTheDocument()
    }
    expect(within(nav).getByRole('link', { name: 'Overview' })).toHaveAttribute('aria-current', 'page')
  })

  it('navigates to a planned module and shows its milestone', async () => {
    renderRoute('/')
    const nav = (await screen.findAllByRole('navigation', { name: 'Primary' }))[0]!
    await userEvent.click(within(nav).getByRole('link', { name: 'Incidents' }))
    expect(screen.getByRole('heading', { level: 1, name: 'Incidents' })).toBeInTheDocument()
    expect(screen.getByText(/milestone M2/)).toBeInTheDocument()
  })

  it('opens and closes the mobile navigation drawer', async () => {
    renderRoute('/')
    await userEvent.click(await screen.findByRole('button', { name: 'Open navigation' }))
    expect(screen.getByRole('dialog', { name: 'Navigation' })).toBeInTheDocument()
    await userEvent.keyboard('{Escape}')
    expect(screen.queryByRole('dialog')).not.toBeInTheDocument()
  })

  it('shows a not-found page for unknown routes', async () => {
    renderRoute('/does-not-exist')
    expect(await screen.findByRole('heading', { name: 'Page not found' })).toBeInTheDocument()
  })
})
