import { Link, NavLink, Outlet, useNavigate } from 'react-router-dom'
import { useAuth } from '../../hooks/useAuth'
import type { Role } from '../../types/hr'
import styles from './Layout.module.css'

const roleLabels: Record<Role, string> = { employee: 'Сотрудник', manager: 'Руководитель', hr: 'HR' }

export function Layout() {
  const { user, signOut } = useAuth()
  const navigate = useNavigate()

  function leave() {
    signOut()
    navigate('/', { replace: true })
  }

  return (
    <div className={styles.shell}>
      <header className={styles.header}>
        <div className={styles.headerInner}>
          <Link className={styles.brand} to="/"><span>HR</span> HR-портал</Link>
          <nav aria-label="Основная навигация">
            <NavLink to="/" end>Главная</NavLink>
            <NavLink to="/development-plans">Планы развития</NavLink>
            <NavLink to="/competencies">Компетенции</NavLink>
            <NavLink to="/departments">Отделы</NavLink>
          </nav>
          <div className={styles.session}>
            {user ? (
              <>
                <span className={styles.identity}>{user.full_name} <small>{roleLabels[user.role]}</small></span>
                <button type="button" onClick={leave}>Выйти</button>
              </>
            ) : <Link to="/login">Войти</Link>}
          </div>
        </div>
      </header>
      <main className={styles.main}><Outlet /></main>
      <footer className={styles.footer}>HR-портал · Развитие персонала</footer>
    </div>
  )
}
