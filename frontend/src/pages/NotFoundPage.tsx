import { Link } from 'react-router-dom'

export function NotFoundPage() {
  return (
    <section className="flex flex-col items-start gap-md">
      <h1>Page not found</h1>
      <p className="text-text-muted">The page you requested does not exist.</p>
      <Link to="/" className="font-medium text-primary hover:underline">
        Back to Overview
      </Link>
    </section>
  )
}
