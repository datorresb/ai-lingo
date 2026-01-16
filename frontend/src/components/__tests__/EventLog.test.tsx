import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import '@testing-library/jest-dom'
import EventLog from '../EventLog'
import { useChatContext } from '../../context/ChatContext'

vi.mock('../../context/ChatContext', () => ({
  useChatContext: vi.fn(),
}))

const mockUseChatContext = vi.mocked(useChatContext)

describe('EventLog Component', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders empty state when no events', () => {
    mockUseChatContext.mockReturnValue({
      events: [],
    } as ReturnType<typeof useChatContext>)

    render(<EventLog />)

    expect(screen.getByText('No events yet.')).toBeInTheDocument()
  })

  it('renders formatted event types and content', () => {
    mockUseChatContext.mockReturnValue({
      events: [
        {
          type: 'thought',
          content: 'Thinking about topic selection',
          timestamp: new Date('2026-01-16T10:00:00Z'),
        },
        {
          type: 'tool_call',
          content: 'Calling RSS tool',
          timestamp: new Date('2026-01-16T10:01:00Z'),
        },
      ],
    } as ReturnType<typeof useChatContext>)

    render(<EventLog />)

    expect(screen.getByText('Thought')).toBeInTheDocument()
    expect(screen.getByText('Tool Call')).toBeInTheDocument()
    expect(screen.getAllByText('Thinking about topic selection').length).toBeGreaterThan(0)
    expect(screen.getAllByText('Calling RSS tool').length).toBeGreaterThan(0)
  })

  it('shows close button when onClose is provided', () => {
    const onClose = vi.fn()
    mockUseChatContext.mockReturnValue({
      events: [],
    } as ReturnType<typeof useChatContext>)

    render(<EventLog onClose={onClose} />)

    expect(screen.getByRole('button', { name: 'Close' })).toBeInTheDocument()
  })
})
