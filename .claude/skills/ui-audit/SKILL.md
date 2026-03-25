---
name: ui-audit
description: >
  6-pillar UI audit covering copywriting, visuals, color, typography, spacing, and experience
  design. Scores each pillar 1-4 and provides specific, actionable findings. Use when user says
  "UI audit", "design review", "UX check", "audit the interface", or "check the design".
user-invocable: true
effort: high
argument-hint: "[url-or-path]"
---

# 6-Pillar UI Audit

Score a user interface across 6 pillars on a 1-4 scale. For each pillar, run every check, record specific findings with file paths and line numbers, then assign a score. Finish with a scorecard and overall grade.

## Scoring Scale

| Score | Label | Meaning |
|-------|-------|---------|
| 4 | Excellent | No issues found. Production-ready. |
| 3 | Good | Minor issues only. Ship with notes. |
| 2 | Needs Work | Multiple issues that hurt usability or consistency. Fix before shipping. |
| 1 | Poor | Fundamental problems. Redesign or rewrite required. |

## Overall Grade

Calculate the average of all 6 pillar scores, then map to a letter grade:

| Average | Grade |
|---------|-------|
| 3.5-4.0 | A |
| 3.0-3.4 | B |
| 2.5-2.9 | C |
| 2.0-2.4 | D |
| 1.0-1.9 | F |

---

## How to Run the Audit

1. **Identify scope** -- which pages, components, or views to audit. If the user does not specify, audit the main layout and one representative page.
2. **Gather files** -- Read all relevant HTML/JSX/TSX templates, CSS/SCSS/Tailwind files, and component files.
3. **Run each pillar** -- Execute every check listed below. Record findings with severity (CRITICAL / WARNING / NOTE).
4. **Score each pillar** -- Assign 1-4 based on findings.
5. **Produce the scorecard** -- Use the output format at the bottom.
6. **List actionable fixes** -- Prioritize by severity, group by pillar.

---

## Pillar 1: Copywriting (Score 1-4)

Evaluate all user-facing text for clarity, consistency, and persuasive value.

### Checks

**1.1 Generic Labels**
- Search for vague button/link text: "Submit", "Click Here", "OK", "Next", "Back", "Page 1", "Go", "Enter"
- Every action label should communicate what happens: "Save Patient Record", "Book Appointment", "Download Report"
- Tool: Grep for common generic patterns in JSX/HTML (`>Submit<`, `>Click Here<`, `>OK<`, `>Next<`)

**1.2 Terminology Consistency**
- Identify the primary domain nouns (e.g., "patient", "user", "client", "customer", "member")
- Flag any page that uses more than one term for the same concept
- Check navigation labels match page headings (sidebar says "Settings" but page title says "Preferences")
- Tool: Grep for each noun variant, compare file-by-file usage counts

**1.3 Microcopy Coverage**
- Empty states: Does every list/table/feed have a zero-content message with guidance? ("No appointments yet. Book your first appointment.")
- Loading states: Are there loading messages or just silent spinners?
- Error messages: Are form validation errors specific? ("Password must be at least 8 characters" not "Invalid input")
- Success confirmations: Do destructive or important actions confirm completion?
- Tool: Search for empty state patterns (`no.*found`, `no.*yet`, `empty`, placeholder text in components)

**1.4 Tone Consistency**
- Is the tone formal, casual, or mixed across pages?
- Do error messages blame the user ("You entered an invalid email") vs. guide them ("Please enter a valid email address")?
- Are headings parallel in structure? (All imperatives, all nouns, or mixed?)
- Check that marketing pages and app UI do not clash in tone

**1.5 CTA Value Communication**
- Primary CTAs should state the benefit, not just the action: "Start Free Trial" vs "Sign Up", "Get Your Report" vs "Submit"
- Check that CTAs are written from the user perspective, not the system perspective
- Verify that destructive CTAs are clearly marked: "Delete Account" not "Remove", with confirmation text

