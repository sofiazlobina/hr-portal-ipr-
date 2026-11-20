import { useCallback, useState } from 'react'
import type { FormEvent } from 'react'
import { useParams } from 'react-router-dom'
import { developmentPlansApi } from '../../api/developmentPlans'
import { Loading, RequestError } from '../../components/common/RequestState'
import { Button, ButtonLink } from '../../components/ui/Button'
import { Input } from '../../components/ui/Input'
import { useAuth } from '../../hooks/useAuth'
import { useRemote } from '../../hooks/useRemote'
import { useSave } from '../../hooks/useSave'
import { planStatuses } from '../../types/hr'
import type { Activity, DevelopmentPlan } from '../../types/hr'
import { formatDate, formatProgress, parseRecordId } from '../../utils/formatters'
import { NotFound } from '../NotFound'
import styles from '../../components/common/Workspace.module.css'

const listPath = '/development-plans'
const activityTypes: Record<Activity['type'], string> = { course: 'Курс', practice: 'Практика', reading: 'Чтение' }

export function PlanRecord({ mode }: { mode: 'form' | 'details' }) {
  const { id } = useParams()
  if (id === undefined && mode === 'form') return <Editor />
  const recordId = id === undefined ? null : parseRecordId(id)
  return recordId ? <RecordLoader key={recordId} id={recordId} mode={mode} /> : <NotFound />
}

function RecordLoader({ id, mode }: { id: number; mode: 'form' | 'details' }) {
  const { user } = useAuth()
  const load = useCallback((signal: AbortSignal) => developmentPlansApi.getById(id, signal), [id])
  const { result, refresh } = useRemote(load)
  if (!result) return <Loading />
  if (!result.data) return <RequestError message={result.error} retry={refresh} />

  const plan = result.data
  const canEdit = plan.employee_id === user?.id && plan.status === 'draft'
  if (mode === 'details') return <Details plan={plan} canEdit={canEdit} />
  if (!canEdit) {
    return <div className={styles.state}><p>Редактировать ИПР может владелец черновика.</p><ButtonLink to={`${listPath}/${id}`}>Открыть ИПР</ButtonLink></div>
  }
  return <Editor plan={plan} />
}

function Editor({ plan }: { plan?: DevelopmentPlan }) {
  const { user } = useAuth()
  const [start, setStart] = useState(plan?.start_date ?? '')
  const [end, setEnd] = useState(plan?.end_date ?? '')
  const [fieldErrors, setFieldErrors] = useState<{ start?: string; end?: string }>({})
  const { pending, error, save } = useSave(listPath)

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    if (!user) return
    const errors: typeof fieldErrors = {}
    const validDate = /^\d{4}-\d{2}-\d{2}$/
    if (!validDate.test(start) || start.startsWith('0000-')) {
      errors.start = 'Укажите дату начала.'
    }
    if (!validDate.test(end) || end.startsWith('0000-')) {
      errors.end = 'Укажите дату окончания.'
    } else if (!errors.start && end < start) {
      errors.end = 'Дата окончания не может быть раньше даты начала.'
    }
    setFieldErrors(errors)
    if (errors.start || errors.end) return

    const values = { start_date: start, end_date: end }
    void save(
      () => plan ? developmentPlansApi.update(plan.id, values) : developmentPlansApi.create({ ...values, employee_id: user.id }),
      plan ? 'Период ИПР обновлён.' : 'Черновик ИПР создан.',
    )
  }

  return (
    <>
      <div className={styles.heading}>
        <div><h1>{plan ? `Редактирование ИПР №${plan.id}` : 'Новый план развития'}</h1><p>Укажите период индивидуального плана.</p></div>
      </div>
      <form className={`${styles.panel} ${styles.form}`} onSubmit={handleSubmit} noValidate aria-busy={pending}>
        <fieldset disabled={pending}>
          <Input label="Дата начала" name="start" type="date" required min="0001-01-01" max="9999-12-31" value={start} error={fieldErrors.start} onChange={(event) => {
            setStart(event.target.value)
            setFieldErrors((current) => ({ ...current, start: undefined }))
          }} />
          <Input label="Дата окончания" name="end" type="date" required min="0001-01-01" max="9999-12-31" value={end} error={fieldErrors.end} onChange={(event) => {
            setEnd(event.target.value)
            setFieldErrors((current) => ({ ...current, end: undefined }))
          }} />
        </fieldset>
        {error && <p role="alert" className={styles.formError}>{error}</p>}
        <div className={styles.actions}>
          <Button type="submit" disabled={pending}>{pending ? 'Сохранение…' : plan ? 'Сохранить' : 'Создать'}</Button>
          <ButtonLink to={listPath} variant="secondary">Отмена</ButtonLink>
        </div>
      </form>
    </>
  )
}

function Details({ plan, canEdit }: { plan: DevelopmentPlan; canEdit: boolean }) {
  return (
    <>
      <div className={styles.heading}>
        <h1>ИПР №{plan.id}</h1>
        <div className={styles.actions}>
          <ButtonLink variant="secondary" to={listPath}>К списку</ButtonLink>
          {canEdit && <ButtonLink to={`${listPath}/${plan.id}/edit`}>Редактировать</ButtonLink>}
        </div>
      </div>
      <section className={`${styles.panel} ${styles.details}`} aria-label="Содержание ИПР">
        <dl className={styles.meta}>
          <div><dt>Статус</dt><dd><span className={styles.badge}>{planStatuses[plan.status]}</span></dd></div>
          <div><dt>Сотрудник</dt><dd>№{plan.employee_id}</dd></div>
          <div><dt>Период</dt><dd>{formatDate(plan.start_date)} – {formatDate(plan.end_date)}</dd></div>
          <div><dt>Прогресс</dt><dd>{formatProgress(plan.progress)}</dd></div>
          {plan.manager_comment && <div><dt>Комментарий руководителя</dt><dd>{plan.manager_comment}</dd></div>}
        </dl>
        <div>
          <h2>Цели и мероприятия</h2>
          {plan.goals.length ? <ul>{plan.goals.map((goal) => (
            <li key={goal.id}>
              {goal.description} · до {formatDate(goal.deadline)}{goal.is_completed ? ' · выполнена' : ''}
              {goal.activities.length > 0 && <ul>{goal.activities.map((activity) => (
                <li key={activity.id}>
                  {activityTypes[activity.type]} · {activity.description} · до {formatDate(activity.deadline)}
                  {activity.status === 'completed' ? ' · выполнено' : ''}
                </li>
              ))}</ul>}
            </li>
          ))}</ul> : <p>Целей пока нет.</p>}
        </div>
        <div>
          <h2>Компетенции</h2>
          {plan.competencies.length ? <ul>{plan.competencies.map((competency) => (
            <li key={competency.competency_id}>Компетенция №{competency.competency_id} · уровень {competency.current_level} → {competency.target_level}</li>
          ))}</ul> : <p>Компетенции пока не добавлены.</p>}
        </div>
      </section>
    </>
  )
}
