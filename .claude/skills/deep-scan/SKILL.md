---
name: deep-scan
description: >
  Configurable multi-pass content audit pipeline with severity levels and trend tracking.
  Covers regulatory compliance, AI language markers, encoding integrity, source citations,
  content parity, and cannibalization detection. Use when user says "deep scan", "content audit",
  "regulatory check", "parity scan", or "source verification".
user-invocable: true
model: opus
effort: high
context: fork
argument-hint: "[scope: regulatory|parity|sources|all]"
---

# Deep Scan Pipeline

Configurable multi-pass content audit. Each pass can be enabled or disabled depending on the project.
Designed for websites, documentation, medical content, and multilingual sites — complements the
`overnight-sweep` skill (which focuses on code quality, not content quality).

---

## Configuration

Create `deep-scan-config.json` in project root to customize passes:

```json
{
  "passes": ["regulatory", "ai-language", "encoding", "sources", "parity", "cannibalization", "schema", "accessibility"],
  "suppressions": {
    "regulatory": ["redirect-stubs", "code-blocks"],
    "cannibalization": ["redirect-stubs"]
  },
  "domain": "medical",
  "languages": ["nb", "en"],
  "severity_threshold": "MEDIUM"
}
```

If no config exists, all passes run with default settings.

---

## Pass 1: Regulatory Compliance

Scan content for forbidden words and missing required disclaimers. Severity: **CRITICAL** for violations that could cause legal issues.

### What to Check
- **Forbidden superlatives**: best, leading, guaranteed, cures, fixes, eliminates (medical/health context)
- **Unqualified medical claims**: Claims without hedging ("reduces pain" vs "may help reduce pain")
- **Missing disclaimers**: Health content without "consult a healthcare professional" or equivalent
- **Testimonial violations**: Fake reviews, AggregateRating without real data, fabricated patient quotes
- **Fear-based marketing**: Urgency language designed to bypass informed consent

### Known False Positive Patterns (filter these)
1. **Redirect stubs**: Files < 2KB with `<meta http-equiv="refresh">` — skip entirely
2. **Code blocks**: Forbidden words inside `<code>`, `<pre>`, or fenced markdown — skip
3. **Cited sentences**: Sentences ending with `<sup>N</sup>` citation — sourced claims are not violations
4. **Quoted material**: Content inside `<blockquote>` from external sources — flag as INFO not CRITICAL
5. **Comparative language**: "better than average" in research context with citation — not a superlative violation
6. **Negations**: "not guaranteed", "no cure" — opposite meaning, not a violation
7. **Legal/disclaimer sections**: Content inside disclaimer/footer elements — already qualified

### Domain-Specific Word Lists
- **Medical**: kurerer, fikser, garantert, best, ledende, helbreder, eliminerer, smertefri
- **Required hedging (Norwegian)**: kan lindre, kan bidra til, kan hjelpe, mulig, potensielt
- **Required hedging (English)**: may help, can contribute to, potentially, evidence suggests
- **Financial**: guaranteed returns, risk-free, cannot lose
- **General**: #1, world's best, industry-leading, unmatched

---

## Pass 2: AI Language Markers

Detect patterns suggesting AI-generated content that hasn't been humanized. Severity: **MEDIUM**.

### Marker Categories
- **Hedging phrases**: "It's important to note", "It's worth mentioning", "It should be noted"
- **Formulaic transitions**: "Furthermore", "Moreover", "In conclusion", "That being said"
- **Excessive qualifiers**: "Significantly", "Remarkably", "Interestingly", "Notably"
- **List introductions**: "Here are some key considerations", "Let's explore"
- **Filler summaries**: "In summary", "To summarize", "Overall"
- **Empathy theater**: "I understand your concern", "That's a great question"

### Scoring
Count markers per file. Thresholds:
- 0-2 markers per 1000 words: PASS
- 3-5 markers per 1000 words: MEDIUM (review recommended)
- 6+ markers per 1000 words: HIGH (likely needs rewriting)

---

## Pass 3: Encoding Integrity

Detect character corruption from encoding mismatches. Severity: **CRITICAL** for visible corruption.

### Corruption Sequences to Detect
| Corrupted | Original | Language |
|-----------|----------|----------|
| Ã¥ | å | Norwegian/Swedish |
| Ã¸ | ø | Norwegian |
| Ã¦ | æ | Norwegian |
| Ã± | ñ | Spanish |
| Ã¼ | ü | German |
| Ã¶ | ö | Swedish/German |
| â€™ | ' | Smart quote |
| â€" | — | Em dash |
| â€" | – | En dash |

### Fix Pattern
If corruption found, use `[System.IO.File]::WriteAllText($path, $content, [System.Text.UTF8Encoding]::new($true))` (UTF8 with BOM) on Windows. On Unix: `iconv` or ensure files are saved as UTF-8 without BOM.

