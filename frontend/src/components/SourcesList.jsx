export default function SourcesList({ sources, sourceMap }) {
  if (!sources || sources.length === 0) return null

  // Sort sources by their assigned number
  const sorted = [...sources].sort(
    (a, b) => (sourceMap[a.url] || 0) - (sourceMap[b.url] || 0)
  )

  return (
    <div>
      <h3 className="text-xs font-medium text-neutral-500 uppercase tracking-wider mb-3">
        Sources
      </h3>
      <div className="space-y-2">
        {sorted.map((source) => {
          const num = sourceMap[source.url]
          return (
            <div
              key={source.source_id}
              className="flex items-start gap-3 text-sm"
            >
              <span className="inline-flex items-center justify-center min-w-[22px] h-[22px] px-1
                               text-[10px] font-medium rounded bg-blue-500/20 text-blue-400 flex-shrink-0 mt-0.5">
                {num}
              </span>
              <div className="min-w-0">
                <a
                  href={source.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-[#e5e5e5] hover:text-blue-400 transition-colors duration-150"
                >
                  {source.title}
                </a>
                <p className="text-xs text-neutral-600 truncate mt-0.5">
                  {source.url}
                </p>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
