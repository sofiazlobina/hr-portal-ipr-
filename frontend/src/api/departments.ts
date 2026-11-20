import { apiClient } from './client'
import type { ListParams, Page } from '../types/api'
import type { Department } from '../types/hr'

export type DepartmentSort = 'id' | 'name'

export const departmentsApi = {
  async getAll(params: ListParams<DepartmentSort>, signal: AbortSignal) {
    return (await apiClient.get<Page<Department>>('/departments/', { params, signal })).data
  },
}
