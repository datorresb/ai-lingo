import { FC, useState } from 'react'
import Header from './components/Header'
import Footer from './components/Footer'
import Chat from './components/Chat'
import EventLog from './components/EventLog'
import SessionSetup from './components/SessionSetup'
import { ChatProvider, useChatContext } from './context/ChatContext'

const AppLayout: FC = () => {
  const { sessionId } = useChatContext()
  const [isEventLogOpen, setIsEventLogOpen] = useState(false)

  return (
    <div className="min-h-screen flex flex-col bg-gray-50">
      <Header />
      <main className="flex-1">
        <div className="mx-auto flex max-w-7xl flex-col gap-6 px-4 py-10 lg:flex-row lg:items-start">
          <div className="flex-1 space-y-6">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-2xl font-semibold text-gray-900">
                  {sessionId ? 'Conversation' : 'Session Setup'}
                </h2>
                <p className="text-sm text-gray-500">
                  {sessionId
                    ? 'Continue the chat and review highlighted expressions.'
                    : 'Create a session to start chatting.'}
                </p>
              </div>
              <button
                type="button"
                onClick={() => setIsEventLogOpen(true)}
                className="inline-flex items-center rounded-lg border border-gray-200 bg-white px-3 py-2 text-sm font-medium text-gray-700 shadow-sm transition hover:border-indigo-300 hover:text-indigo-600 lg:hidden"
              >
                Event Log
              </button>
            </div>

            {sessionId ? <Chat /> : <SessionSetup />}
          </div>

          <aside className="hidden w-full max-w-xs lg:block">
            <EventLog />
          </aside>
        </div>
      </main>
      <Footer />

      {isEventLogOpen && (
        <div className="fixed inset-0 z-50 flex justify-end bg-black/40 p-4 lg:hidden">
          <div className="h-full w-full max-w-sm">
            <EventLog title="Event Log" onClose={() => setIsEventLogOpen(false)} />
          </div>
        </div>
      )}
    </div>
  )
}

const App: FC = () => {
  return (
    <ChatProvider>
      <AppLayout />
    </ChatProvider>
  )
}

export default App
