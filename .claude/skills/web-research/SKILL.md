---
name: web-research
description: >
  Web research patterns using Firecrawl, WebSearch, and WebFetch for deep research,
  competitive analysis, and documentation scraping. Background knowledge for research agents.
user-invocable: false
disable-model-invocation: true
---

# Web Research Patterns

Background knowledge for agents that need to research the web. Covers tool selection,
research workflows, and ethical practices.

---

## Tool Selection

| Need | Tool | When |
|------|------|------|
| Discover information | WebSearch | Don't know which URLs have the answer |
| Read a specific page | WebFetch | Have a URL, need its content |
| Crawl an entire site | Firecrawl | Need comprehensive content from a domain |
| Visual page analysis | Playwright | Need to see rendered UI, not just HTML |

### Firecrawl Patterns

Firecrawl converts web pages to clean markdown — ideal for feeding content into agent context.

**When to use Firecrawl over WebFetch**:
- Crawling documentation sites (multi-page, structured)
- Extracting clean text from complex layouts (removes nav, ads, boilerplate)
- Converting competitor sites to analyzable markdown
- Building knowledge bases from web content

**Common patterns**:
- Documentation crawl: Crawl `/docs/*` pages to build context for a framework
- Competitor analysis: Crawl competitor landing pages for messaging, features, pricing
- Content audit: Crawl your own site to check content quality at scale
- Research synthesis: Crawl multiple sources, then synthesize findings

### WebSearch Patterns

**Query formulation by research type**:
- Academic: `"systematic review" OR "meta-analysis" [topic] site:pubmed.ncbi.nlm.nih.gov`
- Documentation: `[framework] [feature] site:docs.[framework].com`
- Competitor: `[competitor name] [feature] pricing OR plans`
- Market research: `[industry] trends 2026 report`
- Stack Overflow: `[error message] [language] site:stackoverflow.com`

**Triangulation**: Always verify findings across 2+ independent sources. A single search result is a lead, not a fact.

### WebFetch Patterns

**Use for**:
- Checking HTTP response headers (security headers, caching)
- Reading specific documentation pages when you know the URL
- Verifying that a page exists and returns 200
- Extracting schema markup, meta tags, or specific content from a known URL

---

## Research Workflow

### Multi-Step Research Pattern

1. **Broad search** — WebSearch with general query to discover relevant sources
2. **Narrow** — Refine query based on initial results, target specific domains
3. **Deep read** — WebFetch or Firecrawl the most promising sources
4. **Verify** — Cross-reference claims across 2+ sources
5. **Synthesize** — Combine findings into structured output with citations

### Critical Rule: Never Guess URLs

URLs hallucinated by language models often return 404 or lead to unrelated content.

**Always**:
- Search first, then fetch URLs from search results
- Verify URLs exist before citing them
- Use domain-specific searches (`site:`) to find correct documentation pages

**Never**:
- Construct URLs from memory (e.g., "the docs are probably at docs.example.com/api/v2/...")
- Assume URL patterns (e.g., "/blog/2026/03/article-title")
- Cite a URL you haven't actually fetched and read

---

## Rate Limiting and Ethics

- **Respect robots.txt** — Don't crawl pages excluded by robots.txt
- **Space requests** — Wait 1-2 seconds between fetches to the same domain
- **Public data only** — Don't scrape paywalled, login-required, or private content
- **No PII collection** — Don't extract personal information from web pages
- **Cache results** — Don't re-fetch the same URL multiple times in a session
- **Attribution** — When using web content, cite the source URL
