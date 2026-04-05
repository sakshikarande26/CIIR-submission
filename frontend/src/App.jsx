import { useState, useMemo } from 'react'
import { useSearch } from './hooks/useSearch'
import SearchBar from './components/SearchBar'
import LoadingState from './components/LoadingState'
import ResultsTable from './components/ResultsTable'
import CitationPanel from './components/CitationPanel'
import SourcesList from './components/SourcesList'
import PipelineStats from './components/PipelineStats'

function buildSourceMap(results) {
  // Collect all unique URLs from citations across all entities, in order of appearance
  const urls = []
  const seen = new Set()

  for (const entity of results.entities) {
    for (const cell of Object.values(entity.attributes)) {
      for (const c of cell.citations || []) {
        if (!seen.has(c.url)) {
          seen.add(c.url)
          urls.push(c.url)
        }
      }
    }
  }

  // Map URL -> sequential number (1-based)
  const map = {}
  urls.forEach((url, i) => {
    map[url] = i + 1
  })
  return map
}

export default function App() {
  const { query, setQuery, results, loading, error, search } = useSearch()
  const [activeCitation, setActiveCitation] = useState(null)

  const sourceMap = useMemo(() => {
    if (!results) return {}
    return buildSourceMap(results)
  }, [results])

  return (
    <div className="min-h-screen px-4 py-8 md:py-16">
      {/* Title — only prominent when no results */}
      <div className={`text-center mb-8 transition-all duration-300 ${results ? 'mb-6' : 'mb-10 pt-[15vh]'}`}>
        <h1 className={`font-semibold tracking-tight transition-all duration-300 ${results ? 'text-xl' : 'text-3xl md:text-4xl'}`}>
          Agentic Search
        </h1>
        {!results && !loading && (
          <p className="mt-3 text-neutral-500 text-sm">
            Structured entity extraction from the web with source-level citations
          </p>
        )}
      </div>

      {/* Search bar */}
      <SearchBar
        query={query}
        setQuery={setQuery}
        onSearch={search}
        disabled={loading}
      />

      {/* Loading */}
      {loading && <LoadingState />}

      {/* Error */}
      {error && (
        <div className="max-w-2xl mx-auto mt-8 p-4 rounded-xl bg-red-500/10 border border-red-500/20 text-sm text-red-400">
          <p>{error}</p>
          <button
            onClick={() => search()}
            className="mt-2 text-xs text-red-300 hover:text-red-200 underline transition-colors duration-150"
          >
            Retry
          </button>
        </div>
      )}

      {/* Results */}
      {results && !loading && (
        <div className="max-w-6xl mx-auto mt-8 space-y-8">
          {/* Pipeline stats */}
          <PipelineStats metadata={results.pipeline_metadata} />

          {/* Table */}
          <ResultsTable
            entities={results.entities}
            columns={results.columns}
            entityType={results.entity_type}
            sourceCount={Object.keys(sourceMap).length}
            sourceMap={sourceMap}
            onCitationClick={setActiveCitation}
          />

          {/* Sources */}
          <SourcesList sources={results.sources} sourceMap={sourceMap} />
        </div>
      )}

      {/* Citation drawer */}
      <CitationPanel
        citation={activeCitation}
        onClose={() => setActiveCitation(null)}
      />
    </div>
  )
}
