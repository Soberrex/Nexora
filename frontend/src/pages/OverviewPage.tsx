import { ApiStatus } from '@/features/system'

export function OverviewPage() {
  return (
    <section className="flex flex-col gap-xl">
      <header>
        <h1>Overview</h1>
        <p className="mt-xs text-text-muted">Incident, SLA and workload summaries appear here once data exists.</p>
      </header>
      <div className="rounded-lg border border-border bg-surface p-xl shadow-card">
        <h2 className="mb-md font-semibold">System status</h2>
        <ApiStatus />
      </div>
    </section>
  )
}
