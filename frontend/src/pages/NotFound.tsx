import { ButtonLink } from '../components/ui/Button'

export function NotFound() {
  return (
    <section>
      <h1>404 · Страница не найдена</h1>
      <p>Проверьте адрес страницы или вернитесь на главную.</p>
      <ButtonLink to="/">На главную</ButtonLink>
    </section>
  )
}
