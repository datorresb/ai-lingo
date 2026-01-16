/**
 * Tests for ExpressionText Component
 * 
 * Test Coverage:
 * 1. Basic rendering
 * 2. Expression parsing and highlighting
 * 3. Multiple expressions
 * 4. Tooltip interactions (hover, click, keyboard)
 * 5. Accessibility features
 * 6. Edge cases (nested brackets, special chars, empty text)
 */

import { describe, it, expect } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import '@testing-library/jest-dom'
import ExpressionText from '../ExpressionText'

describe('ExpressionText Component', () => {
  describe('Basic Rendering', () => {
    it('should render plain text without expressions', () => {
      render(<ExpressionText text="Hello, this is plain text." />)
      expect(screen.getByText('Hello, this is plain text.')).toBeInTheDocument()
    })

    it('should render empty text', () => {
      const { container } = render(<ExpressionText text="" />)
      expect(container.querySelector('span')).toBeInTheDocument()
    })

    it('should apply custom className', () => {
      const { container } = render(
        <ExpressionText text="Test" className="custom-class" />
      )
      expect(container.querySelector('.custom-class')).toBeInTheDocument()
    })
  })

  describe('Expression Parsing', () => {
    it('should parse and highlight single expression', () => {
      render(
        <ExpressionText text="This is [[a piece of cake::very easy]] to do." />
      )
      
      const expression = screen.getByText('a piece of cake')
      expect(expression).toBeInTheDocument()
      expect(expression).toHaveClass('expression-highlight')
      expect(screen.getByText(/This is/)).toBeInTheDocument()
      expect(screen.getByText(/to do\./)).toBeInTheDocument()
    })

    it('should parse multiple expressions in one text', () => {
      render(
        <ExpressionText text="It's [[a piece of cake::very easy]] and [[costs an arm and a leg::very expensive]]." />
      )
      
      expect(screen.getByText('a piece of cake')).toBeInTheDocument()
      expect(screen.getByText('costs an arm and a leg')).toBeInTheDocument()
    })

    it('should handle expressions at start of text', () => {
      render(
        <ExpressionText text="[[Break the ice::start a conversation]] with a joke." />
      )
      
      expect(screen.getByText('Break the ice')).toBeInTheDocument()
      expect(screen.getByText(/with a joke\./)).toBeInTheDocument()
    })

    it('should handle expressions at end of text', () => {
      render(
        <ExpressionText text="Let's [[break the ice::start a conversation]]" />
      )
      
      expect(screen.getByText(/Let's/)).toBeInTheDocument()
      expect(screen.getByText('break the ice')).toBeInTheDocument()
    })

    it('should handle consecutive expressions', () => {
      render(
        <ExpressionText text="[[first::meaning1]][[second::meaning2]]" />
      )
      
      expect(screen.getByText('first')).toBeInTheDocument()
      expect(screen.getByText('second')).toBeInTheDocument()
    })
  })

  describe('Expression Trimming', () => {
    it('should trim whitespace from phrase and meaning', () => {
      render(
        <ExpressionText text="[[  spaced phrase  ::  spaced meaning  ]]" />
      )
      
      const expression = screen.getByText('spaced phrase')
      expect(expression).toBeInTheDocument()
      expect(expression).toHaveAttribute('aria-label', 'Expression: spaced phrase. Meaning: spaced meaning')
    })
  })

  describe('Tooltip Display', () => {
    it('should show tooltip on mouse enter', async () => {
      render(
        <ExpressionText text="[[piece of cake::very easy]]" />
      )
      
      const expression = screen.getByText('piece of cake')
      
      // Tooltip should not be visible initially
      expect(screen.queryByText('very easy')).not.toBeInTheDocument()
      
      // Hover over expression
      fireEvent.mouseEnter(expression)
      
      // Tooltip should now be visible
      await waitFor(() => {
        expect(screen.getByText('very easy')).toBeInTheDocument()
      })
    })

    it('should hide tooltip on mouse leave', async () => {
      render(
        <ExpressionText text="[[piece of cake::very easy]]" />
      )
      
      const expression = screen.getByText('piece of cake')
      
      // Show tooltip
      fireEvent.mouseEnter(expression)
      await waitFor(() => {
        expect(screen.getByText('very easy')).toBeInTheDocument()
      })
      
      // Hide tooltip
      fireEvent.mouseLeave(expression)
      await waitFor(() => {
        expect(screen.queryByText('very easy')).not.toBeInTheDocument()
      })
    })

    it('should toggle tooltip on click (mobile support)', async () => {
      render(
        <ExpressionText text="[[piece of cake::very easy]]" />
      )
      
      const expression = screen.getByText('piece of cake')
      
      // Click to show
      fireEvent.click(expression)
      await waitFor(() => {
        expect(screen.getByText('very easy')).toBeInTheDocument()
      })
      
      // Click to hide
      fireEvent.click(expression)
      await waitFor(() => {
        expect(screen.queryByText('very easy')).not.toBeInTheDocument()
      })
    })
  })

  describe('Keyboard Accessibility', () => {
    it('should have proper tabIndex for keyboard navigation', () => {
      render(
        <ExpressionText text="[[piece of cake::very easy]]" />
      )
      
      const expression = screen.getByText('piece of cake')
      expect(expression).toHaveAttribute('tabIndex', '0')
    })

    it('should show tooltip on focus', async () => {
      render(
        <ExpressionText text="[[piece of cake::very easy]]" />
      )
      
      const expression = screen.getByText('piece of cake')
      
      // Focus the expression
      fireEvent.focus(expression)
      
      await waitFor(() => {
        expect(screen.getByText('very easy')).toBeInTheDocument()
      })
    })

    it('should hide tooltip on blur', async () => {
      render(
        <ExpressionText text="[[piece of cake::very easy]]" />
      )
      
      const expression = screen.getByText('piece of cake')
      
      // Focus and show tooltip
      fireEvent.focus(expression)
      await waitFor(() => {
        expect(screen.getByText('very easy')).toBeInTheDocument()
      })
      
      // Blur and hide tooltip
      fireEvent.blur(expression)
      await waitFor(() => {
        expect(screen.queryByText('very easy')).not.toBeInTheDocument()
      })
    })

    it('should toggle tooltip on Enter key', async () => {
      render(
        <ExpressionText text="[[piece of cake::very easy]]" />
      )
      
      const expression = screen.getByText('piece of cake')
      
      // Press Enter to show
      fireEvent.keyDown(expression, { key: 'Enter', code: 'Enter' })
      await waitFor(() => {
        expect(screen.getByText('very easy')).toBeInTheDocument()
      })
    })

    it('should toggle tooltip on Space key', async () => {
      render(
        <ExpressionText text="[[piece of cake::very easy]]" />
      )
      
      const expression = screen.getByText('piece of cake')
      
      // Press Space to show
      fireEvent.keyDown(expression, { key: ' ', code: 'Space' })
      await waitFor(() => {
        expect(screen.getByText('very easy')).toBeInTheDocument()
      })
    })

    it('should hide tooltip on Escape key', async () => {
      render(
        <ExpressionText text="[[piece of cake::very easy]]" />
      )
      
      const expression = screen.getByText('piece of cake')
      
      // Show tooltip
      fireEvent.click(expression)
      await waitFor(() => {
        expect(screen.getByText('very easy')).toBeInTheDocument()
      })
      
      // Press Escape to hide
      fireEvent.keyDown(expression, { key: 'Escape', code: 'Escape' })
      await waitFor(() => {
        expect(screen.queryByText('very easy')).not.toBeInTheDocument()
      })
    })

    it('should have proper ARIA attributes', () => {
      render(
        <ExpressionText text="[[piece of cake::very easy]]" />
      )
      
      const expression = screen.getByText('piece of cake')
      expect(expression).toHaveAttribute('role', 'button')
      expect(expression).toHaveAttribute('aria-label', 'Expression: piece of cake. Meaning: very easy')
      expect(expression).toHaveAttribute('aria-expanded', 'false')
    })

    it('should update aria-expanded when tooltip is shown', async () => {
      render(
        <ExpressionText text="[[piece of cake::very easy]]" />
      )
      
      const expression = screen.getByText('piece of cake')
      expect(expression).toHaveAttribute('aria-expanded', 'false')
      
      // Show tooltip
      fireEvent.click(expression)
      await waitFor(() => {
        expect(expression).toHaveAttribute('aria-expanded', 'true')
      })
    })

    it('should have tooltip role', async () => {
      render(
        <ExpressionText text="[[piece of cake::very easy]]" />
      )
      
      const expression = screen.getByText('piece of cake')
      fireEvent.mouseEnter(expression)
      
      await waitFor(() => {
        const tooltip = screen.getByRole('tooltip')
        expect(tooltip).toBeInTheDocument()
        expect(tooltip).toHaveTextContent('very easy')
      })
    })
  })

  describe('Edge Cases', () => {
    it('should handle text with no expressions', () => {
      render(
        <ExpressionText text="Just normal text without any expressions." />
      )
      
      expect(screen.getByText('Just normal text without any expressions.')).toBeInTheDocument()
    })

    it('should handle incomplete expression markers', () => {
      render(
        <ExpressionText text="Incomplete [[expression without closing" />
      )
      
      // Should render as plain text when not properly formatted
      expect(screen.getByText('Incomplete [[expression without closing')).toBeInTheDocument()
    })

    it('should handle malformed expression (missing meaning)', () => {
      render(
        <ExpressionText text="[[phrase without meaning]]" />
      )
      
      // Should render as plain text when separator is missing
      expect(screen.getByText('[[phrase without meaning]]')).toBeInTheDocument()
    })

    it('should handle expressions with special characters', () => {
      render(
        <ExpressionText text="[[it's raining cats & dogs!::heavy rain]]" />
      )
      
      expect(screen.getByText("it's raining cats & dogs!")).toBeInTheDocument()
    })

    it('should handle expressions with colons in meaning', () => {
      render(
        <ExpressionText text="[[example::meaning: this has colons]]" />
      )
      
      // Should only split on the first ::
      expect(screen.getByText('example')).toBeInTheDocument()
    })

    it('should handle expressions with numbers', () => {
      render(
        <ExpressionText text="[[24/7::all day, every day]]" />
      )
      
      expect(screen.getByText('24/7')).toBeInTheDocument()
    })

    it('should handle expressions with unicode characters', () => {
      render(
        <ExpressionText text="[[café::coffee shop]] is nice" />
      )
      
      expect(screen.getByText('café')).toBeInTheDocument()
    })

    it('should handle very long expressions', () => {
      const longPhrase = 'this is a very long expression that goes on and on'
      const longMeaning = 'this is a very long meaning that also continues for a while'
      render(
        <ExpressionText text={`[[${longPhrase}::${longMeaning}]]`} />
      )
      
      expect(screen.getByText(longPhrase)).toBeInTheDocument()
    })

    it('should handle multiple expressions with different positions', () => {
      render(
        <ExpressionText 
          text="Start [[expr1::mean1]] middle [[expr2::mean2]] end [[expr3::mean3]]" 
        />
      )
      
      expect(screen.getByText('expr1')).toBeInTheDocument()
      expect(screen.getByText('expr2')).toBeInTheDocument()
      expect(screen.getByText('expr3')).toBeInTheDocument()
      expect(screen.getByText(/Start/)).toBeInTheDocument()
      expect(screen.getByText(/middle/)).toBeInTheDocument()
      expect(screen.getByText(/end/)).toBeInTheDocument()
    })
  })

  describe('Multiple Tooltips', () => {
    it('should allow showing multiple tooltips independently', async () => {
      render(
        <ExpressionText text="[[first::meaning1]] and [[second::meaning2]]" />
      )
      
      const first = screen.getByText('first')
      const second = screen.getByText('second')
      
      // Show first tooltip
      fireEvent.mouseEnter(first)
      await waitFor(() => {
        expect(screen.getByText('meaning1')).toBeInTheDocument()
      })
      
      // Show second tooltip (both should be visible)
      fireEvent.mouseEnter(second)
      await waitFor(() => {
        expect(screen.getByText('meaning2')).toBeInTheDocument()
      })
      
      expect(screen.getByText('meaning1')).toBeInTheDocument()
      expect(screen.getByText('meaning2')).toBeInTheDocument()
    })
  })
})
