import { FC, FormEvent, KeyboardEvent, useEffect, useRef, useState } from 'react'
import ExpressionText from './ExpressionText'
import { Topic, useAGUIChat } from '../hooks/useAGUIChat'

const Chat: FC = () => {
    const {
        sessionId,
        topics,
        topic,
        messages,
        isLoading,
        error,
        startTopicChat,
        sendMessage,
    } = useAGUIChat()

    const [selectedTopic, setSelectedTopic] = useState<Topic | null>(null)
    const [draft, setDraft] = useState('')
    const messagesEndRef = useRef<HTMLDivElement>(null)

    useEffect(() => {
        if (sessionId && topics.length === 0) {
            startTopicChat()
        }
    }, [sessionId, topics.length, startTopicChat])

    useEffect(() => {
        if (!selectedTopic && topic) {
            setSelectedTopic(topic)
        }
    }, [topic, selectedTopic])

    useEffect(() => {
        const scrollToEnd = messagesEndRef.current?.scrollIntoView
        if (typeof scrollToEnd === 'function') {
            scrollToEnd({ behavior: 'smooth' })
        }
    }, [messages, isLoading, selectedTopic])

    const handleSubmit = async (event: FormEvent) => {
        event.preventDefault()
        const trimmed = draft.trim()
        if (!trimmed || !sessionId || !selectedTopic) return
        setDraft('')
        await sendMessage(trimmed)
    }

    const handleKeyDown = (event: KeyboardEvent<HTMLTextAreaElement>) => {
        if (event.key === 'Enter' && (event.ctrlKey || event.metaKey)) {
            event.preventDefault()
            void handleSubmit(event as unknown as FormEvent)
        }
    }

    if (!sessionId) {
        return (
            <section className="max-w-4xl mx-auto px-4 py-10">
                <div className="rounded-xl border border-gray-200 bg-white p-8 text-center shadow-sm">
                    <h2 className="text-2xl font-semibold text-gray-900 mb-2">Start a session to chat</h2>
                    <p className="text-gray-600">Create a session to load topics and begin chatting.</p>
                </div>
            </section>
        )
    }

    return (
        <section className="max-w-5xl mx-auto px-4 py-8">
            <div className="flex flex-col gap-6">
                <header className="flex flex-col gap-2">
                    <h2 className="text-2xl font-semibold text-gray-900">Chat</h2>
                    <p className="text-gray-600">Choose a topic and start your conversation.</p>
                </header>

                {error && (
                    <div className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-red-700">
                        {error}
                    </div>
                )}

                {!selectedTopic && (
                    <div className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
                        <h3 className="text-lg font-semibold text-gray-900 mb-4">Select a topic</h3>
                        {topics.length === 0 ? (
                            <div className="text-gray-500">
                                {isLoading ? 'Loading topics…' : 'No topics available yet.'}
                            </div>
                        ) : (
                            <div className="grid gap-4 sm:grid-cols-2">
                                {topics.slice(0, 5).map((item) => (
                                    <button
                                        key={item.url || item.headline}
                                        type="button"
                                        onClick={() => setSelectedTopic(item)}
                                        className="flex flex-col items-start gap-2 rounded-lg border border-gray-200 bg-gray-50 px-4 py-3 text-left transition hover:border-indigo-300 hover:bg-indigo-50"
                                    >
                                        <span className="text-sm font-semibold text-indigo-600">{item.source || 'Topic'}</span>
                                        <span className="text-base font-medium text-gray-900">{item.headline}</span>
                                    </button>
                                ))}
                            </div>
                        )}
                    </div>
                )}

                {selectedTopic && (
                    <div className="rounded-xl border border-indigo-200 bg-indigo-50 px-4 py-3">
                        <div className="text-sm text-indigo-600">Selected topic</div>
                        <div className="text-lg font-semibold text-indigo-900">{selectedTopic.headline}</div>
                        {selectedTopic.source && (
                            <div className="text-sm text-indigo-700">{selectedTopic.source}</div>
                        )}
                    </div>
                )}

                <div className="flex flex-col gap-4 rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
                    <div className="flex flex-col gap-4 max-h-[420px] overflow-y-auto pr-2">
                        {messages.length === 0 && (
                            <div className="text-gray-500 text-center py-6">
                                No messages yet. Start the conversation below.
                            </div>
                        )}
                        {messages.map((message, index) => {
                            const bubbleClass =
                                message.role === 'user'
                                    ? 'bg-indigo-600 text-white'
                                    : 'bg-gray-100 text-gray-900'

                            return (
                                <div
                                    key={`${message.role}-${index}`}
                                    className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                                >
                                    <div
                                        className={`max-w-[80%] rounded-2xl px-4 py-3 text-sm sm:text-base shadow-sm ${bubbleClass}`}
                                    >
                                        {message.role === 'assistant' ? (
                                            <ExpressionText text={message.content} />
                                        ) : (
                                            <span>{message.content}</span>
                                        )}
                                    </div>
                                </div>
                            )
                        })}
                        {isLoading && (
                            <div className="flex justify-start">
                                <div className="rounded-2xl bg-gray-100 px-4 py-3 text-sm text-gray-500">
                                    Thinking…
                                </div>
                            </div>
                        )}
                        <div ref={messagesEndRef} />
                    </div>

                    <form onSubmit={handleSubmit} className="flex flex-col gap-3">
                        <label htmlFor="chat-input" className="text-sm font-medium text-gray-700">
                            Your message
                        </label>
                        <textarea
                            id="chat-input"
                            value={draft}
                            onChange={(event) => setDraft(event.target.value)}
                            onKeyDown={handleKeyDown}
                            rows={3}
                            placeholder="Type your message here…"
                            className="w-full resize-none rounded-lg border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-200"
                            disabled={!selectedTopic || isLoading}
                        />
                        <div className="flex items-center justify-between text-xs text-gray-500">
                            <span>Tip: Use Ctrl/⌘ + Enter to send.</span>
                            <button
                                type="submit"
                                disabled={!draft.trim() || !selectedTopic || isLoading}
                                className="inline-flex items-center justify-center rounded-lg bg-indigo-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-indigo-700 disabled:cursor-not-allowed disabled:opacity-50"
                            >
                                Send
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </section>
    )
}

export default Chat
