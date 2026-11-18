import { Building2 } from 'lucide-react'

import { Button } from '@/components/ui/Button'
import { useAuth } from '@/features/auth'

export function NoOrganizationPage() {
  const { user, signOut } = useAuth()
  return (
    <main className="flex min-h-screen items-center justify-center bg-bg px-lg">
      <div className="flex max-w-md flex-col items-center gap-md rounded-lg border border-border bg-surface p-2xl text-center shadow-card">
        <Building2 size={20} className="text-text-muted" aria-hidden="true" />
        <h1 className="text-xl">No organization yet</h1>
        <p className="text-text-muted">
          You are signed in as {user?.email}, but you are not a member of any organization. Ask an organization
          admin to add you, then reload this page.
        </p>
        <Button variant="secondary" onClick={() => void signOut()}>Sign out</Button>
      </div>
    </main>
  )
}
