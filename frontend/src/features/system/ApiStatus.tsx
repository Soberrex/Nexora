import { AlertTriangle, CheckCircle2 } from 'lucide-react'

import { Button } from '@/components/ui/Button'
import { Spinner } from '@/components/ui/Spinner'
import { useHealth } from '@/features/system/api'

/** Shows live backend health. Render Free cold starts can take ~30-60s on first request. */
export function ApiStatus() {
  const { data, isPending, isError, error, refetch, isFetching } = useHealth()

  if (isPending) {
    return (
      <div role="status" className="flex items-center gap-sm text-text-muted">
        <Spinner /> Connecting to the Nexora API… the server may be waking up.
      </div>
    )
  }

  if (isError) {
    return (
      <div role="alert" className="flex flex-wrap items-center gap-md rounded-md bg-red-50 px-lg py-md text-red-700">
        <AlertTriangle size={18} aria-hidden="true" />
        <span>API unavailable: {error.message}</span>
        <Button variant="secondary" size="sm" onClick={() => void refetch()} loading={isFetching}>
          Retry
        </Button>
      </div>
    )
  }

  return (
    <div role="status" className="flex items-center gap-sm text-text-primary">
      <CheckCircle2 size={18} className="text-green-600" aria-hidden="true" />
      API connected (version {data.version})
    </div>
  )
}
