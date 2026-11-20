import { useCallback, useEffect, useRef, useState } from 'react'
import type { ReactNode } from 'react'
import { NotificationContext } from '../../hooks/useNotification'
import type { NotificationKind } from '../../hooks/useNotification'
import styles from './Notifications.module.css'

interface Notification {
  id: number
  message: string
  kind: NotificationKind
}

export function NotificationProvider({ children }: { children: ReactNode }) {
  const [items, setItems] = useState<Notification[]>([])
  const nextId = useRef(0)
  const timers = useRef(new Map<number, ReturnType<typeof setTimeout>>())

  const dismiss = useCallback((id: number) => {
    clearTimeout(timers.current.get(id))
    timers.current.delete(id)
    setItems((current) => current.filter((item) => item.id !== id))
  }, [])

  const notify = useCallback((message: string, kind: NotificationKind) => {
    const id = ++nextId.current
    setItems((current) => [...current, { id, message, kind }])
    timers.current.set(id, setTimeout(() => dismiss(id), 5500))
  }, [dismiss])

  useEffect(() => {
    const activeTimers = timers.current
    return () => {
      for (const timer of activeTimers.values()) clearTimeout(timer)
      activeTimers.clear()
    }
  }, [])

  return (
    <NotificationContext.Provider value={notify}>
      {children}
      <div className={styles.stack}>
        {items.map(({ id, kind, message }) => (
          <div className={`${styles.toast} ${styles[kind]}`} key={id}>
            <span role={kind === 'error' ? 'alert' : 'status'}>{message}</span>
            <button type="button" onClick={() => dismiss(id)} aria-label="Закрыть уведомление">×</button>
          </div>
        ))}
      </div>
    </NotificationContext.Provider>
  )
}
