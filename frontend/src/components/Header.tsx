import { FC } from 'react'

const Header: FC = () => {
  return (
    <header className="bg-white shadow">
      <nav className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
        <div className="flex justify-between items-center">
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-bold text-indigo-600">AI Lingo</h1>
            <span className="text-gray-600 text-sm">Expression Learning Tool</span>
          </div>
          <div className="flex gap-4">
            <a 
              href="#" 
              className="text-gray-700 hover:text-indigo-600 font-medium transition"
            >
              Home
            </a>
            <a 
              href="#" 
              className="text-gray-700 hover:text-indigo-600 font-medium transition"
            >
              Learn
            </a>
            <a 
              href="#" 
              className="text-gray-700 hover:text-indigo-600 font-medium transition"
            >
              About
            </a>
          </div>
        </div>
      </nav>
    </header>
  )
}

export default Header
