import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render } from '@testing-library/react'
import type { ReactElement } from 'react'
import { MemoryRouter } from 'react-router-dom'

import { AppRoutes, routerFuture } from '@/app/routes'
import { type AuthAdapter, AuthProvider } from '@/features/auth'
import { createFakeAuthAdapter } from '@/test/fakeAuth'

export function testQueryClient(): QueryClient {
  return new QueryClient({ defaultOptions: { queries: { retry: false, gcTime: 0 } } })
}

export function renderWithQuery(ui: ReactElement) {
  return render(<QueryClientProvider client={testQueryClient()}>{ui}</QueryClientProvider>)
}

export const SIGNED_IN_USER = { uid: 'uid-tech', email: 'tech@a.io' }

export function renderRoute(path: string, { adapter }: { adapter?: AuthAdapter } = {}) {
  const auth = adapter ?? createFakeAuthAdapter(SIGNED_IN_USER)
  return render(
    <QueryClientProvider client={testQueryClient()}>
      <AuthProvider adapter={auth}>
        <MemoryRouter initialEntries={[path]} future={routerFuture}>
          <AppRoutes />
        </MemoryRouter>
      </AuthProvider>
    </QueryClientProvider>,
  )
}

export function mockFetchJson(status: number, body: unknown) {
  const fn = vi.fn().mockResolvedValue(
    new Response(JSON.stringify(body), { status, headers: { 'Content-Type': 'application/json' } }),
  )
  vi.stubGlobal('fetch', fn)
  return fn
}

type MockRoute = { status?: number; body: unknown }

/** Route fetch calls by pathname; unknown paths return 404 in the standard error shape. */
export function mockApi(routes: Record<string, MockRoute>) {
  const fn = vi.fn(async (input: RequestInfo | URL) => {
    const path = new URL(String(input), 'http://localhost').pathname
    const route = routes[path] ?? { status: 404, body: { detail: 'Not Found', code: null } }
    return new Response(JSON.stringify(route.body), {
      status: route.status ?? 200,
      headers: { 'Content-Type': 'application/json' },
    })
  })
  vi.stubGlobal('fetch', fn)
  return fn
}
