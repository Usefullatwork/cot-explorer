---
name: tool-mastery
description: Advanced Claude Code tool use patterns including parallel tool calls, ToolSearch, dynamic filtering, and permission governance. Background knowledge for efficiency-focused agents.
user-invocable: false
disable-model-invocation: true
---

# Tool Mastery: Advanced Claude Code Tool Use Patterns

Background reference for agents that need to operate at peak efficiency. These four patterns reduce token cost, context pressure, and permission friction across all types of agentic work.

---

## 1. Parallel Tool Calls (PTC)

**What it is:** Sending multiple independent tool calls in a single message instead of chaining them sequentially. Claude Code processes all calls in the batch concurrently and returns all results before the next turn.

**Why it matters:** Sequential tool calls each consume a round-trip (prompt + response). PTC eliminates redundant prompt overhead -- benchmarks show ~37% context reduction on file-heavy tasks.

### When to use

- Reading multiple files whose content does not depend on each other
- Running independent Grep/Glob searches across different patterns
- Executing unrelated Bash commands (e.g., `git status` + `npm test`)
- Fetching multiple URLs in parallel

### When NOT to use

- When call B needs the result of call A (e.g., read a file to find an import path, then read that imported file)
- When calls modify shared state and ordering matters (e.g., write then read the same file)

### Example

**Sequential (wasteful -- 5 round trips):**
```
Read /src/auth.ts          -> wait -> Read /src/db.ts   -> wait ->
Read /src/routes.ts        -> wait -> Read /tests/auth.test.ts -> wait ->
Read /config/settings.json -> wait
```

**Parallel (1 round trip):**
```
Read /src/auth.ts
Read /src/db.ts
Read /src/routes.ts
Read /tests/auth.test.ts
Read /config/settings.json
```
All five results arrive together. The agent processes them as a batch and proceeds.

**Parallel Bash example:**
```
Bash: git status
Bash: git diff --stat HEAD~1
Bash: npm run lint -- --format=compact
```
All three run concurrently. If any one fails, the others still complete.

### Rule of thumb

Any time you have a mental list of "things I need to look at," batch them all into one message. Only sequence when there is a genuine data dependency.

---

## 2. ToolSearch for Deferred Tools

**What it is:** Many tools in Claude Code are deferred -- their schemas are not loaded into the context window until explicitly requested. ToolSearch fetches the schema for one or more tools on demand, making them callable for the remainder of the session.

**Why it matters:** Loading all tool schemas upfront would consume a large portion of every context window. Deferred loading keeps the base prompt lean (~85% token reduction vs. full schema preload). Agents that know which tools they need can fetch schemas precisely when required.

### When to use

- When a system reminder lists a tool name but the tool is not yet callable
- When you need a niche capability (browser automation, notebook editing, MCP tools) for a single task
- When you want to confirm a tool's exact parameter schema before calling it

### Query formats

| Format | Effect | Example |
|--------|--------|---------|
| `select:Tool1,Tool2` | Exact fetch by name | `select:Read,Edit,Grep` |
| `keyword search` | Fuzzy match against tool descriptions | `notebook jupyter` |
| `+required keyword` | Require a term in the name, rank by rest | `+slack send` |

### Example

A system reminder lists `WebFetch` and `NotebookEdit` as deferred. Before calling either:

```
ToolSearch query: "select:WebFetch,NotebookEdit"
```

The response returns both schemas inside a `<functions>` block. From that point forward, `WebFetch` and `NotebookEdit` are callable exactly like built-in tools.

**Keyword search example** -- you know you need a browser tool but not the exact name:
```
ToolSearch query: "browser screenshot"
```
Returns the best-matching browser automation tool with its full schema.

### Best practice

Fetch tool schemas in the same message as your first use, or in the message immediately before. Do not fetch speculatively -- only load what you will actually call.

---

## 3. Dynamic Tool Filtering via `allowed-tools`

**What it is:** The `allowed-tools` frontmatter field in a skill or agent definition restricts which tools are available when that skill is active. Tools not in the list require explicit permission prompts (or are blocked entirely if in `deny`).

**Why it matters:** Restricting tools serves two purposes:
1. **Prompt size** -- fewer tool schemas loaded = smaller context window per turn
2. **Safety** -- prevents accidental destructive tool use in read-only or analysis workflows

### When to use

- Read-only skills (audits, analysis, reporting) -- restrict to `Read`, `Grep`, `Glob`
- Write-scoped skills -- allow only the tools needed (e.g., `Edit`, `Write`, `Bash` for specific scripts)
- Subagents with a narrow responsibility -- keeps agents from drifting into unintended operations

### Example: read-only audit skill

