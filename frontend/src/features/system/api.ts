import { useQuery } from '@tanstack/react-query'

import { apiFetch } from '@/api/client'

export interface HealthResponse {
  status: string
  version: string
}

export const systemKeys = {
  health: ['system', 'health'] as const,
}

export function fetchHealth(): Promise<HealthResponse> {
  return apiFetch<HealthResponse>('/health')
}

export function useHealth() {
  return useQuery({ queryKey: systemKeys.health, queryFn: fetchHealth })
}
