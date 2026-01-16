import { describe, it, expect, vi, beforeEach } from 'vitest'
import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import '@testing-library/jest-dom'
import Chat from '../Chat'
import { Topic, useAGUIChat } from '../../hooks/useAGUIChat'

vi.mock('../../hooks/useAGUIChat', () => ({
  useAGUIChat: vi.fn(),
  default: vi.fn(),
}))

const mockUseAGUIChat = vi.mocked(useAGUIChat)

const buildTopic = (headline: string): Topic => ({
  headline,
  source: 'BBC',
  url: `https://example.com/${headline}`,
})

const buildHookState = (
  overrides: Partial<ReturnType<typeof useAGUIChat>> = {}
): ReturnType<typeof useAGUIChat> => ({
  sessionId: 'session-123',
  variant: 'us',
  topic: null,
  topics: [],
  messages: [],
  events: [],
  isLoading: false,
  error: null,
  startSession: vi.fn(),
  startTopicChat: vi.fn(),
  sendMessage: vi.fn(),
  reset: vi.fn(),
  ...overrides,
})

describe('Chat Component', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders topic cards from streamed topics', () => {
    const topics = [buildTopic('Tech trends'), buildTopic('Science news')]
    mockUseAGUIChat.mockReturnValue(buildHookState({ topics }))

    render(<Chat />)

    expect(screen.getByText('Tech trends')).toBeInTheDocument()
    expect(screen.getByText('Science news')).toBeInTheDocument()
  })

  it('shows selected topic when a card is clicked', async () => {
    const topics = [buildTopic('AI breakthroughs')]
    mockUseAGUIChat.mockReturnValue(buildHookState({ topics }))

    render(<Chat />)

    fireEvent.click(screen.getByText('AI breakthroughs'))

    await waitFor(() => {
      expect(screen.getByText('Selected topic')).toBeInTheDocument()
      expect(screen.getByText('AI breakthroughs')).toBeInTheDocument()
    })
  })

  it('renders assistant message with highlighted expressions', () => {
    const topic = buildTopic('World updates')
    mockUseAGUIChat.mockReturnValue(
      buildHookState({
        topic,
        topics: [topic],
        messages: [
          {
            role: 'assistant',
            content: 'That was [[a piece of cake::very easy]] for the team.',
            timestamp: new Date(),
          },
        ],
      })
    )

    render(<Chat />)

    const highlighted = screen.getByText('a piece of cake')
    expect(highlighted).toHaveClass('expression-highlight')
  })

  it('sends message from input', async () => {
    const topic = buildTopic('Market update')
    const sendMessage = vi.fn()
    mockUseAGUIChat.mockReturnValue(
      buildHookState({ topic, topics: [topic], sendMessage })
    )

    render(<Chat />)

    fireEvent.change(screen.getByLabelText('Your message'), {
      target: { value: 'Hello there' },
    })

    fireEvent.click(screen.getByRole('button', { name: 'Send' }))

    await waitFor(() => {
      expect(sendMessage).toHaveBeenCalledWith('Hello there')
    })
  })
})
