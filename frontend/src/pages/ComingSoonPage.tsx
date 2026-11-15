import { Construction } from 'lucide-react'

export function ComingSoonPage({ title, milestone }: { title: string; milestone: string }) {
  return (
    <section className="flex flex-col gap-xl">
      <h1>{title}</h1>
      <div className="flex flex-col items-center gap-sm rounded-lg border border-border bg-surface p-2xl text-center shadow-card">
        <Construction size={20} className="text-text-muted" aria-hidden="true" />
        <p className="font-medium">Not built yet</p>
        <p className="text-text-muted">This area is planned for milestone {milestone}.</p>
      </div>
    </section>
  )
}
