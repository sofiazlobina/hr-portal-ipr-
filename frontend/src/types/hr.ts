export type Role = 'employee' | 'manager' | 'hr'

export interface User {
  id: number
  full_name: string
  email: string
  role: Role
  department_id: number
  manager_id: number | null
  is_active: boolean
  created_at: string
}

export interface Department {
  id: number
  name: string
}

export interface CompetencyInput {
  name: string
  description: string | null
}

export interface Competency extends CompetencyInput {
  id: number
}

export const planStatuses = {
  draft: 'Черновик',
  pending: 'На согласовании',
  approved: 'Утверждён',
  rejected: 'Отклонён',
  completed: 'Завершён',
} as const

export type PlanStatus = keyof typeof planStatuses

export interface PlanPeriod {
  start_date: string
  end_date: string
}

export interface Activity {
  id: number
  goal_id: number
  type: 'course' | 'practice' | 'reading'
  description: string
  deadline: string
  status: 'planned' | 'completed'
  completion_date: string | null
}

export interface Goal {
  id: number
  plan_id: number
  description: string
  deadline: string
  is_completed: boolean
  activities: Activity[]
}

export interface PlanCompetency {
  plan_id: number
  competency_id: number
  current_level: number
  target_level: number
}

export interface DevelopmentPlan extends PlanPeriod {
  id: number
  employee_id: number
  status: PlanStatus
  manager_comment: string | null
  created_at: string
  updated_at: string
  progress: number
  goals: Goal[]
  competencies: PlanCompetency[]
}
