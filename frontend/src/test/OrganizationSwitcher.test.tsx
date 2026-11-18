import { QueryClient } from '@tanstack/react-query'
import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'

import { apiFetch, setApiOrganizationId } from '@/api/client'
import { mockApi, renderRoute } from '@/test/render'

const ORGS = [
  { id: 'org-a', name: 'Org A', role: 'technician' },
  { id: 'org-b', name: 'Org B', role: 'org_admin' },
]

describe('organization context', () => {
  beforeEach(() => localStorage.clear())
  afterEach(() => setApiOrganizationId(null))

  function lastOrgHeader(fetchMock: ReturnType<typeof mockApi>) {
    const init = (fetchMock.mock.calls.at(-1) as unknown as [unknown, RequestInit])[1]
    return (init.headers as Headers).get('X-Organization-ID')
  }

  it('selects the first organization and sends it to the API', async () => {
    const fetchMock = mockApi({
      '/api/v1/health': { body: { status: 'ok', version: '0.1.0' } },
      '/api/v1/me/organizations': { body: { data: ORGS } },
    })
    renderRoute('/')
    const select = await screen.findByLabelText('Organization')
    expect(select).toHaveValue('org-a')
    expect(screen.getByText('technician')).toBeInTheDocument()
    await apiFetch('/teams').catch(() => undefined)
    expect(lastOrgHeader(fetchMock)).toBe('org-a')

    await userEvent.selectOptions(select, 'org-b')
    expect(localStorage.getItem('nexora.activeOrganizationId')).toBe('org-b')
    expect(screen.getByText('org admin')).toBeInTheDocument()
    await apiFetch('/teams').catch(() => undefined)
    expect(lastOrgHeader(fetchMock)).toBe('org-b')
  })

  it('evicts tenant queries but keeps identity queries when switching', async () => {
    mockApi({
      '/api/v1/health': { body: { status: 'ok', version: '0.1.0' } },
      '/api/v1/me/organizations': { body: { data: ORGS } },
    })
    // Observer-less seeded data would be garbage-collected immediately with the default gcTime of 0.
    const client = new QueryClient({ defaultOptions: { queries: { retry: false, gcTime: Infinity } } })
    client.setQueryData(['teams', 'list'], { data: [] })
    renderRoute('/', { queryClient: client })
    const select = await screen.findByLabelText('Organization')
    expect(client.getQueryData(['me', 'organizations'])).toBeDefined()
    expect(client.getQueryData(['teams', 'list'])).toBeDefined()

    await userEvent.selectOptions(select, 'org-b')
    expect(client.getQueryData(['teams', 'list'])).toBeUndefined()
    expect(client.getQueryData(['me', 'organizations'])).toBeDefined()
  })

  it('restores the saved organization when it is still valid', async () => {
    localStorage.setItem('nexora.activeOrganizationId', 'org-b')
    mockApi({
      '/api/v1/health': { body: { status: 'ok', version: '0.1.0' } },
      '/api/v1/me/organizations': { body: { data: ORGS } },
    })
    renderRoute('/')
    expect(await screen.findByLabelText('Organization')).toHaveValue('org-b')
  })

  it('shows the no-organization screen when the user has no memberships', async () => {
    mockApi({ '/api/v1/me/organizations': { body: { data: [] } } })
    renderRoute('/')
    expect(await screen.findByRole('heading', { name: 'No organization yet' })).toBeInTheDocument()
    expect(screen.getByText(/tech@a\.io/)).toBeInTheDocument()
  })

  it('shows an error with retry when organizations fail to load', async () => {
    mockApi({ '/api/v1/me/organizations': { status: 500, body: { detail: 'Internal server error', code: 'INTERNAL_ERROR' } } })
    renderRoute('/')
    expect(await screen.findByRole('alert')).toHaveTextContent('Internal server error')
    expect(screen.getByRole('button', { name: 'Retry' })).toBeInTheDocument()
  })

  it('signs out from the top bar', async () => {
    mockApi({ '/api/v1/me/organizations': { body: { data: ORGS } }, '/api/v1/health': { body: { status: 'ok', version: '0.1.0' } } })
    renderRoute('/')
    await userEvent.click(await screen.findByRole('button', { name: 'Sign out' }))
    expect(await screen.findByRole('heading', { name: 'Sign in to Nexora' })).toBeInTheDocument()
  })
})