```yaml
---
name: code-auditor
description: Reads and analyzes code without making changes
user-invocable: false
allowed-tools:
  - Read
  - Grep
  - Glob
  - Bash(git log *)
  - Bash(git diff *)
---
```

This skill cannot call `Edit`, `Write`, or any destructive `Bash` variant. Any attempt to do so triggers a permission prompt, which serves as an explicit reminder that the skill is being misused.

### Example: scoped writer skill

```yaml
---
name: docs-writer
description: Writes and updates Markdown documentation only
allowed-tools:
  - Read
  - Glob
  - Edit(*.md)
  - Write(docs/**)
---
```

`Edit` is scoped to `.md` files only. Attempting to edit a `.ts` file triggers a permission request. This enforces the skill's contract at the tool layer rather than relying on instructions alone.

### Interaction with `deny` rules

`allowed-tools` controls what is pre-approved. The `deny` rules in `settings.json` remain in effect regardless -- a tool listed in `allowed-tools` can still be blocked by a `deny` rule at a higher settings level.

---

## 4. Permission Governance

**What it is:** Claude Code's permission system controls which tools run automatically, which require user confirmation, and which are blocked entirely. Rules are evaluated at every tool call.

**Precedence:** `deny > ask > allow`

The `deny` tier is absolute -- it cannot be overridden by `allow` or `ask` rules at any lower settings level. This makes deny rules reliable for security policies.

### Permission modes (set via `permissionMode` in agent frontmatter or `defaultMode` in settings)

| Mode | Behavior | Best for |
|------|----------|----------|
| `default` | Standard prompts for anything not in `allow` | Interactive sessions |
| `acceptEdits` | Auto-accepts file edits, prompts for Bash | CI-adjacent workflows |
| `bypassPermissions` | Skips all checks | Fully automated swarm agents |
| `plan` | Read-only -- no modifications | Analysis, planning passes |

### Domain-specific allows

Restrict `WebFetch` to specific domains to prevent agents from fetching arbitrary URLs:

```json
{
  "permissions": {
    "allow": [
      "WebFetch(domain:api.pubmed.ncbi.nlm.nih.gov)",
      "WebFetch(domain:cochranelibrary.com)",
      "WebFetch(domain:statpearls.com)"
    ],
    "deny": [
      "WebFetch(domain:*)"
    ]
  }
}
```

The `deny` wildcard blocks all domains; specific `allow` entries carve out exceptions. Place the catch-all deny at a higher settings scope (managed or team settings) and the specific allows at a lower scope (project or user settings) -- within a single scope, deny wins; across scopes, allows at lower levels are still concatenated in.

### Path-scoped tool permissions

```json
{
  "permissions": {
    "allow": [
      "Edit(src/**)",
      "Write(docs/**)",
      "Read(.env)"
    ],
    "deny": [
      "Read(./secrets/**)",
      "Bash(rm *)"
    ]
  }
}
```

Path patterns follow gitignore syntax with four prefix types:
- `//path` -- absolute from filesystem root
- `~/path` -- relative to home directory
- `/path` -- relative to project root
- `./path` or `path` -- relative to current directory

### `permissionMode` in agent frontmatter

```yaml
---
name: release-deployer
description: Deploys builds to staging -- runs without prompts
permissionMode: bypassPermissions
tools: Bash, Write, WebFetch
---
```

```yaml
---
name: safe-reviewer
description: Read-only code review -- never modifies files
permissionMode: plan
tools: Read, Grep, Glob, Bash(git *)
---
```

`bypassPermissions` is appropriate for fully automated pipeline agents where a human has already reviewed the task definition. `plan` mode is the safest option for analysis agents -- it enforces read-only behavior at the runtime level, not just through instructions.

### Governance hierarchy summary

```
managed-settings.json / MDM / Registry    <- organization-enforced, cannot be overridden
  .claude/settings.json                   <- team-shared, committed to repo
    .claude/settings.local.json           <- personal project overrides, git-ignored
      ~/.claude/settings.json             <- global personal defaults
```

Array fields (`permissions.allow`, `permissions.deny`) are concatenated across all levels -- rules from every level are active simultaneously. If managed settings include a deny rule, it applies even if a lower level adds an allow for the same tool.

---

## Quick Reference

| Pattern | Primary benefit | Key constraint |
|---------|-----------------|----------------|
| Parallel Tool Calls | ~37% context reduction | Only for independent calls |
| ToolSearch | ~85% schema token reduction | Fetch only what you will use |
| `allowed-tools` | Smaller context + safety | Cannot override `deny` rules |
| Permission governance | Predictable security posture | `deny > ask > allow`, always |
