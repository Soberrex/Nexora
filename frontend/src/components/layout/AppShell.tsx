import { LogOut, Menu, Settings, X } from 'lucide-react'
import { useEffect, useState } from 'react'
import { NavLink, Outlet, useLocation } from 'react-router-dom'

import { primaryNav } from '@/components/layout/navigation'
import { useAuth } from '@/features/auth'
import { OrganizationSwitcher } from '@/features/organizations'
import { cn } from '@/lib/cn'

function navClass({ isActive }: { isActive: boolean }) {
  return cn(
    'flex items-center gap-md rounded-sm px-md py-sm text-sidebar-text transition hover:text-white',
    'focus:outline-none focus-visible:ring-2 focus-visible:ring-primary',
    isActive && 'bg-sidebar-active text-white',
  )
}

function Sidebar({ onNavigate }: { onNavigate?: () => void }) {
  return (
    <div className="flex h-full flex-col bg-sidebar px-md py-lg">
      <div className="px-md pb-xl text-lg font-semibold tracking-tight text-white">Nexora</div>
      <nav aria-label="Primary" className="flex flex-1 flex-col gap-xs">
        {primaryNav.map(({ label, to, icon: Icon }) => (
          <NavLink key={to} to={to} end={to === '/'} className={navClass} onClick={onNavigate}>
            <Icon size={18} aria-hidden="true" />
            {label}
          </NavLink>
        ))}
      </nav>
      <div className="border-t border-white/10 pt-md">
        <NavLink to="/settings" className={navClass} onClick={onNavigate}>
          <Settings size={18} aria-hidden="true" />
          Settings
        </NavLink>
      </div>
    </div>
  )
}

export function AppShell() {
  const [drawerOpen, setDrawerOpen] = useState(false)
  const location = useLocation()
  const { user, signOut } = useAuth()

  useEffect(() => setDrawerOpen(false), [location.pathname])

  useEffect(() => {
    if (!drawerOpen) return
    const onKey = (e: KeyboardEvent) => e.key === 'Escape' && setDrawerOpen(false)
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [drawerOpen])

  return (
    <div className="min-h-screen md:pl-[240px]">
      <aside className="fixed inset-y-0 left-0 hidden w-[240px] md:block">
        <Sidebar />
      </aside>

      {drawerOpen && (
        <div className="fixed inset-0 z-40 md:hidden" role="dialog" aria-modal="true" aria-label="Navigation">
          <div className="absolute inset-0 bg-black/50" onClick={() => setDrawerOpen(false)} />
          <div className="relative h-full w-[240px]">
            <Sidebar onNavigate={() => setDrawerOpen(false)} />
          </div>
        </div>
      )}

      <header className="sticky top-0 z-30 flex h-16 items-center gap-md border-b border-border bg-surface px-xl">
        <button
          type="button"
          className="rounded-sm p-xs md:hidden focus:outline-none focus-visible:ring-2 focus-visible:ring-primary"
          aria-label={drawerOpen ? 'Close navigation' : 'Open navigation'}
          onClick={() => setDrawerOpen((open) => !open)}
        >
          {drawerOpen ? <X size={20} /> : <Menu size={20} />}
        </button>
        <OrganizationSwitcher />
        <div className="ml-auto flex items-center gap-md">
          <span className="hidden text-text-muted sm:inline">{user?.email}</span>
          <button type="button" onClick={() => void signOut()} aria-label="Sign out"
            className="rounded-sm p-xs text-text-muted hover:text-text-primary focus:outline-none focus-visible:ring-2 focus-visible:ring-primary">
            <LogOut size={18} aria-hidden="true" />
          </button>
        </div>
      </header>

      <main className="mx-auto max-w-content p-[28px]">
        <Outlet />
      </main>
    </div>
  )
}
