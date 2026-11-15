import { useOrganization } from './OrganizationProvider'

const ROLE_LABELS = { org_admin: 'org admin', admin: 'admin', technician: 'technician', requester: 'requester' } as const

export function OrganizationSwitcher() {
  const { organizations, active, setActive } = useOrganization()
  return (
    <div className="flex items-center gap-sm">
      <label htmlFor="org-switcher" className="sr-only">Organization</label>
      <select id="org-switcher" value={active.id} onChange={(e) => setActive(e.target.value)}
        className="h-8 max-w-[220px] rounded-sm border border-border bg-surface px-sm focus:outline-none focus-visible:ring-2 focus-visible:ring-primary">
        {organizations.map((o) => (
          <option key={o.id} value={o.id}>{o.name}</option>
        ))}
      </select>
      <span className="rounded-sm bg-bg px-sm py-xs text-text-muted">{ROLE_LABELS[active.role]}</span>
    </div>
  )
}
