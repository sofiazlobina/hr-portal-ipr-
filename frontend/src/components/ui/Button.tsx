import type { ButtonHTMLAttributes, ReactNode } from 'react'
import { Link } from 'react-router-dom'
import styles from './Controls.module.css'

type Variant = 'primary' | 'secondary' | 'danger'
type ButtonProps = ButtonHTMLAttributes<HTMLButtonElement> & { variant?: Variant }

export function Button({ variant = 'primary', type = 'button', className = '', ...props }: ButtonProps) {
  return <button type={type} className={`${styles.button} ${styles[variant]} ${className}`} {...props} />
}

export function ButtonLink({ to, children, variant = 'primary' }: {
  to: string
  children: ReactNode
  variant?: Variant
}) {
  return <Link to={to} className={`${styles.button} ${styles[variant]}`}>{children}</Link>
}
