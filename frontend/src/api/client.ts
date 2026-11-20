import axios from 'axios'
import type { ApiErrorBody } from '../types/api'

export class ApiError extends Error {
  readonly status?: number

  constructor(message: string, status?: number) {
    super(message)
    this.name = 'ApiError'
    this.status = status
  }
}

export const apiClient = axios.create({
  baseURL: '/api',
  timeout: 12_000,
  headers: { Accept: 'application/json' },
})

let token: string | null = null
const expiryListeners = new Set<() => void>()

export function setAccessToken(value: string | null) {
  token = value
}

export function onSessionExpired(listener: () => void) {
  expiryListeners.add(listener)
  return () => { expiryListeners.delete(listener) }
}

apiClient.interceptors.request.use((request) => {
  if (token && !request.headers.has('Authorization')) {
    request.headers.set('Authorization', `Bearer ${token}`)
  }
  return request
})

apiClient.interceptors.response.use(
  (response) => response,
  (error: unknown) => {
    if (axios.isCancel(error) || !axios.isAxiosError<ApiErrorBody>(error)) {
      return Promise.reject(error)
    }

    const status = error.response?.status
    if (status === 401 && token && error.config?.headers.get('Authorization') === `Bearer ${token}`) {
      setAccessToken(null)
      for (const listener of expiryListeners) listener()
    }

    const detail = error.response?.data?.detail
    let message = 'Не удалось выполнить запрос.'
    if (error.code === 'ECONNABORTED') {
      message = 'Сервер не ответил вовремя. Повторите попытку.'
    } else if (!status && error.request) {
      message = 'Нет соединения с API. Проверьте, запущен ли сервер.'
    } else if (status && status >= 500) {
      message = 'Сервер не смог выполнить запрос. Повторите попытку.'
    } else if (typeof detail === 'string' && detail) {
      message = detail
    } else if (status === 401) {
      message = 'Войдите в систему.'
    } else if (status === 403) {
      message = 'Недостаточно прав для этой операции.'
    } else if (status === 404) {
      message = 'Запись не найдена.'
    } else if (status === 422) {
      message = 'Проверьте введённые данные.'
    }
    return Promise.reject(new ApiError(message, status))
  },
)

export function errorMessage(error: unknown) {
  return error instanceof ApiError ? error.message : 'Не удалось выполнить запрос.'
}
