import { FC } from 'react'
import Header from './components/Header'
import Main from './components/Main'
import Footer from './components/Footer'

const App: FC = () => {
  return (
    <div className="min-h-screen flex flex-col bg-gray-50">
      <Header />
      <Main />
      <Footer />
    </div>
  )
}

export default App
