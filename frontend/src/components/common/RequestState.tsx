import { Button } from '../ui/Button'
import styles from './Workspace.module.css'

export function Loading() {
  return <div className={styles.state} role="status"><span className={styles.spinner} /> Загрузка данных…</div>
}

export function RequestError({ message, retry }: { message: string; retry: () => void }) {
  return (
    <div className={styles.state}>
      <p role="alert">{message}</p>
      <Button onClick={retry} variant="secondary">Повторить</Button>
    </div>
  )
}
