# Product Requirements Document (PRD) — Expression Learner Agent

**Project:** Demo Vibe App  
**Date:** 2026-01-15  
**Status:** In Progress  

## 1. Executive Summary

The **Expression Learner** is a conversational AI agent designed to help users learn English idioms, slang, and expressions (US/UK variants). The agent engages in natural conversation, adopting a native speaker persona. It uses RSS feeds to propose relevant discussion topics (News, Tech, Culture) and provides real-time learning aids by highlighting idioms in its responses with tooltips explaining their meaning.

## 2. Objectives

1.  **Immersive Learning:** Provide a natural conversational partner that simulates a native speaker (US or UK).
2.  **Contextual Education:** Teach idioms in context rather than in isolation.
3.  **Transparency:** Visualize the agent's reasoning process (ReAct pattern) to the user.
4.  **Simplicity:** Minimal session state, clear "Select -> Chat -> Learn" user flow.

## 3. User Journey

1.  **Session Setup:**
    *   User launches the app.
    *   User selects a language variant (e.g., "US English", "UK English", or "Custom").
2.  **Topic Selection:**
    *   The agent fetches current headlines from configured RSS feeds (e.g., BBC, NYT, TechCrunch).
    *   The agent presents 3-5 interesting topics to the user.
    *   User selects a topic to discuss.
3.  **Conversation:**
    *   The conversation begins. The agent adopts the persona associated with the selected variant.
    *   The agent integrates relevant idioms and expressions naturally into the dialogue.
4.  **Learning Interaction:**
    *   In the chat interface, idioms and expressions used by the agent are **visually highlighted**.
    *   Hovering over a highlight reveals a **tooltip** with a concise definition/meaning.
    *   The chat interface also shows the Agent's "Thought" process (inner monologue) separately from the final response.

## 4. System Architecture

### 4.1. Technical Stack

*   **Frontend:** React, Vite, TypeScript, Tailwind CSS (or custom CSS).
    *   **Core Components:** `SessionSetup`, `Chat`, `EventLog` (for thoughts), `ExpressionText` (for highlighting).
*   **Backend:** Python 3.12+, FastAPI.
*   **AI Orchestration:** LangGraph (State Graph), LangChain.
*   **LLM:** Azure OpenAI (GPT-3.5/4) via `langchain-openai`.
*   **Infrastructure:** Azure Container Apps (Bicep).

### 4.2. Folder Structure

```
demo-vibe-app/
├── backend/
│   ├── app/
│   │   └── main.py              # FastAPI entrypoint
│   ├── src/
│   │   ├── agents/
│   │   │   ├── agent.py         # LangGraph definition
│   │   │   ├── state.py         # AgentState definition
│   │   │   └── tools.py         # RSS & helper tools
│   │   ├── core/
│   │   │   ├── expressions.py   # Idiom extraction/normalization logic
│   │   │   ├── rss_client.py    # RSS fetching logic
│   │   │   └── models.py        # Pydantic domain models
│   └── pyproject.toml
├── frontend/
│   ├── src/
│   │   ├── components/          # React components
│   │   └── hooks/               # useAGUIChat hook
│   └── vite.config.ts
└── infra/                       # Bicep deployment templates
```

## 5. Backend Specifications

### 5.1. API Endpoints

| Method | Endpoint | Description | Request Body | Response |
| :--- | :--- | :--- | :--- | :--- |
| `GET` | `/` | Metadata | - | Service info |
| `GET` | `/health` | Liveness probe | - | `{"status": "healthy"}` |
| `POST` | `/session` | Init session | `SessionRequest(variant)` | `SessionResponse(session_id, ...)` |
| `POST` | `/chat` | Chat turn | `ChatRequest(session_id, message)` | `StreamingResponse` (SSE/text) |
| `POST` | `/start_chat`| Start topic gen | `StartChatRequest(session_id)` | `StreamingResponse` |

### 5.2. Agent Logic (LangGraph)

The agent is implemented as a state graph (`workflow`).

*   **State (`AgentState`):**
    *   `messages`: List of LangChain messages.
    *   `variant`: "US", "UK", etc.
    *   `topic`: Current discussion topic.
    *   `last_expressions`: List of idioms found in the last turn `[{phrase, meaning}]`.
    *   `turn_count`: Integer.
*   **Nodes:**
    *   `agent`: Main LLM call. Decides to call tools or respond.
    *   `tools`: Executes RSS tools (`list_topics`, `get_article_snippet`).
*   **Tools:**
    *   `list_topics(feed_url, limit)`: Returns headlines.
    *   `get_article_snippet(url)`: Fetches context for the agent.

### 5.3. Expression Extraction

The agent is instructed via System Prompt to mark idiomatic expressions in its response.
*   **Format:** The backend expects the LLM to format expressions as `[[phrase::meaning]]` (e.g., `[[a piece of cake::very easy]]`).
*   **Processing:**
    *   The frontend must parse this specific markup to render the Highlight + Tooltip.
    *   Alternatively, a backend middleware can parse this and return a structured response, but the current design relies on the text stream containing these markers for the frontend to handle.

## 6. Frontend Specifications

### 6.1. State Management (`useAGUIChat`)

*   Manages `sessionId`, `messages` list, `isLoading`, `events` (for debug/observation).
*   Handles SSE (Server-Sent Events) or streaming response parsing from the backend.

### 6.2. UI Components

*   **`SessionSetup`:** Simple form to pick variant.
*   **`Chat`:** Main message list.
    *   **User Message:** Simple bubble.
    *   **Agent Message:** Rendered text. MUST use `ExpressionText` component to parse and render highlights.
*   **`ExpressionText`:** Parses the agent's markup (e.g., Markdown or specific XML) to render interactive tooltips for idioms.
*   **`EventLog`:** A side panel or drawer showing the "Thoughts" (intermediate steps from LangGraph/LangChain) to satisfy the "ReAct visible" requirement.

## 7. Configuration & Environment

Required environment variables:
*   `AZURE_OPENAI_ENDPOINT`
*   `AZURE_OPENAI_DEPLOYMENT_NAME`
*   `AZURE_OPENAI_API_VERSION`
*   `AZURE_CLIENT_ID` (for Managed Identity)

## 8. Success Criteria

1.  User can successfully start a session with a specific variant (e.g., UK).
2.  Agent proposes real-world topics from RSS.
3.  Agent responds in character.
4.  Idioms in agent response are clickable/hoverable with correct definitions.
5.  System deploys successfully to Azure Container Apps.
 