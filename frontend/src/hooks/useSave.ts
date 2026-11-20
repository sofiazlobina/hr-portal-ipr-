import { useEffect, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { errorMessage } from '../api/client'
import { useNotification } from './useNotification'

export function useSave(returnTo: string) {
  const navigate = useNavigate()
  const notify = useNotification()
  const mounted = useRef(false)
  const inFlight = useRef(false)
  const [pending, setPending] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    mounted.current = true
    return () => { mounted.current = false }
  }, [])

  async function save(request: () => Promise<unknown>, message: string) {
    if (inFlight.current) return
    inFlight.current = true
    setPending(true)
    setError('')
    try {
      await request()
      notify(message, 'success')
      if (mounted.current) navigate(returnTo)
    } catch (cause) {
      const detail = errorMessage(cause)
      notify(detail, 'error')
      if (mounted.current) setError(detail)
    } finally {
      inFlight.current = false
      if (mounted.current) setPending(false)
    }
  }

  return { pending, error, save }
}
