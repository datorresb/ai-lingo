/**
 * useAGUIChat - Custom React hook for AI-powered chat management.
 *
 * Manages all state and API communication for the Expression Learner chat interface.
 * Handles streaming responses, SSE parsing, and real-time message updates.
 *
 * Refer to PRD section 6.1 for detailed specifications.
 */

import { useState, useCallback, useRef, useEffect } from 'react'
import axios from 'axios'

export interface Expression {
  phrase: string
  meaning: string
}

export interface Topic {
  headline: string
  source: string
  url: string
}

export interface Message {
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
  expressions?: Expression[]
}

export interface ChatEvent {
  type: 'thought' | 'tool_call' | 'tool_result' | 'state_update' | 'response'
  content: string
  timestamp: Date
}

export interface UseAGUIChatState {
  sessionId: string | null
  variant: string | null
  topic: Topic | null
  topics: Topic[]
  messages: Message[]
  events: ChatEvent[]
  isLoading: boolean
  error: string | null
}

export interface UseAGUIChatActions {
  startSession: (variant: string) => Promise<void>
  startTopicChat: () => Promise<void>
  sendMessage: (message: string) => Promise<void>
  reset: () => void
}

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const normalizeTopic = (rawTopic: unknown): Topic | null => {
  if (!rawTopic) return null

  if (typeof rawTopic === 'string') {
    return {
      headline: rawTopic,
      source: '',
      url: '',
    }
  }

  if (typeof rawTopic === 'object' && rawTopic !== null) {
    const topic = rawTopic as Partial<Topic>
    if (topic.headline) {
      return {
        headline: topic.headline,
        source: topic.source ?? '',
        url: topic.url ?? '',
      }
    }
  }

  return null
}

/**
 * useAGUIChat - Main hook for chat state management and streaming
 */
