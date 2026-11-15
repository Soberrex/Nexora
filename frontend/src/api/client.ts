export interface ApiErrorBody {
  detail: unknown
  code?: string | null
}

export class ApiError extends Error {
  readonly status: number
  readonly code: string | null

  constructor(status: number, message: string, code: string | null = null) {
    super(message)
    this.name = 'ApiError'
    this.status = status
    this.code = code
  }
}

const BASE_URL = (import.meta.env.VITE_API_BASE_URL ?? '').replace(/\/$/, '')

function messageFrom(body: unknown, fallback: string): { message: string; code: string | null } {
  if (body && typeof body === 'object' && 'detail' in body) {
    const { detail, code } = body as ApiErrorBody
    return { message: typeof detail === 'string' ? detail : fallback, code: code ?? null }
  }
  return { message: fallback, code: null }
}

/**
 * Typed fetch wrapper for the Nexora REST API (/api/v1).
 * Auth (Firebase ID token) and X-Organization-ID headers are added here in M1.
 */
export async function apiFetch<T>(path: string, init: RequestInit = {}): Promise<T> {
  const headers = new Headers(init.headers)
  headers.set('Accept', 'application/json')
  if (init.body && !headers.has('Content-Type')) headers.set('Content-Type', 'application/json')

  let response: Response
  try {
    response = await fetch(`${BASE_URL}/api/v1${path}`, { ...init, headers })
  } catch {
    throw new ApiError(0, 'Unable to reach the Nexora API', 'NETWORK_ERROR')
  }

  const body: unknown = await response.json().catch(() => null)
  if (!response.ok) {
    const { message, code } = messageFrom(body, `Request failed (${response.status})`)
    throw new ApiError(response.status, message, code)
  }
  return body as T
}
