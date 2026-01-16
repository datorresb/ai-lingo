import { FC } from 'react'
import { useChatContext } from '../context/ChatContext'

interface EventLogProps {
  onClose?: () => void
  title?: string
}

const EventLog: FC<EventLogProps> = ({ onClose, title = 'Event Log' }) => {
  const { events } = useChatContext()

  const formatType = (type: string) => {
    const normalized = type.replace('_', ' ')
    switch (type) {
      case 'thought':
        return { label: 'Thought', color: 'text-indigo-500 bg-indigo-50' }
      case 'tool_call':
        return { label: 'Tool Call', color: 'text-amber-600 bg-amber-50' }
      case 'tool_result':
        return { label: 'Tool Result', color: 'text-emerald-600 bg-emerald-50' }
      case 'response':
        return { label: 'Response', color: 'text-blue-600 bg-blue-50' }
      case 'assistant_message':
        return { label: 'Assistant', color: 'text-slate-600 bg-slate-50' }
      case 'state_update':
        return { label: 'State Update', color: 'text-violet-600 bg-violet-50' }
      default:
        return { label: normalized, color: 'text-gray-600 bg-gray-100' }
    }
  }

  const buildPreview = (content: string) => {
    const trimmed = content.trim()
    if (trimmed.length <= 120) return trimmed
    return `${trimmed.slice(0, 120)}…`
  }

  return (
    <section className="flex h-full flex-col rounded-xl border border-gray-200 bg-white p-4 shadow-sm">
      <div className="flex items-center justify-between pb-3">
        <h3 className="text-base font-semibold text-gray-900">{title}</h3>
        {onClose && (
          <button
            type="button"
            onClick={onClose}
            className="text-sm text-gray-500 hover:text-gray-700"
          >
            Close
          </button>
        )}
      </div>
      <div className="flex-1 space-y-4 overflow-y-auto pr-1">
        {events.length === 0 ? (
          <p className="text-sm text-gray-500">No events yet.</p>
        ) : (
          events.map((event, index) => (
            <div key={`${event.type}-${index}`} className="relative pl-6">
              <span className="absolute left-1 top-2 h-2 w-2 rounded-full bg-indigo-400" />
              <div className="rounded-lg border border-gray-100 bg-gray-50 p-3 shadow-sm">
                <details className="group">
                  <summary className="flex cursor-pointer list-none items-start justify-between gap-3">
                    <div className="flex flex-col gap-2">
                      <span
                        className={`inline-flex w-fit items-center rounded-full px-2 py-0.5 text-[11px] font-semibold uppercase ${
                          formatType(event.type).color
                        }`}
                      >
                        {formatType(event.type).label}
                      </span>
                      <span className="text-sm text-gray-800">
                        {buildPreview(event.content)}
                      </span>
                    </div>
                    <span className="text-xs text-gray-400">
                      {event.timestamp.toLocaleTimeString()}
                    </span>
                  </summary>
                  <div className="mt-3 rounded-md bg-white px-3 py-2 text-sm text-gray-700">
                    {event.content}
                  </div>
                </details>
              </div>
            </div>
          ))
        )}
      </div>
    </section>
  )
}

export default EventLog
