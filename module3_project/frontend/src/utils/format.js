// DRF serializes DecimalField as a string ("2499.00"), hence the Number().
export function formatPrice(value) {
  return `${new Intl.NumberFormat('uk-UA').format(Number(value))} грн`
}

export function formatDate(value) {
  return new Date(value).toLocaleDateString('uk-UA', {
    day: 'numeric',
    month: 'long',
    year: 'numeric',
  })
}

export const AUDIENCE_LABELS = {
  unisex: 'Унісекс',
  man: 'Чоловіче',
  woman: 'Жіноче',
}
