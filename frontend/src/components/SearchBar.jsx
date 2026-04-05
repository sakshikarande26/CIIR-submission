import { useState, useEffect } from 'react'

const PLACEHOLDERS = [
  'AI startups in healthcare',
  'top pizza places in Brooklyn',
  'open source database tools',
]

export default function SearchBar({ query, setQuery, onSearch, disabled }) {
  const [placeholderIdx, setPlaceholderIdx] = useState(0)

  useEffect(() => {
    const interval = setInterval(() => {
      setPlaceholderIdx((i) => (i + 1) % PLACEHOLDERS.length)
    }, 3000)
    return () => clearInterval(interval)
  }, [])

  const handleSubmit = (e) => {
    e.preventDefault()
    if (!disabled && query.trim()) onSearch()
  }

  return (
    <form onSubmit={handleSubmit} className="w-full max-w-2xl mx-auto">
      <div className="relative flex items-center">
        {/* Search icon */}
        <svg
          className="absolute left-4 w-5 h-5 text-neutral-500 pointer-events-none"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
          />
        </svg>

        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder={PLACEHOLDERS[placeholderIdx]}
          disabled={disabled}
          className="w-full pl-12 pr-28 py-4 bg-surface border border-border rounded-xl
                     text-[#e5e5e5] placeholder-neutral-600 text-base
                     focus:outline-none focus:border-blue-500/50 focus:ring-1 focus:ring-blue-500/30
                     disabled:opacity-50 transition-colors duration-150"
        />

        <button
          type="submit"
          disabled={disabled || !query.trim()}
          className="absolute right-2 px-5 py-2 bg-blue-600 hover:bg-blue-500
                     text-white text-sm font-medium rounded-lg
                     disabled:opacity-40 disabled:hover:bg-blue-600
                     transition-colors duration-150"
        >
          Search
        </button>
      </div>
    </form>
  )
}
