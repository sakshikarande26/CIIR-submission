export default function ResultsTable({
  entities,
  columns,
  entityType,
  sourceCount,
  sourceMap,
  onCitationClick,
}) {
  if (entities.length === 0) {
    return (
      <div className="text-center py-12 text-neutral-500">
        No entities found for this query.
      </div>
    )
  }

  return (
    <div>
      {/* Header */}
      <div className="flex items-center gap-3 mb-4 text-sm text-neutral-400">
        <span className="capitalize">{entityType}s found: <span className="text-[#e5e5e5]">{entities.length}</span></span>
        <span className="text-border">|</span>
        <span>Sources: <span className="text-[#e5e5e5]">{sourceCount}</span></span>
      </div>

      {/* Table */}
      <div className="overflow-x-auto rounded-xl border border-border">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-border bg-surface">
              {columns.map((col) => (
                <th
                  key={col}
                  className="px-4 py-3 text-left text-xs font-medium text-neutral-400 uppercase tracking-wider whitespace-nowrap"
                >
                  {col}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {entities.map((entity, idx) => (
              <tr
                key={idx}
                className="border-b border-border last:border-b-0 hover:bg-white/[0.02] transition-colors duration-150"
              >
                {columns.map((col, colIdx) => {
                  const cell = entity.attributes[col]
                  const value = cell?.value
                  const citations = cell?.citations || []

                  // Get source numbers for citation badges
                  const badgeNums = []
                  const seen = new Set()
                  for (const c of citations) {
                    const num = sourceMap[c.url]
                    if (num !== undefined && !seen.has(num)) {
                      seen.add(num)
                      badgeNums.push({ num, citation: c, col })
                    }
                  }

                  return (
                    <td
                      key={col}
                      className={`px-4 py-3 ${colIdx === 0 ? 'font-medium text-[#e5e5e5]' : 'text-neutral-300'}`}
                    >
                      <div className="flex items-start gap-1.5">
                        <span className={value ? '' : 'text-neutral-600'}>
                          {value || '—'}
                        </span>
                        {badgeNums.length > 0 && (
                          <span className="flex gap-0.5 flex-shrink-0 mt-0.5">
                            {badgeNums.map(({ num, citation, col: attrName }) => (
                              <button
                                key={`${num}-${citation.chunk_id}`}
                                onClick={() =>
                                  onCitationClick({
                                    ...citation,
                                    attribute: attrName,
                                  })
                                }
                                className="inline-flex items-center justify-center min-w-[18px] h-[18px] px-1
                                           text-[10px] font-medium rounded bg-blue-500/20 text-blue-400
                                           hover:bg-blue-500/30 transition-colors duration-150 cursor-pointer"
                              >
                                {num}
                              </button>
                            ))}
                          </span>
                        )}
                      </div>
                    </td>
                  )
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
