import { apiClient } from './client'
import type { ListParams, Page } from '../types/api'
import type { Competency, CompetencyInput } from '../types/hr'

export type CompetencySort = 'id' | 'name'

export const competenciesApi = {
  async getAll(params: ListParams<CompetencySort> & { search?: string }, signal: AbortSignal) {
    return (await apiClient.get<Page<Competency>>('/competencies/', { params, signal })).data
  },
  async getById(id: number, signal: AbortSignal) {
    return (await apiClient.get<Competency>(`/competencies/${id}`, { signal })).data
  },
  async create(values: CompetencyInput) {
    return (await apiClient.post<Competency>('/competencies/', values)).data
  },
  async update(id: number, values: CompetencyInput) {
    return (await apiClient.put<Competency>(`/competencies/${id}`, values)).data
  },
  async delete(id: number) {
    await apiClient.delete(`/competencies/${id}`)
  },
}
