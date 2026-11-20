import { useRef, useState } from 'react'
import { errorMessage } from '../api/client'
import { useNotification } from './useNotification'

export function useDelete(remove: (id: number) => Promise<void>, refresh: () => void, successMessage: string) {
  const [deletingId, setDeletingId] = useState<number | null>(null)
  const busy = useRef(false)
  const notify = useNotification()

  async function deleteRecord(id: number, confirmation: string) {
    if (busy.current || !window.confirm(confirmation)) return
    busy.current = true
    setDeletingId(id)
    try {
      await remove(id)
      refresh()
      notify(successMessage, 'success')
    } catch (error) {
      notify(errorMessage(error), 'error')
    } finally {
      busy.current = false
      setDeletingId(null)
    }
  }

  return { deletingId, deleteRecord }
}
