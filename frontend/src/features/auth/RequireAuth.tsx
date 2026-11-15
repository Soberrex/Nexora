import type { ReactNode } from 'react'
import { Navigate, useLocation } from 'react-router-dom'

import { Spinner } from '@/components/ui/Spinner'

import { useAuth } from './AuthProvider'

export function RequireAuth({ children }: { children: ReactNode }) {
  const { status } = useAuth()
  const location = useLocation()
  if (status === 'loading') {
    return (
      <div role="status" className="flex min-h-screen items-center justify-center gap-sm text-text-muted">
        <Spinner /> Loading…
      </div>
    )
  }
  if (status === 'signed-out') {
    const next = encodeURIComponent(location.pathname + location.search)
    return <Navigate to={`/sign-in?next=${next}`} replace />
  }
  return <>{children}</>
}
