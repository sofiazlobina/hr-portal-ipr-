const dateFormatter = new Intl.DateTimeFormat('ru-RU', {
  day: '2-digit', month: '2-digit', year: 'numeric', timeZone: 'UTC',
})
const numberFormatter = new Intl.NumberFormat('ru-RU', { maximumFractionDigits: 2 })

export function formatDate(value: string) {
  return dateFormatter.format(new Date(value))
}

export function formatProgress(value: number) {
  return `${numberFormatter.format(value)} %`
}

export function parseRecordId(value: string) {
  if (!/^[1-9]\d*$/.test(value)) return null
  const id = Number(value)
  return id <= 2_147_483_647 ? id : null
}
