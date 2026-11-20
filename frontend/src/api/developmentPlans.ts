import { apiClient } from './client'
import type { ListParams, Page } from '../types/api'
import type { DevelopmentPlan, PlanPeriod, PlanStatus } from '../types/hr'

export type PlanSort = 'id' | 'status' | 'start_date' | 'created_at'

export interface PlanFilters {
  status_filter?: PlanStatus
  start_date_from?: string
  start_date_to?: string
  search?: string
}

export const developmentPlansApi = {
  async getAll(params: ListParams<PlanSort> & PlanFilters, signal: AbortSignal) {
    return (await apiClient.get<Page<DevelopmentPlan>>('/development-plans/', { params, signal })).data
  },
  async getById(id: number, signal: AbortSignal) {
    return (await apiClient.get<DevelopmentPlan>(`/development-plans/${id}`, { signal })).data
  },
  async create(values: PlanPeriod & { employee_id: number }) {
    return (await apiClient.post<DevelopmentPlan>('/development-plans/', values)).data
  },
  async update(id: number, values: PlanPeriod) {
    return (await apiClient.put<DevelopmentPlan>(`/development-plans/${id}`, values)).data
  },
  async delete(id: number) {
    await apiClient.delete(`/development-plans/${id}`)
  },
}
