import { useQueryClient } from '@tanstack/react-query'
import { createContext, type ReactNode, useContext, useEffect, useMemo, useRef, useState } from 'react'

import { configureApiAuth } from '@/api/client'

import type { AuthAdapter, AuthUser } from './adapter'

type Status = 'loading' | 'signed-in' | 'signed-out'

interface AuthContextValue {
  status: Status
  user: AuthUser | null
  signIn: AuthAdapter['signIn']
  signUp: AuthAdapter['signUp']
  signOut: AuthAdapter['signOut']
}

const AuthContext = createContext<AuthContextValue | null>(null)

export function AuthProvider({ adapter, children }: { adapter: AuthAdapter; children: ReactNode }) {
  const queryClient = useQueryClient()
  const [state, setState] = useState<{ status: Status; user: AuthUser | null }>({ status: 'loading', user: null })
  const lastUid = useRef<string | null | undefined>(undefined)

  useEffect(() => {
    configureApiAuth(() => adapter.getIdToken())
    return adapter.onChange((user) => {
      const uid = user?.uid ?? null
      // A different (or no) user must never see the previous user's cached data.
      if (lastUid.current !== undefined && lastUid.current !== uid) queryClient.clear()
      lastUid.current = uid
      setState({ status: user ? 'signed-in' : 'signed-out', user })
    })
  }, [adapter, queryClient])

  const value = useMemo<AuthContextValue>(
    () => ({ ...state, signIn: adapter.signIn, signUp: adapter.signUp, signOut: adapter.signOut }),
    [state, adapter],
  )
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used inside AuthProvider')
  return ctx
}
