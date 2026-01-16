/**
 * ExpressionText Component
 * 
 * Parses and renders text containing expression markup [[phrase::meaning]].
 * Displays highlighted expressions with interactive tooltips showing meanings.
 * 
 * Features:
 * - Visual highlighting of expressions
 * - Hover tooltips with meanings
 * - Keyboard navigation support
 * - Mobile-friendly (tap to show/hide tooltip)
 * - Handles multiple expressions in single text
 * - Edge case handling (nested brackets, special chars)
 * 
 * Refer to PRD section 5.3 and 6.2 for specifications.
 */

import { FC, useState, useRef, useEffect, KeyboardEvent } from 'react'

export interface Expression {
  phrase: string
  meaning: string
}

interface ParsedSegment {
  type: 'text' | 'expression'
  content: string
  expression?: Expression
}

interface ExpressionTextProps {
  text: string
  className?: string
}

// Constants
const TOOLTIP_VIEWPORT_MARGIN = 10 // Minimum distance from viewport edge in pixels

/**
 * Parse text containing [[phrase::meaning]] markup into segments
 */
function parseText(text: string): ParsedSegment[] {
  const segments: ParsedSegment[] = []
  // Match [[phrase::meaning]] with non-greedy matching
  // [^\]]+ ensures at least one character that's not a closing bracket
  const pattern = /\[\[([^\]]+?)::([^\]]+?)\]\]/g
  let lastIndex = 0
  let match

  while ((match = pattern.exec(text)) !== null) {
    // Add text before the expression
    if (match.index > lastIndex) {
      segments.push({
        type: 'text',
        content: text.slice(lastIndex, match.index),
      })
    }

    // Add the expression
    segments.push({
      type: 'expression',
      content: match[1].trim(),
      expression: {
        phrase: match[1].trim(),
        meaning: match[2].trim(),
      },
    })

    lastIndex = pattern.lastIndex
  }

  // Add remaining text
  if (lastIndex < text.length) {
    segments.push({
      type: 'text',
      content: text.slice(lastIndex),
    })
  }

  return segments
}

/**
 * HighlightedExpression - Individual expression with tooltip
 */
interface HighlightedExpressionProps {
  phrase: string
  meaning: string
}

const HighlightedExpression: FC<HighlightedExpressionProps> = ({ phrase, meaning }) => {
  const [isTooltipVisible, setIsTooltipVisible] = useState(false)
  const [tooltipPosition, setTooltipPosition] = useState<'top' | 'bottom'>('top')
  const expressionRef = useRef<HTMLSpanElement>(null)
  const tooltipRef = useRef<HTMLDivElement>(null)

  // Check tooltip position to avoid clipping
  useEffect(() => {
    if (isTooltipVisible && expressionRef.current && tooltipRef.current) {
      const expressionRect = expressionRef.current.getBoundingClientRect()
      const tooltipRect = tooltipRef.current.getBoundingClientRect()
      
      // If tooltip would go off top of viewport, show it below instead
      if (expressionRect.top - tooltipRect.height < TOOLTIP_VIEWPORT_MARGIN) {
        setTooltipPosition('bottom')
      } else {
        setTooltipPosition('top')
      }
    }
  }, [isTooltipVisible])

  const handleMouseEnter = () => {
    setIsTooltipVisible(true)
  }

  const handleMouseLeave = () => {
    setIsTooltipVisible(false)
  }

  const handleClick = () => {
    // Toggle tooltip on click for mobile/touch devices
    setIsTooltipVisible(!isTooltipVisible)
  }

  const handleKeyDown = (e: KeyboardEvent<HTMLSpanElement>) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault()
      setIsTooltipVisible(!isTooltipVisible)
    } else if (e.key === 'Escape') {
      setIsTooltipVisible(false)
    }
  }

  const handleFocus = () => {
    setIsTooltipVisible(true)
  }

  const handleBlur = () => {
    setIsTooltipVisible(false)
  }

  return (
    <span className="relative inline-block">
      <span
        ref={expressionRef}
        className="expression-highlight cursor-help px-1 rounded transition-colors duration-200 bg-indigo-100 text-indigo-900 border-b-2 border-indigo-400 hover:bg-indigo-200 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-1"
        onMouseEnter={handleMouseEnter}
        onMouseLeave={handleMouseLeave}
        onClick={handleClick}
        onKeyDown={handleKeyDown}
        onFocus={handleFocus}
        onBlur={handleBlur}
        tabIndex={0}
        role="button"
        aria-label={`Expression: ${phrase}. Meaning: ${meaning}`}
        aria-expanded={isTooltipVisible}
      >
        {phrase}
      </span>
      {isTooltipVisible && (
        <div
          ref={tooltipRef}
          className={`expression-tooltip absolute left-1/2 -translate-x-1/2 z-50 px-3 py-2 text-sm text-white bg-gray-900 rounded-lg shadow-lg whitespace-nowrap pointer-events-none ${
            tooltipPosition === 'top' 
              ? 'bottom-full mb-2' 
              : 'top-full mt-2'
          }`}
          role="tooltip"
        >
          {meaning}
          <div
            className={`absolute left-1/2 -translate-x-1/2 w-2 h-2 bg-gray-900 rotate-45 ${
              tooltipPosition === 'top'
                ? '-bottom-1'
                : '-top-1'
            }`}
          />
        </div>
      )}
    </span>
  )
}

/**
 * ExpressionText - Main component
 * 
 * Parses text with [[phrase::meaning]] markup and renders with interactive highlights
 */
const ExpressionText: FC<ExpressionTextProps> = ({ text, className = '' }) => {
  const segments = parseText(text)

  return (
    <span className={className}>
      {segments.map((segment, index) => {
        if (segment.type === 'expression' && segment.expression) {
          return (
            <HighlightedExpression
              key={`expr-${index}`}
              phrase={segment.expression.phrase}
              meaning={segment.expression.meaning}
            />
          )
        }
        return <span key={`text-${index}`}>{segment.content}</span>
      })}
    </span>
  )
}

export default ExpressionText
