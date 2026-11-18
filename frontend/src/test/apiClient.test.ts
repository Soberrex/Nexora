import { ApiError, apiFetch, configureApiAuth, setApiOrganizationId } from '@/api/client'
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

describe('apiFetch auth headers', () => {
  afterEach(() => {
    configureApiAuth(async () => null)
    setApiOrganizationId(null)
  })

  it('sends the bearer token and active organization', async () => {
    const fetchMock = mockFetchJson(200, {})
    configureApiAuth(async () => 'token-123')
    setApiOrganizationId('org-9')
    await apiFetch('/teams')
    const headers = fetchMock.mock.calls[0]![1].headers as Headers
    expect(headers.get('Authorization')).toBe('Bearer token-123')
    expect(headers.get('X-Organization-ID')).toBe('org-9')
  })

  it('sends no auth headers when signed out', async () => {
    const fetchMock = mockFetchJson(200, {})
    await apiFetch('/health')
    const headers = fetchMock.mock.calls[0]![1].headers as Headers
    expect(headers.has('Authorization')).toBe(false)
    expect(headers.has('X-Organization-ID')).toBe(false)
  })
})
