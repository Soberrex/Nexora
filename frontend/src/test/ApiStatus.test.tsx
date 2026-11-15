import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'

import { ApiStatus } from '@/features/system'
import { mockFetchJson, renderWithQuery } from '@/test/render'

describe('ApiStatus', () => {
  it('shows a loading state, then the connected version', async () => {
    mockFetchJson(200, { status: 'ok', version: '0.1.0' })
    renderWithQuery(<ApiStatus />)
    expect(screen.getByRole('status')).toHaveTextContent(/connecting/i)
    expect(await screen.findByText(/API connected \(version 0\.1\.0\)/)).toBeInTheDocument()
  })

  it('shows an error with a working retry', async () => {
    const fetchMock = mockFetchJson(503, { detail: 'Service unavailable', code: null })
    renderWithQuery(<ApiStatus />)
    expect(await screen.findByRole('alert')).toHaveTextContent('Service unavailable')

    fetchMock.mockResolvedValueOnce(
      new Response(JSON.stringify({ status: 'ok', version: '0.1.0' }), { status: 200 }),
    )
    await userEvent.click(screen.getByRole('button', { name: 'Retry' }))
    expect(await screen.findByText(/API connected/)).toBeInTheDocument()
  })
})
