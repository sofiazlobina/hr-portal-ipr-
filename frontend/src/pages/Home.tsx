import { Link } from 'react-router-dom'
import styles from './Home.module.css'

const sections = [
  { path: '/development-plans', title: 'Планы развития', description: 'Просматривайте индивидуальные планы и редактируйте свои черновики.' },
  { path: '/competencies', title: 'Компетенции', description: 'Найдите компетенции и их описания в общем справочнике.' },
  { path: '/departments', title: 'Отделы', description: 'Просматривайте список подразделений компании.' },
]

export function Home() {
  return (
    <>
      <section className={styles.intro}>
        <h1>Добро пожаловать в HR-портал</h1>
        <p>Рабочее пространство для индивидуальных планов развития сотрудников.</p>
      </section>
      <section className={styles.sections} aria-label="Разделы портала">
        {sections.map(({ path, title, description }) => (
          <Link key={path} to={path}>
            <h2>{title} <span aria-hidden="true">↗</span></h2>
            <p>{description}</p>
          </Link>
        ))}
      </section>
    </>
  )
}
