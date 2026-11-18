import { useQueryClient } from '@tanstack/react-query'
import { createContext, type ReactNode, useCallback, useContext, useMemo, useState } from 'react'

import { setApiOrganizationId } from '@/api/client'
import { Button } from '@/components/ui/Button'
import { Spinner } from '@/components/ui/Spinner'
import { NoOrganizationPage } from '@/pages/NoOrganizationPage'

import { type MyOrganization, useMyOrganizations } from './api'

const STORAGE_KEY = 'nexora.activeOrganizationId'

function readStored(): string | null {
  try {
    return localStorage.getItem(STORAGE_KEY)
  } catch {
    return null
  }
}

function writeStored(id: string): void {
  try {
    localStorage.setItem(STORAGE_KEY, id)
  } catch {
    // Storage unavailable (private mode); the choice just isn't remembered.
  }
}

interface OrganizationContextValue {
  organizations: MyOrganization[]
  active: MyOrganization
  setActive(id: string): void
}

const OrganizationContext = createContext<OrganizationContextValue | null>(null)

export function OrganizationProvider({ children }: { children: ReactNode }) {
  const queryClient = useQueryClient()
  const { data, isPending, isError, error, refetch, isFetching } = useMyOrganizations()
  const [selectedId, setSelectedId] = useState<string | null>(readStored)

  const organizations = useMemo(() => data?.data ?? [], [data])
  const active = organizations.find((o) => o.id === selectedId) ?? organizations[0] ?? null

  // Set synchronously during render so children's first requests already carry the header.
  setApiOrganizationId(active?.id ?? null)

  const setActive = useCallback(
    (id: string) => {
      setSelectedId(id)
      writeStored(id)
      setApiOrganizationId(id)
      // Tenant data from the previous organization must not be shown under the new one.
      queryClient.removeQueries({ predicate: (q) => q.queryKey[0] !== 'me' && q.queryKey[0] !== 'system' })
    },
    [queryClient],
  )

  if (isPending) {
    return (
      <div role="status" className="flex min-h-screen items-center justify-center gap-sm text-text-muted">
        <Spinner /> Loading your organizations…
      </div>
    )
  }
  if (isError) {
    return (
      <div className="flex min-h-screen items-center justify-center px-lg">
        <div role="alert" className="flex flex-wrap items-center gap-md rounded-md bg-red-50 px-lg py-md text-red-700">
          <span>Could not load your organizations: {error.message}</span>
          <Button variant="secondary" size="sm" onClick={() => void refetch()} loading={isFetching}>
            Retry
          </Button>
        </div>
      </div>
    )
  }
  if (!active) return <NoOrganizationPage />

  return (
    <OrganizationContext.Provider value={{ organizations, active, setActive }}>{children}</OrganizationContext.Provider>
  )
}

export function useOrganization(): OrganizationContextValue {
  const ctx = useContext(OrganizationContext)
  if (!ctx) throw new Error('useOrganization must be used inside OrganizationProvider')
  return ctx
}
