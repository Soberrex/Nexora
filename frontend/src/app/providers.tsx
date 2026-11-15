import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { type ReactNode, useState } from 'react'

import { type AuthAdapter, AuthProvider } from '@/features/auth'

export function createQueryClient(): QueryClient {
  return new QueryClient({
    defaultOptions: { queries: { staleTime: 30_000, retry: 1, refetchOnWindowFocus: false } },
  })
}

export function AppProviders({ adapter, children }: { adapter: AuthAdapter; children: ReactNode }) {
  const [client] = useState(createQueryClient)
  return (
    <QueryClientProvider client={client}>
      <AuthProvider adapter={adapter}>{children}</AuthProvider>
    </QueryClientProvider>
  )
}
