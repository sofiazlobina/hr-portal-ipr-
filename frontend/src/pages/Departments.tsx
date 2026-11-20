import { departmentsApi } from '../api/departments'
import type { DepartmentSort } from '../api/departments'
import { CollectionTable } from '../components/common/CollectionTable'
import type { Column } from '../components/ui/Table'
import { useCollection } from '../hooks/useCollection'
import type { Department } from '../types/hr'
import styles from '../components/common/Workspace.module.css'

const columns: Column<Department, DepartmentSort>[] = [
  { key: 'id', title: 'ID', sortBy: 'id', render: (department) => department.id },
  { key: 'name', title: 'Название', sortBy: 'name', render: (department) => department.name },
]

export function Departments() {
  const collection = useCollection(departmentsApi.getAll, 'name', {})
  return (
    <>
      <div className={styles.heading}><h1>Отделы</h1></div>
      <CollectionTable collection={collection} columns={columns} label="Список отделов" />
    </>
  )
}
