import { useCallback, useState } from 'react'
import type { Sort } from '../components/ui/Table'
import type { ListParams, Page } from '../types/api'
import { useRemote } from './useRemote'

const PAGE_SIZE = 10

export function useCollection<T, Field extends string, Filters extends object>(
  getAll: (params: ListParams<Field> & Filters, signal: AbortSignal) => Promise<Page<T>>,
  initialSort: NoInfer<Field>,
  initialFilters: Filters,
) {
  const [page, setPage] = useState(1)
  const [sort, setSort] = useState<Sort<Field>>({ field: initialSort, order: 'asc' })
  const [filters, setFilters] = useState(initialFilters)

  const load = useCallback(async (signal: AbortSignal) => {
    const params = { ...filters, page, per_page: PAGE_SIZE, sort_by: sort.field, sort_order: sort.order }
    const response = await getAll(params, signal)
    const lastPage = Math.max(1, response.total_pages)
    if (page > lastPage && !signal.aborted) setPage(lastPage)
    return response
  }, [getAll, filters, page, sort])

  const remote = useRemote(load)

  function applyFilters(values: Filters) {
    setFilters(values)
    setPage(1)
  }

  function changeSort(field: Field) {
    setSort((current) => ({ field, order: current.field === field && current.order === 'asc' ? 'desc' : 'asc' }))
    setPage(1)
  }

  return { ...remote, page, setPage, sort, changeSort, applyFilters }
}
