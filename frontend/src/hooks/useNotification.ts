import { createContext, useContext } from 'react'

export type NotificationKind = 'success' | 'error' | 'info'
export const NotificationContext = createContext<((message: string, kind: NotificationKind) => void) | null>(null)

export function useNotification() {
  const notify = useContext(NotificationContext)
  if (!notify) throw new Error('NotificationProvider is required')
  return notify
}
