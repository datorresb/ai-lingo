/**
 * ExpressionText Usage Example
 * 
 * This file demonstrates how to use the ExpressionText component
 * to display text with highlighted expressions and interactive tooltips.
 */

import { FC } from 'react'
import ExpressionText from './ExpressionText'

const ExpressionTextExample: FC = () => {
  return (
    <div className="max-w-4xl mx-auto p-8 space-y-8">
      <div className="bg-white rounded-lg shadow-md p-6">
        <h1 className="text-3xl font-bold text-gray-900 mb-6">
          ExpressionText Component Examples
        </h1>

        {/* Example 1: Single Expression */}
        <div className="mb-8">
          <h2 className="text-xl font-semibold text-gray-800 mb-3">
            1. Single Expression
          </h2>
          <div className="bg-gray-50 p-4 rounded border border-gray-200">
            <ExpressionText 
              text="Learning English idioms is [[a piece of cake::very easy]] with this tool!"
              className="text-lg text-gray-700"
            />
          </div>
          <p className="text-sm text-gray-600 mt-2">
            Hover over the highlighted phrase to see its meaning
          </p>
        </div>

        {/* Example 2: Multiple Expressions */}
        <div className="mb-8">
          <h2 className="text-xl font-semibold text-gray-800 mb-3">
            2. Multiple Expressions
          </h2>
          <div className="bg-gray-50 p-4 rounded border border-gray-200">
            <ExpressionText 
              text="Don't worry, it's [[a piece of cake::very easy]]! Just [[break the ice::start a conversation]] and you'll be fine. Remember, [[practice makes perfect::improvement comes with practice]]."
              className="text-lg text-gray-700"
            />
          </div>
        </div>

        {/* Example 3: Real Conversation Example */}
        <div className="mb-8">
          <h2 className="text-xl font-semibold text-gray-800 mb-3">
            3. Chat Message Example
          </h2>
          <div className="bg-indigo-50 p-4 rounded-lg border-l-4 border-indigo-500">
            <div className="flex items-start gap-3">
              <div className="flex-shrink-0 w-8 h-8 bg-indigo-600 rounded-full flex items-center justify-center text-white font-semibold">
                AI
              </div>
              <div className="flex-1">
                <div className="text-sm text-gray-600 mb-1">Assistant</div>
                <ExpressionText 
                  text="That's interesting! In tech startups, you often hear people say they need to [[think outside the box::be creative and innovative]]. Sometimes they [[burn the midnight oil::work late into the night]] to meet deadlines. It's not always [[a walk in the park::easy]], but when you're passionate about your work, it's worth it!"
                  className="text-gray-800"
                />
              </div>
            </div>
          </div>
        </div>

        {/* Example 4: Edge Cases */}
        <div className="mb-8">
          <h2 className="text-xl font-semibold text-gray-800 mb-3">
            4. Special Characters & Numbers
          </h2>
          <div className="bg-gray-50 p-4 rounded border border-gray-200">
            <ExpressionText 
              text="We're open [[24/7::all day, every day]]! It's important to [[dot your i's and cross your t's::pay attention to details]]."
              className="text-lg text-gray-700"
            />
          </div>
        </div>

        {/* Example 5: No Expressions */}
        <div className="mb-8">
          <h2 className="text-xl font-semibold text-gray-800 mb-3">
            5. Plain Text (No Expressions)
          </h2>
          <div className="bg-gray-50 p-4 rounded border border-gray-200">
            <ExpressionText 
              text="This is just regular text without any expressions. The component handles this gracefully."
              className="text-lg text-gray-700"
            />
          </div>
        </div>

        {/* Keyboard Navigation Instructions */}
        <div className="bg-blue-50 p-4 rounded border border-blue-200">
          <h3 className="font-semibold text-blue-900 mb-2">
            ⌨️ Keyboard Navigation
          </h3>
          <ul className="text-sm text-blue-800 space-y-1">
            <li>• <kbd className="px-2 py-1 bg-white rounded border border-blue-300">Tab</kbd> - Navigate between expressions</li>
            <li>• <kbd className="px-2 py-1 bg-white rounded border border-blue-300">Enter</kbd> or <kbd className="px-2 py-1 bg-white rounded border border-blue-300">Space</kbd> - Toggle tooltip</li>
            <li>• <kbd className="px-2 py-1 bg-white rounded border border-blue-300">Esc</kbd> - Hide tooltip</li>
          </ul>
        </div>

        {/* Mobile Note */}
        <div className="bg-green-50 p-4 rounded border border-green-200 mt-4">
          <h3 className="font-semibold text-green-900 mb-2">
            📱 Mobile Support
          </h3>
          <p className="text-sm text-green-800">
            On mobile devices, tap an expression to show/hide its tooltip. The tooltips are positioned to avoid clipping.
          </p>
        </div>
      </div>
    </div>
  )
}

export default ExpressionTextExample
