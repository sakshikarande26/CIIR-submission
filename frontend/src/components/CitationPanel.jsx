import { useEffect } from 'react'

export default function CitationPanel({ citation, onClose }) {
  // Close on Escape key
  useEffect(() => {
    const handler = (e) => {
      if (e.key === 'Escape') onClose()
    }
    document.addEventListener('keydown', handler)
    return () => document.removeEventListener('keydown', handler)
  }, [onClose])

  if (!citation) return null

  return (
    <>
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black/50 z-40 transition-opacity duration-200"
        onClick={onClose}
      />

      {/* Drawer */}
      <div
        className="fixed top-0 right-0 h-full w-full max-w-lg bg-surface border-l border-border
                    z-50 overflow-y-auto shadow-2xl
                    animate-[slideIn_200ms_ease_forwards]"
        style={{
          animation: 'slideIn 200ms ease forwards',
        }}
      >
        <style>{`
          @keyframes slideIn {
            from { transform: translateX(100%); }
            to { transform: translateX(0); }
          }
        `}</style>

        {/* Header */}
        <div className="sticky top-0 bg-surface border-b border-border px-6 py-4 flex items-start justify-between">
          <div className="min-w-0 pr-4">
            <p className="text-xs text-neutral-500 uppercase tracking-wider mb-1">
              Citation for
            </p>
            <p className="text-sm font-medium text-blue-400">
              {citation.attribute}
            </p>
          </div>
          <button
            onClick={onClose}
            className="p-1 text-neutral-500 hover:text-neutral-300 transition-colors duration-150 flex-shrink-0"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Content */}
        <div className="px-6 py-5 space-y-5">
          {/* Source title */}
          <div>
            <p className="text-xs text-neutral-500 uppercase tracking-wider mb-1.5">Source</p>
            <p className="text-sm text-[#e5e5e5] font-medium">{citation.title}</p>
          </div>

          {/* URL */}
          <div>
            <p className="text-xs text-neutral-500 uppercase tracking-wider mb-1.5">URL</p>
            <a
              href={citation.url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-sm text-blue-400 hover:text-blue-300 transition-colors duration-150
                         inline-flex items-center gap-1.5 break-all"
            >
              {citation.url}
              <svg className="w-3.5 h-3.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
              </svg>
            </a>
          </div>

          {/* Passage */}
          <div>
            <p className="text-xs text-neutral-500 uppercase tracking-wider mb-1.5">Passage</p>
            <blockquote className="border-l-2 border-blue-500 pl-4 py-2 text-sm text-neutral-300 leading-relaxed bg-white/[0.02] rounded-r-lg pr-4">
              {citation.passage}
            </blockquote>
          </div>
        </div>
      </div>
    </>
  )
}
