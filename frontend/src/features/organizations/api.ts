import { useQuery } from '@tanstack/react-query'

import { apiFetch } from '@/api/client'
import { useAuth } from '@/features/auth'

export interface MyOrganization {
  id: string
  name: string
  role: 'org_admin' | 'admin' | 'technician' | 'requester'
}

export const organizationKeys = { mine: ['me', 'organizations'] as const }

export function fetchMyOrganizations(): Promise<{ data: MyOrganization[] }> {
  return apiFetch<{ data: MyOrganization[] }>('/me/organizations')
}

export function useMyOrganizations() {
  const { status } = useAuth()
  return useQuery({ queryKey: organizationKeys.mine, queryFn: fetchMyOrganizations, enabled: status === 'signed-in' })
}
