import { useEffect, useState } from 'react'
import type { ReactNode } from 'react'
import { login } from '../../api/auth'
import { onSessionExpired, setAccessToken } from '../../api/client'
import { AuthContext } from '../../hooks/useAuth'
import { useNotification } from '../../hooks/useNotification'
import type { User } from '../../types/hr'

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const notify = useNotification()

  useEffect(() => onSessionExpired(() => {
    setUser(null)
    notify('Срок действия сеанса истёк. Войдите снова.', 'info')
  }), [notify])

  async function signIn(email: string, password: string) {
    const session = await login(email, password)
    setAccessToken(session.accessToken)
    setUser(session.user)
  }

  function signOut() {
    setAccessToken(null)
    setUser(null)
  }

  return <AuthContext.Provider value={{ user, signIn, signOut }}>{children}</AuthContext.Provider>
}
