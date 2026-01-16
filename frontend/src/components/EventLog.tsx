import { FC } from 'react'
import { useChatContext } from '../context/ChatContext'

interface EventLogProps {
  onClose?: () => void
  title?: string
}

const EventLog: FC<EventLogProps> = ({ onClose, title = 'Event Log' }) => {
  const { events } = useChatContext()

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
      <div className="flex-1 space-y-3 overflow-y-auto pr-1">
        {events.length === 0 ? (
          <p className="text-sm text-gray-500">No events yet.</p>
        ) : (
          events.map((event, index) => (
            <div key={`${event.type}-${index}`} className="rounded-lg bg-gray-50 p-3">
              <div className="text-xs font-semibold uppercase text-indigo-500">
                {event.type.replace('_', ' ')}
              </div>
              <div className="text-sm text-gray-800">{event.content}</div>
              <div className="text-xs text-gray-400">
                {event.timestamp.toLocaleTimeString()}
              </div>
            </div>
          ))
        )}
      </div>
    </section>
  )
}

export default EventLog
