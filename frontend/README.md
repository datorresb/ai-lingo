# AI Lingo Frontend

React-based frontend application for the AI Lingo Expression Learner.

## Features

- **SessionSetup Component**: Language variant selection (US, UK, Custom)
- **Chat Component**: Interactive conversation interface
- **useAGUIChat Hook**: State management for sessions and messages
- Real-time streaming responses with SSE
- Error handling with retry functionality
- Responsive design

## Getting Started

### Prerequisites

- Node.js 18+ 
- npm or yarn

### Installation

```bash
cd frontend
npm install
```

### Development

```bash
npm run dev
```

The application will start at `http://localhost:3000`

### Build

```bash
npm run build
```

Build output will be in the `dist/` directory.

### Lint

```bash
npm run lint
```

## Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── SessionSetup.tsx    # Language variant selection
│   │   ├── SessionSetup.css
│   │   ├── Chat.tsx             # Chat interface
│   │   └── Chat.css
│   ├── hooks/
│   │   └── useAGUIChat.ts       # State management hook
│   ├── App.tsx                  # Main app component
│   ├── main.tsx                 # Entry point
│   └── index.css                # Global styles
├── index.html
├── package.json
├── tsconfig.json
└── vite.config.ts
```

## API Integration

The frontend expects the following backend endpoints:

- `POST /api/session` - Create a new session
  - Request: `{ variant: string }`
  - Response: `{ session_id: string }`

- `POST /api/chat` - Send a message
  - Request: `{ session_id: string, message: string }`
  - Response: Server-Sent Events (SSE) stream

## Configuration

Backend API proxy is configured in `vite.config.ts`:
- All `/api/*` requests are proxied to `http://localhost:8000`
- Modify the proxy target if your backend runs on a different port

## Components

### SessionSetup

Initial screen for selecting language variant. Features:
- Radio button selection for US, UK, or Custom English
- Loading state during session initialization
- Error messages with retry option
- Smooth transition to chat after session creation

### Chat

Main chat interface. Features:
- Message history display
- Real-time message sending
- Typing indicators
- Session ID display
- Responsive design

### useAGUIChat Hook

Manages application state:
- `sessionId`: Current session identifier
- `messages`: Message history
- `isLoading`: Loading state
- `error`: Error messages
- `events`: Agent thought process events
- `startSession(variant)`: Initialize new session
- `sendMessage(message)`: Send message to agent
- `clearError()`: Clear error state
