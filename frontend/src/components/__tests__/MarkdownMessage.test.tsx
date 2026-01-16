import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import '@testing-library/jest-dom'
import MarkdownMessage from '../MarkdownMessage'

describe('MarkdownMessage', () => {
    it('renders markdown content', () => {
        render(<MarkdownMessage content="## Title\n\nSome **bold** text" />)

        expect(screen.getByRole('heading', { name: /Title/ })).toBeInTheDocument()
        expect(screen.getByText('bold')).toBeInTheDocument()
    })

    it('renders expression highlights inside markdown', () => {
        render(
            <MarkdownMessage content="This is [[a piece of cake::very easy]] to do." />
        )

        const highlighted = screen.getByText('a piece of cake')
        expect(highlighted).toHaveClass('expression-highlight')
    })

    it('sanitizes raw html', () => {
        render(
            <MarkdownMessage content="Hello <script>alert('x')</script> world" />
        )

        expect(screen.queryByText("alert('x')")).not.toBeInTheDocument()
        expect(screen.getByText(/Hello/)).toBeInTheDocument()
        expect(screen.getByText(/world/)).toBeInTheDocument()
    })
})
