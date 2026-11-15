import { Loader2 } from 'lucide-react'

export function Spinner({ size = 16, label }: { size?: number; label?: string }) {
  return (
    <Loader2
      size={size}
      className="animate-spin"
      aria-hidden={label ? undefined : true}
      aria-label={label}
      role={label ? 'img' : undefined}
    />
  )
}
