import { FC } from 'react'
import Welcome from './Welcome'

const Main: FC = () => {
  return (
    <main className="flex-1">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <Welcome />
      </div>
    </main>
  )
}

export default Main
