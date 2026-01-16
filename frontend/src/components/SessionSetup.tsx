import { FC, FormEvent, useState } from 'react'
import { useChatContext } from '../context/ChatContext'

const VARIANTS = [
  { value: 'US', label: 'English (US)' },
  { value: 'UK', label: 'English (UK)' },
  { value: 'Custom', label: 'Custom' },
]

const SessionSetup: FC = () => {
  const { startSession, isLoading, error } = useChatContext()
  const [variant, setVariant] = useState('US')

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault()
    await startSession(variant)
  }

  return (
    <section className="mx-auto flex w-full max-w-3xl flex-col gap-6 rounded-2xl border border-gray-200 bg-white p-8 shadow-sm">
      <header className="space-y-2">
        <h2 className="text-3xl font-semibold text-gray-900">Start your session</h2>
        <p className="text-gray-600">
          Choose the language variant and begin practicing expressions.
        </p>
      </header>

      {error && (
        <div className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-red-700">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="flex flex-col gap-4">
        <label className="text-sm font-medium text-gray-700" htmlFor="variant">
          Language variant
        </label>
        <select
          id="variant"
          value={variant}
          onChange={(event) => setVariant(event.target.value)}
          className="rounded-lg border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-200"
          disabled={isLoading}
        >
          {VARIANTS.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>

        <button
          type="submit"
          className="inline-flex items-center justify-center rounded-lg bg-indigo-600 px-5 py-2 text-sm font-semibold text-white transition hover:bg-indigo-700 disabled:cursor-not-allowed disabled:opacity-50"
          disabled={isLoading}
        >
          {isLoading ? 'Starting…' : 'Start Session'}
        </button>
      </form>
    </section>
  )
}

export default SessionSetup