**1.6 Placeholder Text and Lorem Ipsum**
- Search for "lorem ipsum", "placeholder", "TODO", "FIXME", "TBD", "xxx" in user-facing text
- Check that form placeholders show format hints ("john@example.com") not labels ("Email")
- Tool: Grep for `lorem|placeholder|TODO|FIXME|TBD|xxx` in template files

**1.7 Truncation and Overflow**
- Check for text that may overflow containers (long names, translated strings)
- Verify that truncated text has tooltips or expand affordances
- Look for hardcoded string lengths that assume English character counts

---

## Pillar 2: Visual Hierarchy (Score 1-4)

Evaluate how effectively the layout guides the eye and communicates importance.

### Checks

**2.1 Focal Point on Load**
- Does the page have one clear primary element above the fold?
- Is it obvious within 3 seconds what the page is for and what to do first?
- Check that the primary CTA is visually dominant (larger, colored, high contrast)

**2.2 Weight Distribution**
- Flag pages where all elements have equal visual weight (everything bold, everything the same size)
- Check for proper heading hierarchy: H1 > H2 > H3 in both size and weight
- Verify that secondary actions are visually subordinate to primary actions (ghost buttons, text links, muted colors)
- Tool: Search CSS for heading styles -- verify progressive size/weight reduction

**2.3 Above-the-Fold Content**
- Key actions and primary content must be visible without scrolling on 1280x720 viewport
- Check for excessive headers, banners, or navigation that push content down
- Verify that the most important information is not buried in a sidebar or below a large hero

**2.4 Card and Panel Consistency**
- Are cards/panels the same height in a row? (Flexbox/Grid alignment check)
- Do similar cards use the same structure (image, title, description, action)?
- Flag inconsistent border-radius, shadow, or padding across card variants
- Tool: Search CSS for `.card`, `.panel`, `.box` -- compare padding/radius/shadow values

**2.5 Visual Grouping (Gestalt Proximity)**
- Related elements should be closer together than unrelated elements
- Check that form labels are closer to their inputs than to the previous input
- Verify section boundaries are clear (spacing, dividers, or background color changes)
- Flag "floating" elements that do not visually belong to any group

**2.6 Information Density**
- Tables and data-heavy views: is there enough whitespace between rows/columns?
- Dashboards: are widgets sized proportional to their importance?
- Forms: are inputs grouped logically with section headers for long forms (>6 fields)?

**2.7 Responsive Hierarchy Preservation**
- Does the visual hierarchy hold on mobile? (Primary CTA still prominent, headings still scaled)
- Check that desktop sidebar content does not disappear on mobile without alternative access
- Verify that stacked mobile layouts maintain logical reading order

---

## Pillar 3: Color (Score 1-4)

Evaluate color usage for accessibility, consistency, and semantic correctness.

### Checks

**3.1 Accent Color Count**
- Count distinct accent/brand colors used across the interface
- More than 3 competing accent colors creates visual noise -- flag it
- Identify the primary, secondary, and tertiary accent colors and verify consistent usage
- Tool: Search CSS for color definitions, extract unique hues

**3.2 Contrast Ratios (WCAG AA)**
- Text on backgrounds must meet minimum 4.5:1 contrast ratio (AA standard)
- Large text (18px+ or 14px+ bold) needs minimum 3:1
- Interactive elements (buttons, links) need 3:1 against adjacent colors
- Flag any light gray text on white backgrounds, or colored text on colored backgrounds
- Tool: Extract text color + background color pairs from CSS, calculate ratios

**3.3 Semantic Color Usage**
- Red = error/danger/destructive -- never for success or neutral actions
- Green = success/positive/confirmed -- never for errors or warnings
- Yellow/Orange = warning/caution -- never for success
- Blue = informational/primary -- typical for links and primary actions
- Flag any semantic color violations (green "Delete" button, red "Success" badge)
- Tool: Search for color assignments on error/success/warning/info elements

