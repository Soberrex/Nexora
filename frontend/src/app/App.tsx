import { BrowserRouter } from 'react-router-dom'

import { AppProviders } from '@/app/providers'
import { AppRoutes, routerFuture } from '@/app/routes'
import { createFirebaseAuthAdapter } from '@/features/auth/firebaseAdapter'

const authAdapter = createFirebaseAuthAdapter()

export function App() {
  return (
    <AppProviders adapter={authAdapter}>
      <BrowserRouter future={routerFuture}>
        <AppRoutes />
      </BrowserRouter>
    </AppProviders>
  )
}
