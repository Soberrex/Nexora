import type { RouteObject } from 'react-router-dom'

import { AppShell } from '@/components/layout/AppShell'
import { ComingSoonPage } from '@/pages/ComingSoonPage'
import { NotFoundPage } from '@/pages/NotFoundPage'
import { OverviewPage } from '@/pages/OverviewPage'

export const routes: RouteObject[] = [
  {
    path: '/',
    element: <AppShell />,
    children: [
      { index: true, element: <OverviewPage /> },
      { path: 'incidents', element: <ComingSoonPage title="Incidents" milestone="M2" /> },
      { path: 'my-work', element: <ComingSoonPage title="My Work" milestone="M3" /> },
      { path: 'teams', element: <ComingSoonPage title="Teams" milestone="M1" /> },
      { path: 'workflows', element: <ComingSoonPage title="Workflows" milestone="M5" /> },
      { path: 'knowledge', element: <ComingSoonPage title="Knowledge Base" milestone="M6" /> },
      { path: 'assistant', element: <ComingSoonPage title="AI Assistant" milestone="M6" /> },
      { path: 'reports', element: <ComingSoonPage title="Reports" milestone="M7" /> },
      { path: 'settings', element: <ComingSoonPage title="Settings" milestone="M1" /> },
      { path: '*', element: <NotFoundPage /> },
    ],
  },
]

// Opt in to React Router v7 behaviour now to avoid a breaking upgrade later.
export const routerFuture = { v7_startTransition: true, v7_relativeSplatPath: true } as const
