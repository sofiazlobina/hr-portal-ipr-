import type { ReactNode } from 'react'
import styles from './Table.module.css'

export interface Column<Row, SortField extends string> {
  key: string
  title: string
  render: (row: Row) => ReactNode
  sortBy?: SortField
}

export interface Sort<Field extends string> {
  field: Field
  order: 'asc' | 'desc'
}

export function Table<Row extends { id: number }, SortField extends string>({
  label, columns, rows, sort, onSort,
}: {
  label: string
  columns: readonly Column<Row, SortField>[]
  rows: Row[]
  sort: Sort<SortField>
  onSort: (field: SortField) => void
}) {
  return (
    <div className={styles.scroll} role="region" aria-label={label} tabIndex={0}>
      <table className={styles.table} aria-label={label}>
        <thead>
          <tr>{columns.map(({ key, title, sortBy }) => (
            <th key={key} scope="col" aria-sort={sortBy === sort.field ? (sort.order === 'asc' ? 'ascending' : 'descending') : undefined}>
              {sortBy ? (
                <button type="button" onClick={() => onSort(sortBy)}>
                  {title} <span aria-hidden="true">{sortBy === sort.field ? (sort.order === 'asc' ? '↑' : '↓') : '↕'}</span>
                </button>
              ) : title}
            </th>
          ))}</tr>
        </thead>
        <tbody>{rows.map((row) => (
          <tr key={row.id}>{columns.map((column) => <td key={column.key}>{column.render(row)}</td>)}</tr>
        ))}</tbody>
      </table>
    </div>
  )
}
