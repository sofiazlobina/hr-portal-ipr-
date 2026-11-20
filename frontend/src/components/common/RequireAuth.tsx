import { Navigate, Outlet, useLocation } from 'react-router-dom'
import { useAuth } from '../../hooks/useAuth'

export function RequireAuth() {
  const { user } = useAuth()
  const { pathname, search } = useLocation()
  return user ? <Outlet /> : <Navigate to="/login" state={{ from: pathname + search }} replace />
}
