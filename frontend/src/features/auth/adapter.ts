export interface AuthUser {
  uid: string
  email: string
}

/** Boundary around the identity provider so components and tests never import Firebase. */
export interface AuthAdapter {
  onChange(callback: (user: AuthUser | null) => void): () => void
  signIn(email: string, password: string): Promise<void>
  signUp(email: string, password: string): Promise<void>
  signOut(): Promise<void>
  getIdToken(): Promise<string | null>
}
