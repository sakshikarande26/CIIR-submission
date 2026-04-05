import { useState, useEffect } from 'react'

const STEPS = [
  'Searching the web...',
  'Scraping pages...',
  'Analyzing content...',
  'Extracting entities...',
  'Resolving duplicates...',
]

export default function LoadingState() {
  const [visibleCount, setVisibleCount] = useState(1)

  useEffect(() => {
    if (visibleCount >= STEPS.length) return
    const timer = setTimeout(() => {
      setVisibleCount((c) => c + 1)
    }, 3500)
    return () => clearTimeout(timer)
  }, [visibleCount])

  return (
    <div className="w-full max-w-md mx-auto py-16">
      <div className="space-y-4">
        {STEPS.slice(0, visibleCount).map((step, i) => {
          const isActive = i === visibleCount - 1
          return (
            <div
              key={step}
              className="flex items-center gap-3 animate-fade-in-up"
            >
              {/* Pulsing dot for active, static check for completed */}
              {isActive ? (
                <span className="w-2 h-2 rounded-full bg-blue-500 animate-pulse-dot" />
              ) : (
                <svg
                  className="w-4 h-4 text-neutral-600"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M5 13l4 4L19 7"
                  />
                </svg>
              )}
              <span
                className={
                  isActive ? 'text-[#e5e5e5] text-sm' : 'text-neutral-600 text-sm'
                }
              >
                {step}
              </span>
            </div>
          )
        })}
      </div>

      {/* Progress bar */}
      <div className="mt-8 h-0.5 bg-border rounded-full overflow-hidden">
        <div
          className="h-full bg-blue-500/60 rounded-full transition-all duration-1000 ease-out"
          style={{ width: `${(visibleCount / STEPS.length) * 100}%` }}
        />
      </div>
    </div>
  )
}
