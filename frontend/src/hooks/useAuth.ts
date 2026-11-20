import { createContext, useContext } from 'react'
import type { User } from '../types/hr'

export const AuthContext = createContext<{
  user: User | null
  signIn: (email: string, password: string) => Promise<void>
  signOut: () => void
} | null>(null)

export function useAuth() {
  const auth = useContext(AuthContext)
  if (!auth) throw new Error('AuthProvider is required')
  return auth
}
