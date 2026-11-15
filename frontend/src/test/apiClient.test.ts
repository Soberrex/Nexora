import { ApiError, apiFetch } from '@/api/client'
import { mockFetchJson } from '@/test/render'

describe('apiFetch', () => {
  it('prefixes /api/v1 and returns parsed JSON', async () => {
    const fetchMock = mockFetchJson(200, { status: 'ok', version: '0.1.0' })
    await expect(apiFetch('/health')).resolves.toEqual({ status: 'ok', version: '0.1.0' })
    expect(fetchMock).toHaveBeenCalledWith('/api/v1/health', expect.any(Object))
  })

  it('maps the standard error body to ApiError', async () => {
    mockFetchJson(409, { detail: 'Invalid transition', code: 'INVALID_STATUS_TRANSITION' })
    const error = await apiFetch('/incidents/1').catch((e: unknown) => e)
    expect(error).toBeInstanceOf(ApiError)
    expect(error).toMatchObject({ status: 409, message: 'Invalid transition', code: 'INVALID_STATUS_TRANSITION' })
  })

  it('reports network failures as NETWORK_ERROR', async () => {
    vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new TypeError('Failed to fetch')))
    await expect(apiFetch('/health')).rejects.toMatchObject({ status: 0, code: 'NETWORK_ERROR' })
  })
})
