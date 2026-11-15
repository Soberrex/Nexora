import type { AuthAdapter, AuthUser } from '@/features/auth'

export function createFakeAuthAdapter(initial: AuthUser | null = null): AuthAdapter & { current(): AuthUser | null } {
  let user = initial
  const listeners = new Set<(u: AuthUser | null) => void>()
  const emit = () => listeners.forEach((l) => l(user))
  return {
    current: () => user,
    onChange(cb) {
      listeners.add(cb)
      cb(user)
      return () => {
        listeners.delete(cb)
      }
    },
    async signIn(email, password) {
      if (password !== 'correct-horse') throw Object.assign(new Error('bad'), { code: 'auth/invalid-credential' })
      user = { uid: `uid-${email}`, email }
      emit()
    },
    async signUp(email) {
      user = { uid: `uid-${email}`, email }
      emit()
    },
    async signOut() {
      user = null
      emit()
    },
    async getIdToken() {
      return user ? `${user.uid}|${user.email}` : null
    },
  }
}
