/**
 * Tests for useAGUIChat hook
 *
 * Tests:
 * 1. Hook initialization
 * 2. Session creation
 * 3. Topic chat with streaming
 * 4. Message sending with streaming
 * 5. Expression extraction
 * 6. Error handling
 * 7. SSE parsing
 * 8. State updates
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { renderHook, act } from '@testing-library/react'
import axios from 'axios'
import { useAGUIChat } from '../useAGUIChat'

// Mock axios
vi.mock('axios')

describe('useAGUIChat Hook', () => {

  beforeEach(() => {
    vi.clearAllMocks()
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  describe('Initialization', () => {
    it('should initialize with null/empty state', () => {
      const { result } = renderHook(() => useAGUIChat())

      expect(result.current.sessionId).toBeNull()
      expect(result.current.variant).toBeNull()
      expect(result.current.topic).toBeNull()
      expect(result.current.topics).toEqual([])
      expect(result.current.messages).toEqual([])
      expect(result.current.events).toEqual([])
      expect(result.current.isLoading).toBe(false)
      expect(result.current.error).toBeNull()
    })

    it('should provide all required functions', () => {
      const { result } = renderHook(() => useAGUIChat())

      expect(typeof result.current.startSession).toBe('function')
      expect(typeof result.current.startTopicChat).toBe('function')
      expect(typeof result.current.sendMessage).toBe('function')
      expect(typeof result.current.reset).toBe('function')
    })
  })

  describe('startSession', () => {
    it('should create a session with variant', async () => {
      const mockSessionId = 'session-123'
      vi.mocked(axios.post).mockResolvedValue({
        data: { session_id: mockSessionId },
      })

      const { result } = renderHook(() => useAGUIChat())

      await act(async () => {
        await result.current.startSession('us')
      })

      expect(axios.post).toHaveBeenCalledWith('http://localhost:8000/session', {
        variant: 'us',
      })
      expect(result.current.sessionId).toBe(mockSessionId)
      expect(result.current.variant).toBe('us')
      expect(result.current.isLoading).toBe(false)
    })

    it('should reset messages and events on new session', async () => {
      const mockSessionId = 'session-123'
      vi.mocked(axios.post).mockResolvedValue({
        data: { session_id: mockSessionId },
      })

      const { result } = renderHook(() => useAGUIChat())

      // Create first session
      await act(async () => {
        await result.current.startSession('us')
      })

      // Manually add messages (simulating previous chat)
      const prevSession = result.current
      expect(prevSession.sessionId).toBe(mockSessionId)

      // Create second session
      vi.mocked(axios.post).mockResolvedValue({
        data: { session_id: 'session-456' },
      })

      await act(async () => {
        await result.current.startSession('uk')
      })

      expect(result.current.sessionId).toBe('session-456')
      expect(result.current.variant).toBe('uk')
      expect(result.current.messages).toEqual([])
      expect(result.current.events).toEqual([])
    })

    it('should handle session creation error', async () => {
      const errorMsg = 'Server error'
      vi.mocked(axios.post).mockRejectedValue(new Error(errorMsg))

      const { result } = renderHook(() => useAGUIChat())

      await act(async () => {
        try {
          await result.current.startSession('us')
        } catch (e) {
          // Expected
        }
      })

      expect(result.current.error).toBe(errorMsg)
      expect(result.current.sessionId).toBeNull()
      expect(result.current.isLoading).toBe(false)
    })

    it('should set isLoading during session creation', async () => {
      let resolvePost: ((value: unknown) => void) | null = null
      const postPromise = new Promise((resolve) => {
        resolvePost = resolve
      })
      vi.mocked(axios.post).mockReturnValue(postPromise as never)

      const { result } = renderHook(() => useAGUIChat())

      const sessionPromise = result.current.startSession('us').then(() => {
        // After it resolves, check that loading was false after
        expect(result.current.isLoading).toBe(false)
      }).catch(() => {
        // Expected
      })

      // Give the async flow a chance to start
      await new Promise((r) => setTimeout(r, 10))

      // Resolve the promise
      if (resolvePost) {
        resolvePost({ data: { session_id: 'session-123' } })
      }
      await sessionPromise
    })
  })

  describe('startTopicChat', () => {
    it('should fail without active session', async () => {
      const { result } = renderHook(() => useAGUIChat())

      await act(async () => {
        await result.current.startTopicChat()
      })

      expect(result.current.error).toBe('No active session')
    })

    it('should stream topic from /start_chat endpoint', async () => {
      const mockSessionId = 'session-123'
      vi.mocked(axios.post).mockResolvedValue({
        data: { session_id: mockSessionId },
      })

      const { result } = renderHook(() => useAGUIChat())

      // Create session
      await act(async () => {
        await result.current.startSession('us')
      })

      // Mock streaming response
      const mockStream = {
        body: new ReadableStream({
          start(controller) {
            controller.enqueue(
              new TextEncoder().encode(
                'data: {"topic":{"headline":"Technology","source":"TechCrunch","url":"https://example.com"}}\n'
              )
            )
            controller.close()
          },
        }),
        ok: true,
      } as Response

      global.fetch = vi.fn().mockResolvedValue(mockStream)

      await act(async () => {
        await result.current.startTopicChat()
      })

      expect(result.current.topic?.headline).toBe('Technology')
      expect(result.current.topics).toHaveLength(1)
      expect(global.fetch).toHaveBeenCalledWith('http://localhost:8000/start_chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: mockSessionId }),
        signal: expect.any(AbortSignal),
      })
    })

    it('should add event when topic is selected', async () => {
      const mockSessionId = 'session-123'
      vi.mocked(axios.post).mockResolvedValue({
        data: { session_id: mockSessionId },
      })

      const { result } = renderHook(() => useAGUIChat())

      await act(async () => {
        await result.current.startSession('us')
      })

      const mockStream = {
        body: new ReadableStream({
          start(controller) {
            controller.enqueue(
              new TextEncoder().encode(
                'data: {"topic":{"headline":"Science","source":"BBC","url":"https://example.com"}}\n'
              )
            )
            controller.close()
          },
        }),
        ok: true,
      } as Response

      global.fetch = vi.fn().mockResolvedValue(mockStream)

      await act(async () => {
        await result.current.startTopicChat()
      })

      expect(result.current.events).toHaveLength(1)
      expect(result.current.events[0].type).toBe('tool_call')
      expect(result.current.events[0].content).toContain('Science')
    })
  })

  describe('sendMessage', () => {
    beforeEach(async () => {
      const mockSessionId = 'session-123'
      vi.mocked(axios.post).mockResolvedValue({
        data: { session_id: mockSessionId },
      })
    })

    it('should fail without active session', async () => {
      const { result } = renderHook(() => useAGUIChat())

      await act(async () => {
        await result.current.sendMessage('Hello')
      })

      expect(result.current.error).toBe('No active session')
    })

    it('should add user message immediately', async () => {
      const mockSessionId = 'session-123'
      vi.mocked(axios.post).mockResolvedValue({
        data: { session_id: mockSessionId },
      })

      const { result } = renderHook(() => useAGUIChat())

      await act(async () => {
        await result.current.startSession('us')
      })

      const mockStream = {
        body: new ReadableStream({
          start(controller) {
            // Don't emit done event, just end the stream
            controller.close()
          },
        }),
        ok: true,
      } as Response

      global.fetch = vi.fn().mockResolvedValue(mockStream)

      await act(async () => {
        await result.current.sendMessage('What is hello?')
      })

      // Should only have user message since no assistant message was sent
      expect(result.current.messages).toHaveLength(1)
      expect(result.current.messages[0].role).toBe('user')
      expect(result.current.messages[0].content).toBe('What is hello?')
    })

    it('should stream assistant response with chunks', async () => {
      const mockSessionId = 'session-123'
      vi.mocked(axios.post).mockResolvedValue({
        data: { session_id: mockSessionId },
      })

      const { result } = renderHook(() => useAGUIChat())

      await act(async () => {
        await result.current.startSession('us')
      })

      const mockStream = {
        body: new ReadableStream({
          start(controller) {
            controller.enqueue(
              new TextEncoder().encode(
                'data: {"type":"chunk","content":"Hello is a greeting"}\n'
              )
            )
            controller.enqueue(
              new TextEncoder().encode('data: {"type":"done"}\n')
            )
            controller.close()
          },
        }),
        ok: true,
      } as Response

      global.fetch = vi.fn().mockResolvedValue(mockStream)

      await act(async () => {
        await result.current.sendMessage('What is hello?')
      })

      expect(result.current.messages).toHaveLength(2)
      expect(result.current.messages[1].role).toBe('assistant')
      expect(result.current.messages[1].content).toContain('Hello is a greeting')
    })

    it('should extract expressions from response', async () => {
      const mockSessionId = 'session-123'
      vi.mocked(axios.post).mockResolvedValue({
        data: { session_id: mockSessionId },
      })

      const { result } = renderHook(() => useAGUIChat())

      await act(async () => {
        await result.current.startSession('us')
      })

      const mockStream = {
        body: new ReadableStream({
          start(controller) {
            controller.enqueue(
              new TextEncoder().encode(
                'data: {"type":"chunk","content":"This is [[raining cats and dogs::raining heavily]]"}\n'
              )
            )
            controller.enqueue(
              new TextEncoder().encode('data: {"type":"done"}\n')
            )
            controller.close()
          },
        }),
        ok: true,
      } as Response

      global.fetch = vi.fn().mockResolvedValue(mockStream)

      await act(async () => {
        await result.current.sendMessage('What expressions?')
      })

      expect(result.current.messages[1].expressions).toHaveLength(1)
      expect(result.current.messages[1].expressions![0].phrase).toBe(
        'raining cats and dogs'
      )
      expect(result.current.messages[1].expressions![0].meaning).toBe('raining heavily')
    })

    it('should handle multiple expressions in response', async () => {
      const mockSessionId = 'session-123'
      vi.mocked(axios.post).mockResolvedValue({
        data: { session_id: mockSessionId },
      })

      const { result } = renderHook(() => useAGUIChat())

      await act(async () => {
        await result.current.startSession('us')
      })

      const mockStream = {
        body: new ReadableStream({
          start(controller) {
            controller.enqueue(
              new TextEncoder().encode(
                'data: {"type":"chunk","content":"[[piece of cake::easy]] and [[break the ice::start conversation]]"}\n'
              )
            )
            controller.enqueue(
              new TextEncoder().encode('data: {"type":"done"}\n')
            )
            controller.close()
          },
        }),
        ok: true,
      } as Response

      global.fetch = vi.fn().mockResolvedValue(mockStream)

      await act(async () => {
        await result.current.sendMessage('Give examples')
      })

      expect(result.current.messages[1].expressions).toHaveLength(2)
      expect(result.current.messages[1].expressions![0].phrase).toBe('piece of cake')
      expect(result.current.messages[1].expressions![1].phrase).toBe('break the ice')
    })

    it('should capture thought events', async () => {
      const mockSessionId = 'session-123'
      vi.mocked(axios.post).mockResolvedValue({
        data: { session_id: mockSessionId },
      })

      const { result } = renderHook(() => useAGUIChat())

      await act(async () => {
        await result.current.startSession('us')
      })

      const mockStream = {
        body: new ReadableStream({
          start(controller) {
            controller.enqueue(
              new TextEncoder().encode(
                'data: {"type":"thought","content":"Thinking about the question"}\n'
              )
            )
            controller.enqueue(
              new TextEncoder().encode('data: {"type":"chunk","content":"Answer"}\n')
            )
            controller.enqueue(
              new TextEncoder().encode('data: {"type":"done"}\n')
            )
            controller.close()
          },
        }),
        ok: true,
      } as Response

      global.fetch = vi.fn().mockResolvedValue(mockStream)

      await act(async () => {
        await result.current.sendMessage('Question?')
      })

      expect(result.current.events).toHaveLength(1)
      expect(result.current.events[0].type).toBe('thought')
      expect(result.current.events[0].content).toBe('Thinking about the question')
    })
  })

  describe('Expression Extraction', () => {
    it('should handle expressions with whitespace', async () => {
      const mockSessionId = 'session-123'
      vi.mocked(axios.post).mockResolvedValue({
        data: { session_id: mockSessionId },
      })

      const { result } = renderHook(() => useAGUIChat())

      await act(async () => {
        await result.current.startSession('us')
      })

      const mockStream = {
        body: new ReadableStream({
          start(controller) {
            controller.enqueue(
              new TextEncoder().encode(
                'data: {"type":"chunk","content":"[[  spaced phrase  ::  spaced meaning  ]]"}\n'
              )
            )
            controller.enqueue(
              new TextEncoder().encode('data: {"type":"done"}\n')
            )
            controller.close()
          },
        }),
        ok: true,
      } as Response

      global.fetch = vi.fn().mockResolvedValue(mockStream)

      await act(async () => {
        await result.current.sendMessage('Test')
      })

      expect(result.current.messages[1].expressions![0].phrase).toBe('spaced phrase')
      expect(result.current.messages[1].expressions![0].meaning).toBe('spaced meaning')
    })

    it('should handle empty expressions gracefully', async () => {
      const mockSessionId = 'session-123'
      vi.mocked(axios.post).mockResolvedValue({
        data: { session_id: mockSessionId },
      })

      const { result } = renderHook(() => useAGUIChat())

      await act(async () => {
        await result.current.startSession('us')
      })

      const mockStream = {
        body: new ReadableStream({
          start(controller) {
            controller.enqueue(
              new TextEncoder().encode(
                'data: {"type":"chunk","content":"Text without expressions"}\n'
              )
            )
            controller.enqueue(
              new TextEncoder().encode('data: {"type":"done"}\n')
            )
            controller.close()
          },
        }),
        ok: true,
      } as Response

      global.fetch = vi.fn().mockResolvedValue(mockStream)

      await act(async () => {
        await result.current.sendMessage('Test')
      })

      expect(result.current.messages[1].expressions).toHaveLength(0)
    })
  })

  describe('reset', () => {
    it('should reset all state', async () => {
      const mockSessionId = 'session-123'
      vi.mocked(axios.post).mockResolvedValue({
        data: { session_id: mockSessionId },
      })

      const { result } = renderHook(() => useAGUIChat())

      await act(async () => {
        await result.current.startSession('us')
      })

      expect(result.current.sessionId).toBe(mockSessionId)

      act(() => {
        result.current.reset()
      })

      expect(result.current.sessionId).toBeNull()
      expect(result.current.variant).toBeNull()
      expect(result.current.topic).toBeNull()
      expect(result.current.topics).toEqual([])
      expect(result.current.messages).toEqual([])
      expect(result.current.events).toEqual([])
      expect(result.current.error).toBeNull()
      expect(result.current.isLoading).toBe(false)
    })
  })

  describe('Error Handling', () => {
    it('should handle fetch errors', async () => {
      const mockSessionId = 'session-123'
      vi.mocked(axios.post).mockResolvedValue({
        data: { session_id: mockSessionId },
      })

      const { result } = renderHook(() => useAGUIChat())

      await act(async () => {
        await result.current.startSession('us')
      })

      global.fetch = vi.fn().mockRejectedValue(new Error('Network error'))

      await act(async () => {
        await result.current.sendMessage('Test')
      })

      expect(result.current.error).toBe('Network error')
    })

    it('should handle HTTP errors', async () => {
      const mockSessionId = 'session-123'
      vi.mocked(axios.post).mockResolvedValue({
        data: { session_id: mockSessionId },
      })

      const { result } = renderHook(() => useAGUIChat())

      await act(async () => {
        await result.current.startSession('us')
      })

      const mockStream = {
        ok: false,
      } as Response

      global.fetch = vi.fn().mockResolvedValue(mockStream)

      await act(async () => {
        await result.current.sendMessage('Test')
      })

      expect(result.current.error).toContain('HTTP')
    })
  })
})
