---
name: visual-check
description: >
  Use when you need to visually verify changes to a web page, check responsive
  design, test a localhost dev server, or see what a rendered page looks like.
  Triggers: "check how it looks", "verify the page", "test the design",
  "screenshot", "visual regression", "does it render correctly".
allowed-tools: Bash(agent-browser:*), Read(*)
---

# Visual Verification Skill

Take screenshots of web pages and analyze them visually using Claude's multimodal capabilities.

## Quick Screenshot
1. Open URL: 2. Wait for load: 3. Screenshot: 4. Read and analyze: Use the Read tool on 
## Mobile Check
1. Set mobile viewport: 2. Screenshot: 3. Read and analyze the mobile screenshot

## Desktop Check
1. Set desktop viewport: 2. Screenshot: 3. Read and analyze

## Full Page Capture
1. Open URL: 2. Wait for load: 3. Full page screenshot: 4. Read and analyze

## Visual Analysis Checklist
When analyzing screenshots, check:
- Layout alignment and spacing
- Typography (size, weight, line-height)
- Colors (exact hex match against spec)
- Responsive behavior
- Image sizing and positioning
- CTA visibility and placement
- Accessibility contrast ratios
- No overlapping elements
- No horizontal scrollbar on mobile
- Text is readable (not truncated or overflowing)

## Comparison Workflow
To compare before/after changes:
1. Screenshot before: 2. Make changes
3. Reload: 4. Wait: 5. Screenshot after: 6. Read both screenshots and describe differences

## Common Viewport Sizes
| Device | Width | Height |
|--------|-------|--------|
| iPhone SE | 375 | 667 |
| iPhone 14 Pro | 393 | 852 |
| iPad | 768 | 1024 |
| Laptop | 1280 | 720 |
| Desktop | 1920 | 1080 |

## Gotchas (Windows)
- Use forward slashes in paths:  not - agent-browser daemon mode keeps browser open between commands
- Use  flag for labeled screenshots
-  flag captures entire page (slow for long pages)
- If agent-browser is unavailable, fall back to Playwright CLI:
  \