---

## Pass 4: Source Citations

Count inline citations and reference lists. Flag files with factual claims but no sources. Severity: **CRITICAL** for unsourced medical/health claims.

### What to Count
- **Inline citations**: `(Author et al., Year)`, `(Author, Year)`, `<sup>N</sup>` patterns
- **Reference lists**: `<li>` elements inside `<section class="sources-section">` or `<ol>` in sources
- **Legacy format**: `<div><p>` reference sections (count these separately — scripts may miss them)

### Severity Levels
- 0 inline citations + 0 references + factual claims present: **CRITICAL**
- 0 inline citations + references exist (but not linked to claims): **MEDIUM**
- Inline citations present + reference list: **PASS**
- No factual claims (e.g., navigation pages, contact pages): **N/A** — skip

### Known False Positives
- Redirect stubs (< 2KB with `<meta refresh>`) — always skip
- PWA offline pages — skip
- Index/listing pages with no factual claims — skip

---

## Pass 5: Content Parity

Compare paired files across languages. Severity: **HIGH** for structural mismatches.

### What to Compare
- **Word count ratio**: Flag if outside 0.8-1.3 range (translation should be similar length)
- **Section count**: Both versions should have the same number of `<h2>`/`<h3>` sections
- **Image count**: Same number of images (alt text may differ)
- **Schema parity**: Both versions should have the same structured data types
- **FAQ parity**: Same number of FAQ items
- **Missing pairs**: Files that exist in one language but not the other

### Pairing Strategy
Use hreflang tags to find pairs. If no hreflang, use directory structure mapping (e.g., `plager/korsrygg/` ↔ `en/conditions/lower-back-pain/`).

---

## Pass 6: Cannibalization Detection

Find pages targeting the same keywords. Severity: **HIGH** when 2+ pages compete for identical search intent.

### Detection Method
1. Extract `<title>` and `<meta name="description">` from each page
2. Extract `<h1>` text
3. Group pages by similar title/H1 keywords (>60% word overlap)
4. Flag groups where 2+ non-redirect pages target the same intent

### Known False Positives
- **Redirect stubs**: `<meta refresh>` pages that redirect to canonical — exclude from analysis
- **Language variants**: NO and EN versions of the same page — not cannibalization
- **Hub + sub-article**: A hub page mentioning a topic and a dedicated article — intentional hierarchy

---

## Pass 7: Schema Validation

Check JSON-LD structured data matches page content. Severity: **MEDIUM** for mismatches.

### Checks
- FAQPage schema: answers must match body text exactly (not paraphrased)
- MedicalWebPage schema: `about` field matches page topic
- Article schema: `datePublished` is not in the future, `author` is not empty
- BreadcrumbList: URLs in breadcrumb exist and are not 404
- AggregateRating: Only present if backed by real review data (NOT fabricated)

---

## Pass 8: Accessibility

Check content accessibility. Severity: **MEDIUM** for missing attributes.

### Checks
- Images without `alt` attribute
- Missing `lang` attribute on `<html>` element
- Missing `role="alert"` on emergency/red-flag content
- Links without descriptive text (no "click here")
- Missing skip-to-content link
- Color contrast issues (if tooling available)
- Missing ARIA labels on interactive elements

---

## Output Format

Generate report at: `reports/deep-scan-YYYY-MM-DD.md`

```markdown
# Deep Scan Report — YYYY-MM-DD

## Summary

| Pass | Status | CRITICAL | HIGH | MEDIUM | LOW | Files Scanned |
|------|--------|----------|------|--------|-----|---------------|
| Regulatory | PASS/FAIL | N | N | N | N | N |
| AI Language | PASS/FAIL | — | N | N | — | N |
| Encoding | PASS/FAIL | N | — | — | — | N |
| Sources | PASS/FAIL | N | — | N | — | N |
| Parity | PASS/FAIL | — | N | N | — | N |
| Cannibalization | PASS/FAIL | — | N | — | — | N |
| Schema | PASS/FAIL | — | — | N | — | N |
| Accessibility | PASS/FAIL | — | — | N | N | N |

## Trend (vs. previous scan)
[If previous report exists, show delta: +N new issues, -N fixed, N unchanged]

## Details
[Per-pass findings with file paths, line numbers, and specific violations]

## Suppressions Applied
[List any false-positive filters that were active]
```

---

## Complementary Skills

| Need | Use |
|------|-----|
| Code quality audit | `overnight-sweep` |
| Content quality audit | `deep-scan` (this skill) |
| Visual regression | `visual-check` |
| SEO health | `seo-audit` |
| Translation parity | `i18n-parity` |