**3.4 Dark Mode Readiness**
- Are colors defined as CSS custom properties (variables) or hardcoded hex values?
- Hardcoded colors in component files make dark mode impossible -- flag them
- Check for `prefers-color-scheme` media queries or a theme toggle mechanism
- Flag any `color: #000` or `background: #fff` hardcoded in component styles
- Tool: Grep for hardcoded hex colors in component files vs. CSS variable usage

**3.5 Brand Color Consistency**
- Is the primary brand color used consistently for the same purpose across all pages?
- Flag pages where the primary action button is a different color than other pages
- Check that hover/active/focus states use the same color family (darker/lighter shade, not a different hue)

**3.6 Color as Sole Indicator**
- Color must never be the only way to communicate information (accessibility requirement)
- Error fields: do they have an icon or text in addition to a red border?
- Status indicators: do they have labels in addition to colored dots?
- Charts/graphs: do they use patterns or labels in addition to colors?
- Tool: Search for error/status/badge components -- verify non-color indicators exist

**3.7 Background and Surface Layers**
- Are there clear visual layers? (Page background, card surface, modal overlay)
- Flag flat designs where cards and page background are the same color with no border or shadow
- Verify modal/dialog overlays dim the background to establish depth

---

## Pillar 4: Typography (Score 1-4)

Evaluate font usage for readability, consistency, and systematic application.

### Checks

**4.1 Font Size Scale**
- Count distinct font sizes used across the interface
- More than 5-6 distinct sizes indicates no type scale -- flag it
- Ideal: use a modular scale (e.g., 12, 14, 16, 20, 24, 32) or Tailwind default scale
- Flag any "magic number" font sizes (13px, 17px, 22px) that do not fit a system
- Tool: Grep CSS for `font-size` declarations, extract and deduplicate values

**4.2 Font Weight Consistency**
- Count distinct font weights used
- More than 3 weights (regular, medium/semibold, bold) is excessive -- flag it
- Verify that weight assignments are semantic: regular for body, medium for labels, bold for headings
- Flag `font-weight: 900` or `font-weight: 100` unless part of a display/hero font

**4.3 Line Height (Leading)**
- Body text: line-height should be 1.4-1.7 (too tight below 1.4, too loose above 2.0)
- Headings: line-height should be 1.1-1.3 (tighter than body)
- Flag any line-height values below 1.2 for body text or above 2.0 for any text
- Tool: Grep CSS for `line-height` declarations, check values

**4.4 Responsive Font Scaling**
- Do font sizes adjust for mobile? (Media queries, clamp(), fluid typography)
- Flag base font sizes below 14px on mobile (too small for touch devices)
- Check that heading sizes scale down proportionally -- H1 should not be the same size on mobile and desktop
- Tool: Search for responsive font declarations (`@media`, `clamp(`, `vw` units in font-size)

**4.5 Line Length (Measure)**
- Optimal reading measure: 45-75 characters per line
- Flag any content container wider than 75ch or ~700px without max-width constraint
- Blog/article content is especially sensitive -- check `max-width` on prose containers
- Tool: Check content container widths in CSS -- `max-width` on article/prose/content classes

**4.6 Font Family Consistency**
- Count distinct font families used
- More than 2 families (one sans-serif, one monospace for code) is suspicious -- flag it
- Verify font fallback stacks include system fonts: `Inter, system-ui, -apple-system, sans-serif`
- Flag missing font fallbacks (`font-family: "Fancy Font"` with no fallback)
- Tool: Grep CSS for `font-family` declarations

**4.7 Text Alignment**
- Body text should be left-aligned (not justified -- causes rivers of whitespace)
- Center-aligned text should be limited to headings, short labels, and hero sections
- Flag justified text (`text-align: justify`) in any content area
- Flag center-aligned paragraphs longer than 3 lines

**4.8 Heading Hierarchy**
- Verify H1 through H6 have progressively smaller sizes and lighter weights
- Check that each page has exactly one H1
- Flag skipped heading levels (H1 then H3 with no H2)
- Tool: Check heading tag usage in HTML/JSX and corresponding CSS sizes

