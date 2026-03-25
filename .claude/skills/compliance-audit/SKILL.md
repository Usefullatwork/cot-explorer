---
name: compliance-audit
description: >
  Comprehensive GDPR, WCAG 2.1 AA, PCI-DSS, and API security compliance audit.
  Use when user says "compliance audit", "GDPR check", "accessibility audit",
  "WCAG check", "PCI compliance", or "security audit".
user-invocable: true
model: opus
effort: high
context: fork
argument-hint: "[scope: gdpr|wcag|pci|all]"
---

# Compliance Audit

Comprehensive compliance audit covering GDPR, WCAG, PCI-DSS, and API security.
Adapt checklists to the specific project tech stack and regulatory requirements.

## GDPR Audit Checklist

### Consent & Lawful Basis

- [ ] User consent mechanism exists for data processing
- [ ] Marketing consent is separate from service consent
- [ ] Cookie consent banner present (if cookies used)
- [ ] Privacy policy linked and accessible
- [ ] Lawful basis documented for each data processing activity

### Data Subject Rights

- [ ] **Right to access**: User can view all their data
- [ ] **Right to deletion**: Account deletion with cascade delete
- [ ] **Right to portability**: Data export in standard format (JSON/CSV)
- [ ] **Right to rectification**: User can update their profile data
- [ ] **Right to restriction**: User can restrict processing of their data

### Data Protection

- [ ] Passwords hashed with bcrypt (cost factor >= 10) or argon2
- [ ] PII encrypted at rest or masked in responses
- [ ] Data retention policy defined and enforced
- [ ] Breach notification process documented (72-hour requirement)
- [ ] Data processing agreements with third parties

## WCAG 2.1 AA Audit

### Perceivable

- [ ] `lang` attribute on `<html>` element
- [ ] Alt text on all meaningful images
- [ ] Labels on all form inputs
- [ ] Color contrast >= 4.5:1 for normal text, >= 3:1 for large text
- [ ] No information conveyed by color alone

### Operable

- [ ] All interactive elements keyboard accessible
- [ ] Skip navigation link present
- [ ] Focus visible on all interactive elements
- [ ] No keyboard traps
- [ ] Focus management in modals (trap + restore)

### Understandable

- [ ] Error messages are descriptive and helpful
- [ ] Form validation messages associated with inputs
- [ ] Consistent navigation across pages
- [ ] Language of page identified in HTML

### Robust

- [ ] ARIA roles, states, and properties correct
- [ ] Valid HTML (no duplicate IDs, proper nesting)
- [ ] Works in latest Chrome, Firefox, Safari, Edge

## PCI-DSS Awareness

- [ ] No credit card data stored in database
- [ ] Payment routes isolated in separate router
- [ ] Payment webhook signatures verified before processing
- [ ] Payment amounts not logged in plaintext
- [ ] HTTPS enforced for all payment endpoints (production)
- [ ] No payment tokens in URL parameters

## API Security

- [ ] Rate limiting on all public endpoints
- [ ] CORS configured (not `*` in production)
- [ ] Security headers enabled (Helmet or equivalent)
- [ ] Input sanitization against injection attacks
- [ ] Request body size limits
- [ ] JWT expiration enforced (short-lived access tokens)
- [ ] Refresh token rotation with replay detection

## Output

For each checklist item, report:

- **PASS**: Evidence of compliance (file:line or API response)
- **FAIL**: What is missing + fix recommendation + regulation reference
- **N/A**: Not applicable with justification

### Summary Table

| Category | Pass | Fail | N/A | Score |
|----------|------|------|-----|-------|
| GDPR | X | X | X | XX% |
| WCAG 2.1 AA | X | X | X | XX% |
| PCI-DSS | X | X | X | XX% |
| API Security | X | X | X | XX% |
| **Total** | X | X | X | **XX%** |