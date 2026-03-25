# Skills Index

| Skill | Trigger | Purpose |
|-------|---------|---------|
| `design-first` | Any change touching 3+ files | Mandatory design gate: read, plan, approve, execute |
| `compliance-audit` | Regulatory content review | Scan for compliance violations and regulatory issues |
| `overnight-sweep` | Batch quality pass | Run full-suite quality checks across the Python codebase |
| `visual-check` | UI verification | Visual regression and layout verification |
| `code-review` | Code review | Two-stage review: spec compliance then quality |
| `ui-audit` | UI verification | 6-pillar UI audit: copywriting, visuals, color, typography, spacing, UX |
| `rpi-workflow` | Background knowledge | Research-Plan-Implement development methodology (not user-invocable) |
| `tool-mastery` | Background knowledge | Advanced tool use patterns: PTC, ToolSearch, filtering (not user-invocable) |
| `web-research` | Background knowledge | Web research patterns: Firecrawl, WebSearch, WebFetch workflows (not user-invocable) |
| `dream` | Memory consolidation | 4-phase memory consolidation: orient, gather, consolidate, prune. Auto-triggers after 24hr gap. |

Skills marked "Background knowledge" are not user-invocable. They are loaded into agents via the `skills:` frontmatter field to provide domain knowledge.

## Removed Skills (SB2 saas preset — not applicable to Python trading project)

The following skills were removed during fine-tuning:
- `seo-*` (8 skills) — No website to SEO
- `i18n-parity` — No multi-language support
- `multi-tenant-audit` — Not a SaaS application
- `onboarding-flow` — No user accounts
- `api-docs` — No REST API
- `deep-scan` — Medical content audit (TheBackROM-specific)
