# ai-lingo

Learn how to speak AI language

## 🚀 Expression Learner Agent

A conversational AI agent designed to help users learn English idioms, slang, and expressions (US/UK variants) through natural conversation.

**Status**: 🔨 In Development (Mayor West Mode)

---

## 📋 Project Overview

The **Expression Learner** is part of the Demo Vibe App, providing:
- 💬 Natural conversational partner (native speaker persona)
- 📰 Real-world topics from RSS feeds (BBC, NYT, TechCrunch)
- 🎯 Idioms highlighted in context with tooltips
- 🧠 Visible reasoning process (ReAct pattern)
- 🌍 Multiple language variants (US English, UK English)

**Refer to [PRD.md](./PRD.md) for complete specifications.**

---

## 📊 Development Progress

### ✅ Completed (1/17)
- [x] **#1 - Backend: Setup FastAPI project structure** (PR #18)
  - ✅ FastAPI app with GET / and GET /health endpoints
  - ✅ Project structure with pyproject.toml (no version pinning)
  - ✅ 2 tests passing
  - ✅ Installation with `uv` package manager
  - ✅ CORS middleware configured
  - ✅ .env.example for configuration

### 🔄 Next in Queue
- [ ] **#2 - Backend: Implement Pydantic domain models**
- [ ] **#9 - Frontend: Setup React + Vite + TypeScript** (can run parallel)

### ⏳ Pending (15/17)

**Backend (6 remaining)**
- [ ] #2 - Implement Pydantic domain models
- [ ] #3 - Implement RSS client for fetching headlines
- [ ] #4 - Implement expression extraction and normalization
- [ ] #5 - Implement LangGraph agent state and workflow
- [ ] #6 - Implement /session endpoint
- [ ] #7 - Implement /start_chat endpoint with topic generation
- [ ] #8 - Implement /chat endpoint with streaming response

**Frontend (7 issues)**
- [ ] #9 - Setup React + Vite + TypeScript project
- [ ] #10 - Implement useAGUIChat custom hook
- [ ] #11 - Implement ExpressionText component for idiom highlights
- [ ] #12 - Implement SessionSetup component
- [ ] #13 - Implement Chat component with message display
- [ ] #14 - Implement EventLog component for agent reasoning
- [ ] #15 - Implement App component with routing and layout

**Infrastructure & Docs (2 issues)**
- [ ] #16 - Setup Bicep templates for Azure Container Apps
- [ ] #17 - Create setup and development guide

---

## 🛠 Tech Stack

- **Backend**: Python 3.12+, FastAPI, LangGraph, LangChain
- **Frontend**: React, Vite, TypeScript, Tailwind CSS
- **AI/LLM**: Azure OpenAI (GPT-3.5/4)
- **Infrastructure**: Azure Container Apps (Bicep)
- **Package Manager**: `uv` (fast Python dependency management)
- **Skills**: Vercel React Best Practices (45 rules), Web Design Guidelines

---

## 📦 Installation

### Backend Setup

```bash
cd backend

# Install with uv (recommended - faster than pip)
uv sync
uv pip install -e .[dev]

# Run tests
uv run pytest tests/ -v

# Start development server
uv run uvicorn app.main:app --reload
```

### Frontend Setup (Coming Soon)

```bash
cd frontend
npm install
npm run dev
```

---

## 📂 Project Structure

```
ai-lingo/
├── backend/
│   ├── app/
│   │   └── main.py              # FastAPI entrypoint
│   ├── src/
│   │   ├── agents/              # LangGraph agents
│   │   └── core/                # Models, utilities
│   ├── tests/                   # Test suite
│   └── pyproject.toml           # Dependencies (uv format)
├── frontend/                    # React + Vite (Coming)
├── infra/                       # Bicep templates (Coming)
├── .github/
│   ├── agents/
│   │   └── mayor-west-mode.md   # Agent protocol
│   └── skills/                  # Vercel skills
├── PRD.md                       # Product Requirements Doc
├── AGENTS.md                    # Agent instructions
├── CHANGELOG.md                 # Changes log
├── env.example                  # Environment variables
└── README.md                    # This file
```

---

## 🚀 Development Workflow (Mayor West Mode)

### Setup (Mayor West Mode)

Run the setup wizard from GitHub:

```bash
npx github:shyamsridhar123/MayorWest setup
```

### Working on an Issue

1. **Read Issue**: Understand acceptance criteria
2. **Create Branch**: `git checkout -b feature/issue-description`
3. **Implement**: Follow project conventions
4. **Test**: `uv run pytest` - ALL tests must pass
5. **Commit**: `[MAYOR] Description: Details (Closes #N)`
6. **Push**: `git push origin feature/branch-name`
7. **PR**: Automatically created with issue link

### Commit Format

```
[MAYOR] Backend setup: FastAPI project with health endpoint

- Added FastAPI entrypoint
- Created project structure
- Added health check endpoint
- All tests passing

Closes #1
```

---

## 📚 Available Skills & Guidelines

### React Best Practices
**Location**: [.github/skills/react-best-practices/](./github/skills/react-best-practices/)

45 optimization rules across 8 categories for React/Next.js performance

### Web Design Guidelines
**Location**: [.github/skills/web-design-guidelines/](./github/skills/web-design-guidelines/)

UI/UX and accessibility best practices from Vercel

---

## 📋 Roadmap

### Phase 1: Foundation ✅ (1/2)
- [x] Backend FastAPI setup
- [ ] Frontend React setup

### Phase 2: Models & Utilities (0/5)
- [ ] Pydantic models
- [ ] RSS client
- [ ] Expression extraction
- [ ] useAGUIChat hook
- [ ] ExpressionText component

### Phase 3: Agent & API (0/4)
- [ ] LangGraph workflow
- [ ] /session endpoint
- [ ] /start_chat endpoint
- [ ] /chat endpoint

### Phase 4: Frontend Components (0/4)
- [ ] SessionSetup
- [ ] Chat
- [ ] EventLog
- [ ] App

### Phase 5: Deployment (0/2)
- [ ] Bicep templates
- [ ] Documentation

---

## 🔗 Key Files

- **[PRD.md](./PRD.md)** - Product Requirements Document
- **[AGENTS.md](./AGENTS.md)** - Agent instructions
- **[CHANGELOG.md](./CHANGELOG.md)** - Version history

---

## 📝 License

MIT

---

**Last Updated**: January 15, 2026  
**Current Progress**: 1/17 issues completed (6%)
