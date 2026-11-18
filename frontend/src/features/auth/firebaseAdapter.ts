import { initializeApp } from 'firebase/app'
import {
  type Auth,
  connectAuthEmulator,
  createUserWithEmailAndPassword,
  getAuth,
  onIdTokenChanged,
  signInWithEmailAndPassword,
  signOut,
} from 'firebase/auth'

import type { AuthAdapter } from './adapter'

let instance: Auth | null = null

function auth(): Auth {
  if (instance) return instance
  const app = initializeApp({
    apiKey: import.meta.env.VITE_FIREBASE_API_KEY,
    authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN,
    projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID,
  })
  instance = getAuth(app)
  const emulatorUrl = import.meta.env.VITE_FIREBASE_AUTH_EMULATOR_URL
  if (emulatorUrl) connectAuthEmulator(instance, emulatorUrl, { disableWarnings: true })
  return instance
}

export function createFirebaseAuthAdapter(): AuthAdapter {
  return {
    onChange(callback) {
      return onIdTokenChanged(auth(), (u) => callback(u && u.email ? { uid: u.uid, email: u.email } : null))
    },
    async signIn(email, password) {
      await signInWithEmailAndPassword(auth(), email, password)
    },
    async signUp(email, password) {
      await createUserWithEmailAndPassword(auth(), email, password)
    },
    async signOut() {
      await signOut(auth())
    },
    async getIdToken() {
      return (await auth().currentUser?.getIdToken()) ?? null
    },
  }
}
