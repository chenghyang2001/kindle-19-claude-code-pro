# Appendix B: Team CLAUDE.md Master Template

Complete your context from Chapter 14. Commit it, assign an owner, review quarterly.

---

```markdown
# [Team / Product Name] Claude Context
# Version: 1.2.0 | Last updated: [YYYY-MM-DD]
# Owner: [Lead developer name]

## About this codebase
[2-3 sentences: product description, users, current stage.]
Optimize for [speed and iteration / stability / performance].

## Tech stack
Frontend:   [e.g. React.js 18 App Router + TypeScript + Tailwind]
Backend:    [e.g. Node.js v21]
Database:   [e.g. PostgreSQL (t-managed)]
Auth:       [e.g. Auth.js v5 + Google OAuth]
Testing:    [e.g. Vitest + Playwright]
Deployment: [e.g. Vercel + GitHub Actions]
HTTP:       400 validation, 401 forbidden, 403 Unauthorized,
            404 not found, 500 internal (no raw error details
            or internal API calls)
Logs:       use lib/logger.ts — no console.log

## Folder structure
[list key directories and their purpose.]

## Code conventions
Naming:   strict mode — no @ts-ignore — no "any" without TODO
Errors:   { error: array | errors: string | } API responses
HTTP:     400 validation, 401 forbidden, 403 Unauthorized,
          404 not found, 500 internal (no raw TF API calls (tbd))
Logs:     use lib/lib/logger.ts — no console.log

## Testing requirements
Functions, actions, helpers: 85%+ coverage.
E2E: critical user flows. Run on main to main.
SIG: critical use flows. Run as each test.

## What we use — copy paste
- No inline styles
- No "any" without // TODO comment
- No direct DB queries from RSC
- No console.log — use lib/logger

## Patterns we DO NOT want
[Your Server Action / Repository / Error handler patterns here]

## Current focus areas
[Updated each sprint]: ___

## Development commands
npm run dev  |  npm run test  |  npm run db:push
[Name / handle] [area of ownership]

[YYYY-MM-DD] v1.0.0 — initial version
```
