import { FC } from 'react'

const Welcome: FC = () => {
  return (
    <div className="text-center">
      <h2 className="text-4xl font-bold text-gray-900 mb-4">
        Welcome to AI Lingo
      </h2>
      <p className="text-lg text-gray-600 mb-8 max-w-2xl mx-auto">
        An intelligent platform for learning and understanding expressions through AI-powered analysis.
      </p>
      <button className="bg-indigo-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-indigo-700 transition">
        Get Started
      </button>
    </div>
  )
}

export default Welcome