---

## Pillar 5: Spacing (Score 1-4)

Evaluate whitespace usage for consistency, rhythm, and visual comfort.

### Checks

**5.1 Spacing System**
- Are spacing values based on a consistent scale? (4px/8px grid, Tailwind spacing scale, or custom tokens)
- Flag "magic number" spacing values (5px, 7px, 13px, 19px) that do not fit a system
- Check if spacing is defined as design tokens/CSS variables or scattered as raw values
- Tool: Grep CSS for `padding` and `margin` declarations, extract unique values

**5.2 Component Internal Padding**
- Cards, buttons, inputs, and containers should have consistent internal padding
- Flag buttons where padding varies between instances (one has `8px 16px`, another has `10px 20px`)
- Verify input fields have uniform height and padding across the app
- Tool: Compare padding values on `.btn`, `.card`, `input`, `.modal` classes

**5.3 Section Spacing**
- Major sections should have generous vertical spacing (32-80px depending on design)
- Flag sections that are too close together (creating a "wall of content" feel)
- Verify that section spacing is larger than within-section element spacing (establishes hierarchy)

**5.4 Element Proximity**
- Labels should be closer to their associated input than to the previous field input (Gestalt proximity)
- Button groups should have consistent gap between buttons
- List items should have uniform spacing
- Flag any form where `margin-bottom` on labels equals or exceeds `margin-bottom` on input groups

**5.5 Symmetry and Alignment**
- Padding should be symmetric where expected (same top/bottom, same left/right)
- Flag asymmetric padding that should be symmetric: `padding: 12px 16px 8px 16px`
- Check that grid/flex gaps are consistent within a layout section
- Verify horizontal alignment of elements in the same visual column

**5.6 Whitespace Breathing Room**
- Check for cramped interfaces: too many elements packed into a small area
- Verify that clickable/tappable elements have sufficient spacing (minimum 8px gap between touch targets)
- Mobile: touch targets should be at least 44x44px (WCAG) with adequate spacing between them
- Flag dense data tables on mobile without horizontal scrolling or responsive adaptation

**5.7 Consistent Gaps in Repeated Patterns**
- Card grids: are gaps uniform? (No mixed 16px and 24px gaps in the same grid)
- Navigation items: are gaps uniform?
- Sidebar menu items: are gaps uniform?
- Tool: Check `gap`, `grid-gap`, or margin values on repeated layout patterns

**5.8 Vertical Rhythm**
- Do text blocks maintain a consistent baseline rhythm?
- Check that the spacing between paragraphs matches the line-height or a multiple thereof
- Flag inconsistent spacing between heading and first paragraph across different sections

---

## Pillar 6: Experience Design (Score 1-4)

Evaluate interaction states, feedback patterns, and defensive design.

### Checks

**6.1 Loading States**
- Do async operations show loading feedback? (Spinner, skeleton screen, progress bar)
- Is the loading indicator contextual (near the loading content) or global (page-level)?
- Check that buttons show loading state during form submission (disable + spinner)
- Flag any fetch/API call that lacks a loading state in the UI
- Tool: Search for loading/spinner/skeleton components and verify usage alongside data fetching

**6.2 Empty States**
- Every list, table, feed, and search results view needs a zero-content state
- Empty states should explain WHY it is empty and WHAT to do: "No patients found. Add your first patient."
- Flag generic "No data" messages without actionable guidance
- Tool: Search for empty state text, conditional renders for zero-length arrays

**6.3 Error States**
- Form validation: are errors inline (next to the field) or only at the top of the form?
- Network errors: is there a retry mechanism or at least a clear error message?
- 404/500 pages: do they exist and provide navigation back to safety?
- Check that error messages are user-friendly (not raw exception text or error codes)
- Tool: Search for error boundary components, form validation patterns, error message strings

