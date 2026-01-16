import { createContext, FC, PropsWithChildren, useContext } from 'react'
import { useAGUIChat } from '../hooks/useAGUIChat'

const ChatContext = createContext<ReturnType<typeof useAGUIChat> | null>(null)

export const ChatProvider: FC<PropsWithChildren> = ({ children }) => {
  const chat = useAGUIChat()
  return <ChatContext.Provider value={chat}>{children}</ChatContext.Provider>
}

export const useChatContext = () => {
  const context = useContext(ChatContext)
  if (!context) {
    throw new Error('useChatContext must be used within a ChatProvider')
  }
  return context
}
