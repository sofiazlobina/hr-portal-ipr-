import { useState } from 'react'
import type { FormEvent } from 'react'
import { Navigate, useLocation } from 'react-router-dom'
import { errorMessage } from '../api/client'
import { Button } from '../components/ui/Button'
import { Input } from '../components/ui/Input'
import { useAuth } from '../hooks/useAuth'
import styles from '../components/common/Workspace.module.css'

export function Login() {
  const { user, signIn } = useAuth()
  const { state } = useLocation()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [pending, setPending] = useState(false)
  const destination = typeof state?.from === 'string' && /^\/(?![\s/\\])/.test(state.from) ? state.from : '/development-plans'

  if (user) return <Navigate to={destination} replace />

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    if (pending) return
    setPending(true)
    setError('')
    try {
      await signIn(email.trim(), password)
    } catch (cause) {
      setError(errorMessage(cause))
    } finally {
      setPending(false)
    }
  }

  return (
    <>
      <div className={styles.heading}>
        <div><h1>Вход в HR-портал</h1><p>Используйте рабочую почту и пароль.</p></div>
      </div>
      <form className={`${styles.panel} ${styles.form}`} onSubmit={handleSubmit} aria-busy={pending}>
        <fieldset disabled={pending}>
          <Input label="Рабочая почта" name="username" type="email" autoComplete="username" required value={email} onChange={(event) => setEmail(event.target.value)} />
          <Input label="Пароль" name="password" type="password" autoComplete="current-password" required value={password} onChange={(event) => setPassword(event.target.value)} />
        </fieldset>
        {error && <p role="alert" className={styles.formError}>{error}</p>}
        <div className={styles.actions}><Button type="submit" disabled={pending}>{pending ? 'Вход…' : 'Войти'}</Button></div>
      </form>
    </>
  )
}
