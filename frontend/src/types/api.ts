export interface Page<T> {
  items: T[]
  total: number
  page: number
  per_page: number
  total_pages: number
}

export interface ListParams<Field extends string> {
  page: number
  per_page: number
  sort_by: Field
  sort_order: 'asc' | 'desc'
}

export interface ApiErrorBody {
  detail?: string
  error_code?: string
  field?: string
  errors?: { loc: (string | number)[]; msg: string }[]
}
