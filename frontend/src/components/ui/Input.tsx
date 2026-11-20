import { useId } from 'react'
import type { InputHTMLAttributes, SelectHTMLAttributes, TextareaHTMLAttributes } from 'react'
import styles from './Controls.module.css'

type FieldProps = { label: string; error?: string }

export function Input({ label, error, id, ...props }: InputHTMLAttributes<HTMLInputElement> & FieldProps) {
  const generatedId = useId()
  const fieldId = id ?? generatedId
  return (
    <div className={styles.field}>
      <label htmlFor={fieldId}>{label}</label>
      <input {...props} id={fieldId} aria-invalid={!!error} aria-describedby={error ? `${fieldId}-error` : props['aria-describedby']} />
      {error && <span id={`${fieldId}-error`} className={styles.fieldError}>{error}</span>}
    </div>
  )
}

export function Textarea({ label, error, id, ...props }: TextareaHTMLAttributes<HTMLTextAreaElement> & FieldProps) {
  const generatedId = useId()
  const fieldId = id ?? generatedId
  return (
    <div className={styles.field}>
      <label htmlFor={fieldId}>{label}</label>
      <textarea {...props} id={fieldId} aria-invalid={!!error} aria-describedby={error ? `${fieldId}-error` : props['aria-describedby']} />
      {error && <span id={`${fieldId}-error`} className={styles.fieldError}>{error}</span>}
    </div>
  )
}

export function Select({ label, id, ...props }: SelectHTMLAttributes<HTMLSelectElement> & { label: string }) {
  const generatedId = useId()
  const fieldId = id ?? generatedId
  return (
    <div className={styles.field}>
      <label htmlFor={fieldId}>{label}</label>
      <select {...props} id={fieldId} />
    </div>
  )
}
