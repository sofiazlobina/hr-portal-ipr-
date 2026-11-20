import type { useCollection } from '../../hooks/useCollection'
import { Button } from '../ui/Button'
import { Table } from '../ui/Table'
import type { Column } from '../ui/Table'
import { Loading, RequestError } from './RequestState'
import styles from './Workspace.module.css'

export function CollectionTable<Row extends { id: number }, Field extends string, Filters extends object>({
  collection, columns, label,
}: {
  collection: ReturnType<typeof useCollection<Row, Field, Filters>>
  columns: readonly Column<Row, Field>[]
  label: string
}) {
  const { result, refresh, sort, changeSort, setPage } = collection
  if (!result) return <Loading />
  if (result.data === undefined) return <RequestError message={result.error} retry={refresh} />

  const { items, page, total, total_pages: totalPages } = result.data
  if (!items.length) return <p className={styles.state} role="status">Записи не найдены.</p>

  return (
    <section className={styles.panel} aria-label={label}>
      <Table label={label} rows={items} columns={columns} sort={sort} onSort={changeSort} />
      <nav className={styles.pagination} aria-label="Пагинация">
        <span>Всего записей: {total}</span>
        <div className={styles.actions}>
          <Button variant="secondary" disabled={page <= 1} onClick={() => setPage(page - 1)}>Назад</Button>
          <span>Страница {page} из {totalPages}</span>
          <Button variant="secondary" disabled={page >= totalPages} onClick={() => setPage(page + 1)}>Вперёд</Button>
        </div>
      </nav>
    </section>
  )
}
