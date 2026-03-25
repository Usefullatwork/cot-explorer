---
name: dream
description: >
  Memory consolidation skill. Runs 4 phases: orient, gather signal, consolidate, prune.
  Synthesizes session learnings into durable project memory. Use when wrapping up a session,
  after major milestones, or when prompted by the auto-trigger (24hr+ gap).
  Triggers: "dream", "consolidate memory", "session review", "what did we learn".
user-invocable: true
model: opus
effort: high
argument-hint: "[auto|manual|status]"
---

# Memory Consolidation (/dream)

## When to Run
- End of a productive session (manual: `/dream`)
- After 24+ hours since last consolidation (auto-triggered via Stop hook)
- After major milestones (feature complete, sprint end, release)
- When context feels stale or memory is cluttered

## 4-Phase Process

### Phase 1: Orient
Understand current memory state before making changes.

1. Read the project's `MEMORY.md` index file
2. Read the project's `CLAUDE.md` for current conventions
3. Read `.planning/progress.md` or session logs if they exist
4. List agent memory files in `.claude/agent-memory/` if any exist
5. Summarize: what does memory currently track? What's the freshness?

### Phase 2: Gather Signal
Collect raw signal from the current session and recent history.

1. Check `git log --oneline -20` for recent commits — what changed?
2. Read `.planning/` directory for task plans, progress notes, snapshots
3. Identify patterns:
   - **Conventions established** — naming, file organization, coding patterns
   - **Decisions made** — architectural choices, tool preferences, workflow adjustments
   - **What worked** — approaches that succeeded, efficient patterns
   - **What failed** — approaches that were abandoned, errors encountered
   - **Feedback received** — user corrections, preference signals
4. Check for stale information — completed projects, outdated patterns

### Phase 3: Consolidate
Update memory with new learnings. Apply these rules:

1. **New patterns** — Create new memory file with proper frontmatter (type: feedback or project)
2. **Updated patterns** — Edit existing memory file to reflect current state
3. **Confirmed patterns** — Leave unchanged (don't touch what's working)
4. **Stale entries** — Mark for pruning in Phase 4

Write changes to actual memory files — this is not a dry run.
Update MEMORY.md index if new files were created or old ones removed.

### Phase 4: Prune
Remove outdated information to keep memory lean.

1. Delete memory files for completed/abandoned projects (after confirming with user)
2. Remove entries from MEMORY.md that point to deleted files
3. Consolidate duplicate or overlapping memories into single entries
4. Update timestamps/descriptions on memories that were refreshed
5. Report: what was added, updated, and pruned

## Output Format

After completing all 4 phases, report:

```
## Dream Report

### Session Summary
[1-2 sentence summary of what happened]

### New Memories
- [memory-file.md] — [what was learned]

### Updated Memories
- [memory-file.md] — [what changed]

### Pruned
- [memory-file.md] — [why removed]

### Memory Health
- Total files: N
- Fresh (< 7 days): N
- Stale (> 30 days): N
- Next dream recommended: [date]
```

## Updating the Timestamp

After a successful dream, write the current Unix timestamp to `.planning/last-dream-timestamp`:
```bash
date +%s > .planning/last-dream-timestamp
```

This allows the `should-dream.sh` Stop hook to track when the next dream is due.

## Constraints
- Never delete memory without user confirmation (use AskUserQuestion)
- Never overwrite memory — always read first, then merge
- Keep MEMORY.md under 200 lines (truncation happens beyond that)
- Prefer updating existing memories over creating new ones
- One memory per topic — no duplicates
