import { type FormEvent, useState } from 'react'
import { Navigate, useSearchParams } from 'react-router-dom'

import { Button } from '@/components/ui/Button'
import { authErrorMessage, useAuth } from '@/features/auth'

function safeNext(next: string | null): string {
  return next && next.startsWith('/') && !next.startsWith('//') ? next : '/'
}

export function SignInPage() {
  const { status, signIn, signUp } = useAuth()
  const [params] = useSearchParams()
  const [mode, setMode] = useState<'sign-in' | 'sign-up'>('sign-in')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)

  if (status === 'signed-in') return <Navigate to={safeNext(params.get('next'))} replace />

  async function onSubmit(event: FormEvent) {
    event.preventDefault()
    setError(null)
    setBusy(true)
    try {
      await (mode === 'sign-in' ? signIn(email.trim(), password) : signUp(email.trim(), password))
    } catch (err) {
      setError(authErrorMessage(err))
    } finally {
      setBusy(false)
    }
  }

  const isSignIn = mode === 'sign-in'
  return (
    <main className="flex min-h-screen items-center justify-center bg-bg px-lg">
      <div className="w-full max-w-sm rounded-lg border border-border bg-surface p-xl shadow-card">
        <div className="mb-lg text-lg font-semibold">Nexora</div>
        <h1 className="mb-xl">{isSignIn ? 'Sign in to Nexora' : 'Create your account'}</h1>
        <form className="flex flex-col gap-lg" onSubmit={onSubmit} noValidate>
          <div className="flex flex-col gap-xs">
            <label htmlFor="email" className="font-medium">Email</label>
            <input id="email" type="email" autoComplete="email" required value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="h-9 rounded-sm border border-border px-md focus:outline-none focus-visible:ring-2 focus-visible:ring-primary" />
          </div>
          <div className="flex flex-col gap-xs">
            <label htmlFor="password" className="font-medium">Password</label>
            <input id="password" type="password" required minLength={6} value={password}
              autoComplete={isSignIn ? 'current-password' : 'new-password'}
              onChange={(e) => setPassword(e.target.value)}
              className="h-9 rounded-sm border border-border px-md focus:outline-none focus-visible:ring-2 focus-visible:ring-primary" />
          </div>
          {error && (
            <p role="alert" className="rounded-sm bg-red-50 px-md py-sm text-red-700">{error}</p>
          )}
          <Button type="submit" loading={busy} disabled={!email || !password}>
            {isSignIn ? 'Sign in' : 'Create account'}
          </Button>
        </form>
        <p className="mt-lg text-text-muted">
          {isSignIn ? 'New to Nexora?' : 'Already have an account?'}{' '}
          <button type="button" className="font-medium text-primary hover:underline"
            onClick={() => { setMode(isSignIn ? 'sign-up' : 'sign-in'); setError(null) }}>
            {isSignIn ? 'Create an account' : 'Sign in instead'}
          </button>
        </p>
      </div>
    </main>
  )
}
