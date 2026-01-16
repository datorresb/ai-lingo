import { useAGUIChat } from './hooks/useAGUIChat';
import SessionSetup from './components/SessionSetup';
import Chat from './components/Chat';

function App() {
  const {
    sessionId,
    messages,
    isLoading,
    error,
    startSession,
    sendMessage,
    clearError,
  } = useAGUIChat();

  // Show SessionSetup if no session exists
  if (!sessionId) {
    return (
      <SessionSetup
        onSessionStart={startSession}
        isLoading={isLoading}
        error={error}
        onClearError={clearError}
      />
    );
  }

  // Show Chat once session is created
  return (
    <Chat
      messages={messages}
      onSendMessage={sendMessage}
      isLoading={isLoading}
      sessionId={sessionId}
    />
  );
}

export default App;
