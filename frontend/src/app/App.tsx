import { BrowserRouter, useRoutes } from 'react-router-dom'

import { AppProviders } from '@/app/providers'
import { routerFuture, routes } from '@/app/routes'

export function AppRoutes() {
  return useRoutes(routes)
}

export function App() {
  return (
    <AppProviders>
      <BrowserRouter future={routerFuture}>
        <AppRoutes />
      </BrowserRouter>
    </AppProviders>
  )
}