export function useAGUIChat(): UseAGUIChatState & UseAGUIChatActions {
  const [sessionId, setSessionId] = useState<string | null>(null)
  const [variant, setVariant] = useState<string | null>(null)
  const [topic, setTopic] = useState<Topic | null>(null)
  const [topics, setTopics] = useState<Topic[]>([])
  const [messages, setMessages] = useState<Message[]>([])
  const [events, setEvents] = useState<ChatEvent[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const abortControllerRef = useRef<AbortController | null>(null)

  /**
   * Initialize session with language variant
   */
  const startSession = useCallback(
    async (selectedVariant: string) => {
      try {
        setError(null)
        setIsLoading(true)

        const response = await axios.post(`${API_BASE_URL}/session`, {
          variant: selectedVariant,
        })

        const { session_id } = response.data
        setSessionId(session_id)
        setVariant(selectedVariant)
        setMessages([])
        setEvents([])

        console.log(`✅ Session started: ${session_id} (${selectedVariant})`)
      } catch (err) {
        const errorMsg = err instanceof Error ? err.message : 'Failed to start session'
        setError(errorMsg)
        console.error('❌ Session error:', errorMsg)
        throw err
      } finally {
        setIsLoading(false)
      }
    },
    []
  )

  const serializeEventContent = useCallback((value: unknown): string => {
    if (typeof value === 'string') return value
    if (value === undefined || value === null) return ''
    try {
      return JSON.stringify(value, null, 2)
    } catch (e) {
      return String(value)
    }
  }, [])

  const addEvent = useCallback(
    (type: ChatEvent['type'], content: unknown): void => {
      const event: ChatEvent = {
        type,
        content: serializeEventContent(content),
        timestamp: new Date(),
      }
      setEvents((prev) => [...prev, event])
    },
    [serializeEventContent]
  )

  /**
   * Start chat with topic generation from RSS feeds
   */
  const startTopicChat = useCallback(async () => {
    if (!sessionId) {
      setError('No active session')
      return
    }

    try {
      setError(null)
      setIsLoading(true)
      abortControllerRef.current = new AbortController()

      const response = await fetch(`${API_BASE_URL}/start_chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ session_id: sessionId }),
        signal: abortControllerRef.current.signal,
      })

      if (!response.ok) throw new Error(`HTTP ${response.status}`)

      // Parse streaming response
      const reader = response.body?.getReader()
      if (!reader) throw new Error('No response body')

      const decoder = new TextDecoder()
      let buffer = ''
      let done = false

      while (!done) {
        const { done: readerDone, value } = await reader.read()
        done = readerDone

        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        buffer = lines.pop() || ''

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6))
              if (data.topic) {
                const normalizedTopic = normalizeTopic(data.topic)
                if (normalizedTopic) {
                  setTopics((prev) => {
                    if (prev.some((item) => item.url && item.url === normalizedTopic.url)) {
                      return prev
                    }
                    if (prev.some((item) => item.headline === normalizedTopic.headline)) {
                      return prev
                    }
                    return [...prev, normalizedTopic]
                  })
                  setTopic(normalizedTopic)
                  addEvent('tool_call', `Selected topic: ${normalizedTopic.headline}`)
                }
              }
            } catch (e) {
              console.error('Parse error:', e)
            }
          }
        }
      }
    } catch (err) {
      if (err instanceof Error && err.name !== 'AbortError') {
        const errorMsg = err.message || 'Failed to start topic chat'
        setError(errorMsg)
        console.error('❌ Topic chat error:', errorMsg)
      }
    } finally {
      setIsLoading(false)
      abortControllerRef.current = null
    }
  }, [sessionId, addEvent])

  /**
   * Extract expressions from text using [[phrase::meaning]] format
   */
  const extractExpressions = (text: string): Expression[] => {
    const pattern = /\[\[([^\]]+)::([^\]]+)\]\]/g
    const expressions: Expression[] = []
    let match

    while ((match = pattern.exec(text)) !== null) {
      expressions.push({
        phrase: match[1].trim(),
        meaning: match[2].trim(),
      })
    }

    return expressions
  }

  /**
   * Process streaming SSE response from chat endpoint
   */
  const processStreamResponse = useCallback(async (response: Response) => {
    const reader = response.body?.getReader()
    if (!reader) throw new Error('No response body')

    const decoder = new TextDecoder()
    let buffer = ''
    let assistantContent = ''
    let extractedExpressions: Expression[] = []

    let done = false
    while (!done) {
      const { done: readerDone, value } = await reader.read()
      done = readerDone

      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n')
      buffer = lines.pop() || ''

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          try {
            const data = JSON.parse(line.slice(6))

            // Handle different event types
            if (data.type === 'thought') {
              addEvent('thought', data.content)
            } else if (data.type === 'tool_call') {
              addEvent('tool_call', data.content ?? data)
            } else if (data.type === 'tool_result') {
              addEvent('tool_result', data.content ?? data)
            } else if (data.type === 'state_update') {
              addEvent('state_update', data.content ?? data)
            } else if (data.type === 'assistant_message') {
              addEvent('response', data.content ?? data)
            } else if (data.type === 'response') {
              addEvent('response', data.content ?? data)
            } else if (data.type === 'chunk') {
              // Stream text chunk
              assistantContent += data.content

              // Extract expressions from chunk
              const expressions = extractExpressions(data.content)
              extractedExpressions = [...extractedExpressions, ...expressions]
            } else if (data.type === 'done') {
              // Message complete - add to messages
              const assistantMsg: Message = {
                role: 'assistant',
                content: assistantContent,
                timestamp: new Date(),
                expressions: extractedExpressions,
              }
              setMessages((prev) => [...prev, assistantMsg])
              if (assistantContent) {
                addEvent('response', assistantContent)
              }
              assistantContent = ''
              extractedExpressions = []
            }
          } catch (e) {
            console.error('Parse error:', e)
          }
        }
      }
    }

    // Flush any remaining content
    if (assistantContent) {
      const assistantMsg: Message = {
        role: 'assistant',
        content: assistantContent,
        timestamp: new Date(),
        expressions: extractedExpressions,
      }
      setMessages((prev) => [...prev, assistantMsg])
    }
  }, [addEvent])

  /**
   * Send message and stream response
   */
  const sendMessage = useCallback(
    async (content: string) => {
      if (!sessionId) {
        setError('No active session')
        return
      }

      try {
        setError(null)
        setIsLoading(true)

        // Add user message immediately
        const userMsg: Message = {
          role: 'user',
          content,
          timestamp: new Date(),
        }
        setMessages((prev) => [...prev, userMsg])

        abortControllerRef.current = new AbortController()

        // Stream agent response
        const response = await fetch(`${API_BASE_URL}/chat`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            session_id: sessionId,
            message: content,
          }),
          signal: abortControllerRef.current.signal,
        })

        if (!response.ok) throw new Error(`HTTP ${response.status}`)

        // Process streaming response
        await processStreamResponse(response)
      } catch (err) {
        if (err instanceof Error && err.name !== 'AbortError') {
          const errorMsg = err.message || 'Failed to send message'
          setError(errorMsg)
          console.error('❌ Message error:', errorMsg)
        }
      } finally {
        setIsLoading(false)
        abortControllerRef.current = null
      }
    },
    [sessionId, processStreamResponse]
  )

  /**
   * Reset all state
   */
  const reset = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort()
    }
    setSessionId(null)
    setVariant(null)
    setTopic(null)
    setTopics([])
    setMessages([])
    setEvents([])
    setError(null)
    setIsLoading(false)
  }, [])

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort()
      }
    }
  }, [])

  return {
    sessionId,
    variant,
    topic,
    topics,
    messages,
    events,
    isLoading,
    error,
    startSession,
    startTopicChat,
    sendMessage,
    reset,
  }
}

export default useAGUIChat
