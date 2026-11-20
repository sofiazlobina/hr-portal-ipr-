import { useEffect, useState } from 'react'
import { ApiError, errorMessage } from '../api/client'
import { useNotification } from './useNotification'

type Result<T> = { data: T; error?: never } | { error: string; data?: never }
type Loader<T> = (signal: AbortSignal) => Promise<T>

export function useRemote<T>(load: Loader<T>) {
  const [revision, setRevision] = useState(0)
  const [snapshot, setSnapshot] = useState<{ load: Loader<T>; revision: number; result: Result<T> }>()
  const notify = useNotification()

  useEffect(() => {
    const controller = new AbortController()
    const { signal } = controller
    load(signal).then(
      (data) => {
        if (!signal.aborted) setSnapshot({ load, revision, result: { data } })
      },
      (error: unknown) => {
        if (signal.aborted) return
        const message = errorMessage(error)
        setSnapshot({ load, revision, result: { error: message } })
        if (!(error instanceof ApiError && error.status === 401)) notify(message, 'error')
      },
    )
    return () => controller.abort()
  }, [load, revision, notify])

  const result = snapshot?.load === load && snapshot.revision === revision ? snapshot.result : undefined
  return { result, refresh: () => setRevision((current) => current + 1) }
}
