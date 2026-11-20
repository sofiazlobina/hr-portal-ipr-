import { useState } from 'react'
import type { FormEvent } from 'react'
import { Link } from 'react-router-dom'
import { developmentPlansApi } from '../../api/developmentPlans'
import type { PlanFilters, PlanSort } from '../../api/developmentPlans'
import { CollectionTable } from '../../components/common/CollectionTable'
import { Button, ButtonLink } from '../../components/ui/Button'
import { Input, Select } from '../../components/ui/Input'
import type { Column } from '../../components/ui/Table'
import { useAuth } from '../../hooks/useAuth'
import { useCollection } from '../../hooks/useCollection'
import { useDelete } from '../../hooks/useDelete'
import { planStatuses } from '../../types/hr'
import type { DevelopmentPlan, PlanStatus } from '../../types/hr'
import { formatDate, formatProgress } from '../../utils/formatters'
import styles from '../../components/common/Workspace.module.css'

const initialFilters: PlanFilters = {}
const blank = { search: '', status: '' as PlanStatus | '', from: '', to: '' }
const baseColumns: Column<DevelopmentPlan, PlanSort>[] = [
  { key: 'id', title: 'ИПР', sortBy: 'id', render: (plan) => <Link to={`/development-plans/${plan.id}`}>ИПР №{plan.id}</Link> },
  { key: 'employee', title: 'ID сотрудника', render: (plan) => plan.employee_id },
  { key: 'status', title: 'Статус', sortBy: 'status', render: (plan) => <span className={styles.badge}>{planStatuses[plan.status]}</span> },
  { key: 'start', title: 'Начало', sortBy: 'start_date', render: (plan) => formatDate(plan.start_date) },
  { key: 'end', title: 'Окончание', render: (plan) => formatDate(plan.end_date) },
  { key: 'progress', title: 'Прогресс', render: (plan) => formatProgress(plan.progress) },
]

export function PlansList() {
  const { user } = useAuth()
  const [filters, setFilters] = useState(blank)
  const [filterError, setFilterError] = useState('')
  const collection = useCollection(developmentPlansApi.getAll, 'id', initialFilters)
  const { deletingId, deleteRecord } = useDelete(developmentPlansApi.delete, collection.refresh, 'Черновик ИПР удалён.')

  function applyFilters(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    const search = filters.search.trim()
    if (search.length === 1) {
      setFilterError('Введите минимум два символа для поиска.')
      return
    }
    if (filters.from && filters.to && filters.to < filters.from) {
      setFilterError('Конец интервала не может быть раньше начала.')
      return
    }
    setFilterError('')
    collection.applyFilters({
      search: search || undefined,
      status_filter: filters.status || undefined,
      start_date_from: filters.from || undefined,
      start_date_to: filters.to || undefined,
    })
  }

  function changeFilter<Key extends keyof typeof blank>(key: Key, value: (typeof blank)[Key]) {
    setFilters((current) => ({ ...current, [key]: value }))
    setFilterError('')
  }

  const actions: Column<DevelopmentPlan, PlanSort> = {
    key: 'actions', title: 'Действия',
    render: (plan) => plan.status === 'draft' && plan.employee_id === user?.id ? (
      <div className={styles.actions}>
        <ButtonLink variant="secondary" to={`/development-plans/${plan.id}/edit`}>Редактировать</ButtonLink>
        <Button variant="danger" disabled={deletingId !== null} onClick={() => void deleteRecord(plan.id, `Удалить черновик ИПР №${plan.id} вместе с его содержимым?`)}>
          {deletingId === plan.id ? 'Удаление…' : 'Удалить'}
        </Button>
      </div>
    ) : '-',
  }

  return (
    <>
      <div className={styles.heading}>
        <div><h1>Планы развития</h1><p>Ваши индивидуальные планы и планы сотрудников, к которым у вас есть доступ.</p></div>
        <ButtonLink to="/development-plans/new">Создать ИПР</ButtonLink>
      </div>
      <form className={`${styles.panel} ${styles.filters}`} onSubmit={applyFilters}>
        <div className={styles.search}>
          <Input label="Поиск" type="search" placeholder="Цель или комментарий" value={filters.search} onChange={(event) => changeFilter('search', event.target.value)} />
        </div>
        <Select label="Статус" value={filters.status} onChange={(event) => changeFilter('status', event.target.value as PlanStatus | '')}>
          <option value="">Все статусы</option>
          {Object.entries(planStatuses).map(([value, label]) => <option key={value} value={value}>{label}</option>)}
        </Select>
        <Input label="Дата начала от" type="date" max="9999-12-31" value={filters.from} onChange={(event) => changeFilter('from', event.target.value)} />
        <Input label="Дата начала до" type="date" max="9999-12-31" value={filters.to} onChange={(event) => changeFilter('to', event.target.value)} />
        <Button type="submit">Применить</Button>
        <Button variant="secondary" onClick={() => {
          setFilters(blank)
          setFilterError('')
          collection.applyFilters(initialFilters)
        }}>Сбросить</Button>
        {filterError && <p role="alert" className={styles.filterError}>{filterError}</p>}
      </form>
      <CollectionTable collection={collection} columns={[...baseColumns, actions]} label="Список планов развития" />
    </>
  )
}
