// The project has no product photos, so instead of a grey placeholder every
// product gets a typographic tile: its first letter set in the display face
// on a tint chosen deterministically from the name. Same input → same tile.
const TINTS = [
  { bg: 'bg-accent-soft', letter: 'text-accent' },
  { bg: 'bg-volt-soft', letter: 'text-ink' },
  { bg: 'bg-ink', letter: 'text-paper' },
]

export default function ProductTile({ name, large = false, className = '' }) {
  const tint = TINTS[(name.codePointAt(0) + name.length) % TINTS.length]

  return (
    <div
      aria-hidden="true"
      className={`flex items-center justify-center ${tint.bg} ${className}`}
    >
      <span
        className={`font-display font-black select-none ${tint.letter} ${
          large ? 'text-[10rem]' : 'text-5xl'
        }`}
      >
        {name[0].toUpperCase()}
      </span>
    </div>
  )
}
