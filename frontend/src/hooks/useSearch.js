import { useState, useCallback } from 'react'

export function useSearch() {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const search = useCallback(async (searchQuery) => {
    const q = searchQuery ?? query
    if (!q.trim()) return

    setLoading(true)
    setError(null)
    setResults(null)

    try {
      const resp = await fetch('/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: q }),
      })

      if (!resp.ok) {
        throw new Error(`Server error: ${resp.status}`)
      }

      const data = await resp.json()
      setResults(data)
    } catch (err) {
      setError(err.message || 'Something went wrong')
    } finally {
      setLoading(false)
    }
  }, [query])

  return { query, setQuery, results, loading, error, search }
}
