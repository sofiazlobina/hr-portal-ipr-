import { useState } from 'react'
import type { FormEvent } from 'react'
import { competenciesApi } from '../../api/competencies'
import type { CompetencySort } from '../../api/competencies'
import { CollectionTable } from '../../components/common/CollectionTable'
import { Button, ButtonLink } from '../../components/ui/Button'
import { Input } from '../../components/ui/Input'
import type { Column } from '../../components/ui/Table'
import { useAuth } from '../../hooks/useAuth'
import { useCollection } from '../../hooks/useCollection'
import { useDelete } from '../../hooks/useDelete'
import type { Competency } from '../../types/hr'
import styles from '../../components/common/Workspace.module.css'

const initialFilters: { search?: string } = {}
const baseColumns: Column<Competency, CompetencySort>[] = [
  { key: 'id', title: 'ID', sortBy: 'id', render: (row) => row.id },
  { key: 'name', title: 'Название', sortBy: 'name', render: (row) => <strong>{row.name}</strong> },
  { key: 'description', title: 'Описание', render: (row) => row.description || '-' },
]

export function CompetenciesList() {
  const { user } = useAuth()
  const canManage = user?.role === 'hr'
  const [search, setSearch] = useState('')
  const [searchError, setSearchError] = useState('')
  const collection = useCollection(competenciesApi.getAll, 'id', initialFilters)
  const { deletingId, deleteRecord } = useDelete(competenciesApi.delete, collection.refresh, 'Компетенция удалена.')

  function applySearch(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    const value = search.trim()
    if (value.length === 1) {
      setSearchError('Введите минимум два символа для поиска.')
      return
    }
    setSearchError('')
    collection.applyFilters({ search: value || undefined })
  }

  const actions: Column<Competency, CompetencySort> = {
    key: 'actions', title: 'Действия',
    render: (row) => (
      <div className={styles.actions}>
        <ButtonLink variant="secondary" to={`/competencies/${row.id}/edit`}>Редактировать</ButtonLink>
        <Button variant="danger" disabled={deletingId !== null} onClick={() => void deleteRecord(row.id, `Удалить компетенцию «${row.name}»?`)}>
          {deletingId === row.id ? 'Удаление…' : 'Удалить'}
        </Button>
      </div>
    ),
  }

  return (
    <>
      <div className={styles.heading}>
        <div><h1>Компетенции</h1><p>Справочник навыков для планов развития.</p></div>
        {canManage && <ButtonLink to="/competencies/new">Добавить компетенцию</ButtonLink>}
      </div>
      <form className={`${styles.panel} ${styles.filters}`} onSubmit={applySearch} noValidate>
        <div className={styles.search}>
          <Input label="Поиск" type="search" placeholder="Название или описание" value={search} error={searchError} onChange={(event) => {
            setSearch(event.target.value)
            setSearchError('')
          }} />
        </div>
        <Button type="submit">Найти</Button>
        <Button variant="secondary" onClick={() => {
          setSearch('')
          setSearchError('')
          collection.applyFilters(initialFilters)
        }}>Сбросить</Button>
      </form>
      <CollectionTable collection={collection} columns={canManage ? [...baseColumns, actions] : baseColumns} label="Список компетенций" />
    </>
  )
}
