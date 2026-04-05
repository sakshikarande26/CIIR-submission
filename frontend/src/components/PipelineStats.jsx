export default function PipelineStats({ metadata }) {
  if (!metadata) return null

  const stats = [
    { label: 'Total time', value: `${metadata.total_time_seconds}s` },
    { label: 'Pages scraped', value: `${metadata.pages_scraped}/${metadata.pages_scraped + metadata.pages_failed}` },
    { label: 'Chunks', value: metadata.chunks_created },
    { label: 'Entities', value: metadata.entities_found },
  ]

  return (
    <div className="flex flex-wrap items-center gap-x-5 gap-y-1 text-xs text-neutral-500">
      {stats.map((s, i) => (
        <span key={i}>
          {s.label}: <span className="text-neutral-400">{s.value}</span>
        </span>
      ))}
    </div>
  )
}
