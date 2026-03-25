---
name: i18n-parity
description: >
  Check i18n key parity between locale files. Reports missing keys,
  interpolation mismatches, plural gaps, and hardcoded strings. Use when user
  says "i18n parity", "locale check", "translation audit", "missing translations",
  or "i18n diff".
user-invocable: true
effort: medium
argument-hint: "[locale-pair]"
---

# i18n Parity Check

Audit all locale files for translation completeness and consistency.
Adapt locale paths to the specific project structure.

## Step 1: Load Locale Files

Read all JSON files from all locale directories. Typical structures:

- `src/i18n/locales/{lang}/*.json` (namespace-per-file)
- `src/locales/{lang}.json` (single-file)
- `public/locales/{lang}/*.json` (next-i18next style)

Identify the **primary language** (source of truth) and **secondary languages**.

## Step 2: Key Parity Diff

For each namespace, compare keys between primary and secondary locales:

- Keys present in primary but missing from secondary -> **MISSING_{LANG}**
- Keys present in secondary but missing from primary -> **EXTRA_{LANG}**
- Report count per namespace and list all missing keys

## Step 3: Interpolation Consistency

For keys present in both languages, compare `{{variable}}` placeholders:

- Extract all `{{...}}` tokens from each value
- Flag mismatches where one language has a placeholder the other does not
- Report as **INTERPOLATION_MISMATCH** with key, primary placeholders, secondary placeholders

## Step 4: Plural Form Check

For keys ending in `_one`, verify a matching `_other` exists (and vice versa):

- Check all locale files
- Report missing plural counterparts as **PLURAL_GAP**

## Step 5: Hardcoded String Scan

Scan recently modified `.tsx` / `.jsx` / `.vue` files for user-facing text not wrapped in `t()`:

- Check for string literals in JSX (between `>` and `<`)
- Ignore: HTML entities, empty strings, single characters, CSS classes, test IDs
- Report as **HARDCODED** with file, line, and the string found

## Output Format

```
=== i18n Parity Report ===

NAMESPACE: common
  MISSING_EN: 2 keys (common.greeting, common.farewell)
  MISSING_NB: 0 keys
  INTERPOLATION_MISMATCH: 1 (common.welcome: nb has {{name}}, en missing)

NAMESPACE: products
  OK -- all keys match

PLURAL_GAPS: 1
  - nb/common.json: item_one exists but item_other missing

HARDCODED: 3
  - src/pages/Dashboard.tsx:42 -- "Velkommen tilbake"

SUMMARY: 3 MISSING_EN | 0 MISSING_NB | 1 MISMATCH | 1 PLURAL_GAP | 3 HARDCODED
```