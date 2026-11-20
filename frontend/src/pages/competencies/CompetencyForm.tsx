import { useCallback, useState } from 'react'
import type { FormEvent } from 'react'
import { useParams } from 'react-router-dom'
import { competenciesApi } from '../../api/competencies'
import { Loading, RequestError } from '../../components/common/RequestState'
import { Button, ButtonLink } from '../../components/ui/Button'
import { Input, Textarea } from '../../components/ui/Input'
import { useAuth } from '../../hooks/useAuth'
import { useRemote } from '../../hooks/useRemote'
import { useSave } from '../../hooks/useSave'
import type { Competency } from '../../types/hr'
import { parseRecordId } from '../../utils/formatters'
import { NotFound } from '../NotFound'
import styles from '../../components/common/Workspace.module.css'

const listPath = '/competencies'

export function CompetencyForm() {
  const { id } = useParams()
  const { user } = useAuth()
  if (user?.role !== 'hr') {
    return <div className={styles.state}><p>Изменять справочник может только HR-специалист.</p><ButtonLink to={listPath}>К списку</ButtonLink></div>
  }
  if (id === undefined) return <Editor />
  const recordId = parseRecordId(id)
  return recordId ? <EditLoader key={recordId} id={recordId} /> : <NotFound />
}

function EditLoader({ id }: { id: number }) {
  const load = useCallback((signal: AbortSignal) => competenciesApi.getById(id, signal), [id])
  const { result, refresh } = useRemote(load)
  if (!result) return <Loading />
  if (!result.data) return <RequestError message={result.error} retry={refresh} />
  return <Editor record={result.data} />
}

function Editor({ record }: { record?: Competency }) {
  const [name, setName] = useState(record?.name ?? '')
  const [description, setDescription] = useState(record?.description ?? '')
  const [nameError, setNameError] = useState('')
  const { pending, error, save } = useSave(listPath)

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    const value = name.trim()
    if (value.length < 1 || value.length > 100) {
      setNameError('Введите название длиной от 1 до 100 символов.')
      return
    }
    const values = { name: value, description: description.trim() || null }
    void save(
      () => record ? competenciesApi.update(record.id, values) : competenciesApi.create(values),
      record ? 'Компетенция обновлена.' : 'Компетенция создана.',
    )
  }

  return (
    <>
      <div className={styles.heading}><h1>{record ? 'Редактирование компетенции' : 'Новая компетенция'}</h1></div>
      <form className={`${styles.panel} ${styles.form}`} onSubmit={handleSubmit} noValidate aria-busy={pending}>
        <fieldset disabled={pending}>
          <Input label="Название" required maxLength={100} value={name} error={nameError} onChange={(event) => {
            setName(event.target.value)
            setNameError('')
          }} />
          <Textarea label="Описание" rows={5} value={description} onChange={(event) => setDescription(event.target.value)} />
        </fieldset>
        {error && <p role="alert" className={styles.formError}>{error}</p>}
        <div className={styles.actions}>
          <Button type="submit" disabled={pending}>{pending ? 'Сохранение…' : record ? 'Сохранить' : 'Создать'}</Button>
          <ButtonLink to={listPath} variant="secondary">Отмена</ButtonLink>
        </div>
      </form>
    </>
  )
}