**6.4 Interaction Feedback**
- Buttons: do they have hover, active, focus, and disabled states?
- Links: do they have hover and focus states distinct from surrounding text?
- Inputs: do they have focus ring, error, and disabled states?
- Check that keyboard focus indicators are visible (not suppressed with `outline: none` without replacement)
- Tool: Search CSS for `:hover`, `:focus`, `:active`, `:disabled` pseudo-classes on interactive elements

**6.5 Confirmation for Destructive Actions**
- Delete, remove, cancel subscription, and similar actions MUST have a confirmation step
- The confirmation should restate what will happen: "This will permanently delete 3 patient records"
- Check that the destructive option is NOT the pre-selected or visually dominant button in the confirmation dialog
- Tool: Search for delete/remove handlers -- verify a confirmation dialog or modal precedes the action

**6.6 Transitions and Animations**
- Do modals/drawers/dropdowns animate in and out? (Not just appear/disappear)
- Are transitions short (150-300ms) and purposeful? (Not gratuitous or slow)
- Check for `transition` or `animation` CSS on interactive elements
- Flag abrupt state changes: tabs switching without transition, accordions without smooth open/close
- Tool: Grep CSS for `transition` and `animation` declarations

**6.7 Progressive Disclosure**
- Complex forms: are they broken into steps or sections rather than one long scroll?
- Advanced options: are they hidden behind "Advanced" or "More options" toggles?
- Flag forms with more than 8 visible fields that could benefit from grouping or progressive reveal
- Check that non-essential information is collapsible or on secondary views

**6.8 Undo and Reversibility**
- After a destructive or significant action, is there an undo option or at least a way to recover?
- Toast/snackbar notifications for completed actions should include an "Undo" link when possible
- Check that bulk operations (multi-select + delete) have extra safeguards beyond single-item operations

---

## Output Format

Present the audit results using this exact structure:

```
## UI Audit Report

### Scorecard

| # | Pillar | Score | Label |
|---|--------|-------|-------|
| 1 | Copywriting | X/4 | Excellent / Good / Needs Work / Poor |
| 2 | Visual Hierarchy | X/4 | Excellent / Good / Needs Work / Poor |
| 3 | Color | X/4 | Excellent / Good / Needs Work / Poor |
| 4 | Typography | X/4 | Excellent / Good / Needs Work / Poor |
| 5 | Spacing | X/4 | Excellent / Good / Needs Work / Poor |
| 6 | Experience Design | X/4 | Excellent / Good / Needs Work / Poor |
| | **Average** | **X.X/4** | **Grade: X** |

---

### Pillar 1: Copywriting -- X/4

**Findings:**
- CRITICAL: [specific finding with file path and line number]
- WARNING: [specific finding with file path and line number]
- NOTE: [specific finding with file path and line number]

**Recommendation:** [1-2 sentence summary of what to fix first]

---

### Pillar 2: Visual Hierarchy -- X/4

**Findings:**
- [findings...]

**Recommendation:** [...]

---

[Repeat for Pillars 3-6]

---

### Priority Fix List

#### Critical (fix before shipping)
1. [specific actionable fix with file path]
2. [...]

#### Warnings (fix soon)
1. [specific actionable fix with file path]
2. [...]

#### Notes (improve when possible)
1. [specific suggestion with file path]
2. [...]
```

## Rules

- Every finding MUST include a file path and line number (or component name if line number is impractical).
- Never give a score without justifying it with specific findings.
- A score of 4 (Excellent) still requires stating what was checked -- do not skip pillars with "looks fine."
- If a pillar cannot be evaluated (e.g., no CSS files exist), score it N/A and explain why.
- Findings must be actionable: "Button contrast is too low" is not actionable; "Change `.btn-primary` background from `#aaa` to `#2563eb` to meet 4.5:1 contrast on white (currently 2.8:1)" is actionable.
- Group related findings together rather than listing the same issue per-file.
- When running on a component library or design system, audit the tokens/primitives first, then spot-check composed views.
