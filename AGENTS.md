# Project - Agent Instructions

> **MANDATORY ENFORCEMENT**: This file is automatically loaded for ALL AI interactions in this workspace.

## Project Identity

This project uses **Mayor West Mode** - autonomous GitHub Copilot development workflows.

## Agent Hierarchy

| Pattern | Agent | Location |
|---------|-------|----------|
| `**` | Mayor West Mode | `.github/agents/mayor-west-mode.md` |

## Mandatory Rules

1. **Never auto-approve destructive commands**: `rm`, `kill`, `reset --hard`
2. **Always run tests before committing**
3. **Use commit format**: `[MAYOR] <description>`
4. **Include `Fixes #<issue>` in PR body**
5. **Workflow cycle**: crear issue → implementar → PR a dev → merge → cerrar issue → continuar

## Development Commands

```bash
npm install           # Install dependencies
npm test              # Run tests
npm run lint          # Lint code
```

## Available Skills

### React Best Practices
**Location:** `.github/skills/react-best-practices/`

Vercel's comprehensive React and Next.js performance optimization guidelines. Contains 45 rules across 8 categories:

1. **Eliminating Waterfalls** (CRITICAL) - `async-*` prefix
   - Defer/parallelize promises, use Suspense for streaming
   
2. **Bundle Size Optimization** (CRITICAL) - `bundle-*` prefix
   - Dynamic imports, barrel avoidance, conditional loading
   
3. **Server-Side Performance** (HIGH) - `server-*` prefix
   - React.cache(), LRU caching, data serialization
   
4. **Re-render Optimization** (MEDIUM) - `rerender-*` prefix
   - Memoization, dependencies, state management
   
5. **Rendering Performance** (MEDIUM) - `rendering-*` prefix
   - SVG optimization, content-visibility, hydration
   
6. **JavaScript Performance** (LOW-MEDIUM) - `js-*` prefix
   - DOM batching, lookup optimization, algorithm efficiency

**Apply when:** Writing React components, Next.js pages, optimizing performance, reviewing code.

### Web Design Guidelines
**Location:** `.github/skills/web-design-guidelines/`

Vercel's web interface design and accessibility guidelines. Fetches latest rules from:
```
https://raw.githubusercontent.com/vercel-labs/web-interface-guidelines/main/command.md
```

**Apply when:** Reviewing UI code, checking accessibility, auditing design, reviewing UX compliance.

## Skill References

When working on tasks:
- **Frontend/React work:** Reference `.github/skills/react-best-practices/SKILL.md` and rules
- **UI/Design review:** Reference `.github/skills/web-design-guidelines/SKILL.md`
