---
name: code-review
description: >
  Two-stage code review: first check spec compliance, then check code quality.
  Use when user says "review this", "code review", "check my code", "review PR",
  or before merging a branch.
user-invocable: true
model: opus
effort: high
argument-hint: "[file-or-branch]"
---

# Code Review Skill

Perform a structured two-stage review. Complete Stage 1 before Stage 2. Output a verdict for each category.

---

## Stage 1: Spec Compliance

Answer each question with PASS, FAIL, or N/A. For any FAIL, include a specific finding.

**Does the code do what was asked?**
- Re-read the original request or ticket description
- Trace the implementation path against the stated requirement
- If the requirement is ambiguous, flag it rather than assuming

**Are all acceptance criteria met?**
- Check every explicit criterion listed in the task, ticket, or PR description
- If no criteria were written down, note that absence as a process gap

**Are edge cases handled?**
- Empty/null inputs
- Boundary values (off-by-one, max length, zero)
- Concurrent access if applicable
- Error paths (network failure, DB unavailable, invalid user input)

**Does it match the approved design?**
- If a plan exists in `.planning/`, compare implementation against it
- Flag any deviations — even improvements must be consciously approved
- If no design document exists for a 3+ file change, note this as a workflow violation (see `rules/workflow.md`)

---

## Stage 2: Code Quality

**Security**
- SQL/command/template injection risks
- Auth bypass possibilities (missing middleware, incorrect guard placement)
- Sensitive data exposure (logging secrets, returning internal fields to client)
- Unvalidated user input reaching file paths, shell commands, or queries

**Performance**
- N+1 query patterns (loop containing a DB call)
- Unnecessary re-renders (React: missing memoization, unstable prop references)
- Missing database indexes for new query patterns
- Synchronous blocking in async contexts

**Maintainability**
- File size: flag any file exceeding 500 lines (project rule)
- Function complexity: flag any function exceeding 80 lines (project rule)
- Nesting depth: flag more than 3 levels (use early returns instead)
- Naming clarity: are variables and functions self-documenting?
- No commented-out code (project rule: delete it, git has history)

**Testing**
- Are new code paths covered by tests?
- Do tests assert behavior (outputs) rather than implementation (internal calls)?
- Are error paths tested (4xx responses, thrown exceptions)?
- Are test names descriptive of the scenario being tested?

**Style**
- Consistent with existing patterns in the codebase
- Follows naming conventions from `rules/coding-style.md`
- Import grouping: builtins → external → internal → relative
- No unhandled promise rejections; no silent catch blocks

---

## Output Format

```
## Code Review

### Stage 1: Spec Compliance
- Does what was asked:        PASS / FAIL — [finding]
- Acceptance criteria:        PASS / FAIL / N/A — [finding]
- Edge cases:                 PASS / FAIL — [finding]
- Matches approved design:    PASS / FAIL / N/A — [finding]

**Stage 1 Verdict**: PASS / FAIL

---

### Stage 2: Code Quality
- Security:        PASS / FAIL — [finding]
- Performance:     PASS / FAIL — [finding]
- Maintainability: PASS / FAIL — [finding]
- Testing:         PASS / FAIL — [finding]
- Style:           PASS / FAIL — [finding]

**Stage 2 Verdict**: PASS / FAIL

---

### Summary
[One paragraph: overall assessment, most critical finding, recommended next step.]

### Required Changes (block merge)
1. [specific actionable change]

### Suggested Improvements (non-blocking)
1. [specific suggestion]
```

If there are no required changes, state "None — approved to merge."
