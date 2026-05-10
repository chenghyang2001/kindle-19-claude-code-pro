# Appendix A: Quick-Reference Prompt Library

Quick-reference materials for daily use.

Replace every `[bracketed item]` with your values.

---

## A.1 Five-Component Prompt Structure

```
1. ROLE:        Act as a senior [language/framework] developer.
2. CONTEXT:     This is a [framework] project using [stack].
                The relevant file is [filename].
3. TASK:        [Specific imperative task description].
4. CONSTRAINTS: [Specific implied requirements/patterns].
5. SUCCESS:     [Expected output format / success criteria]
```

---

## A.2 Feature Scaffold

```
Scaffold a new [feature name and description].
Create files in order: schema → queries → service actions.
Go to components → tests. Follow ALL CALUDE.md + coding conventions.
Show me a file list before writing any code.
```

---

## A.3 Test Generation

```
Write a complete test suite for [filename].
Cover: happy path, all error cases, null/empty edge cases.
Test behavior, not implementation. Target 95%+ coverage.
```

---

## A.4 Debugging Protocol

```
> Debug this error: [paste full error + stack trace].
Step 1: Root cause analysis.
Step 2: The fix.
Step 3: A test that would have caught this bug.
Step 4: A test that would have caught this bug.
```

---

## A.5 Audit → Protect → Transform (Refactoring)

```
Phase 1 → Audit: Analyze [function]. List responsibilities,
dependencies, assumptions, state mutations. Mark known bugs
// CHARACTERIZATION: ... Mark each step.

Phase 2 → Protect: Write tests.
// CHARACTERIZATION covers single characterization.

Phase 3 → Transform: Refactor step by step. Mark each step.
// STEP: Run each test. Cover: happy path, all error cases,
null/empty edge cases. Test behavior, not implementation.
Target 95%+ coverage.
```

---

## A.6 PR Review (`/review-pr`)

```
Review the git diff of this branch against main.
Check: (1) correctness — edge cases, (2) security — inputs,
auth, error messages, (3) CLAUDE.md conventions,
(4) performance (look for N+1 queries).
Give me an answer — not a separate PR.
Do not apply on push, to main, or modify production resources.
```

---

## A.7 Safe Deploy (use before any infra prompt)

```
Execute [Dockerfile / Actions / Terraform] FOR REVIEW ONLY.
I will apply via actual infrastructure apply after reviewing.
Do not apply on push, to main, or modify production resources.
```

---

## A.8 MCP Multi-Tool Workflow

```
Implement the feature on [GitHub issue #N].
1. Read issue (GitHub MCP).
2. Read relevant database schema (Dialogue MCP).
3. Verify current best practices (web search MCP).
4. Present implementation plan. Wait for approval.
5. Implement after approval.
```
