---
name: onboarding-flow
description: >
  Audit and design SaaS onboarding flows including signup, trials, invitations,
  data seeding, and activation metrics. Use when user says "onboarding flow",
  "signup audit", "trial setup", "activation metrics", or "user journey".
user-invocable: true
effort: medium
argument-hint: "[scope: signup|trial|invite|all]"
---

# SaaS Onboarding Flow Audit

Audit and design onboarding flows for SaaS applications: signup, trial management, team invitations, data seeding, and activation metrics.

$ARGUMENTS

## Signup Flow Audit

### Email Verification

```bash
# Email verification implementation
grep -rn 'verify.*email\|email.*verify\|confirmation.*token\|verifyToken' --include='*.js' --include='*.ts' --exclude-dir=node_modules .

# Check for verification before granting access
grep -rn 'isVerified\|emailVerified\|verified.*true\|status.*active' --include='*.js' --include='*.ts' --exclude-dir=node_modules .
```

Verify:
- Verification email sent on signup (not optional)
- Token expiry set (recommended: 24 hours)
- Single-use tokens (invalidated after use)
- Re-send endpoint with rate limiting
- Account access restricted until verified

### Password Policy

```bash
# Password validation rules
grep -rn 'password.*length\|minLength\|password.*regex\|passwordPolicy\|zxcvbn\|password.*strength' --include='*.js' --include='*.ts' --exclude-dir=node_modules .

# Password hashing
grep -rn 'bcrypt\|argon2\|scrypt\|pbkdf2\|hashPassword' --include='*.js' --include='*.ts' --exclude-dir=node_modules .
```

Verify:
- Minimum 8 characters (NIST 800-63B recommends no max or composition rules)
- Password hashed with bcrypt (cost 12+), argon2id, or scrypt
- No plaintext password storage or logging
- Breach database check (HaveIBeenPwned API or similar)

### Rate Limiting on Signup

```bash
# Rate limiting middleware on auth routes
grep -rn 'rateLimit\|rateLimiter\|throttle' --include='*.js' --include='*.ts' --exclude-dir=node_modules . | grep -i 'auth\|signup\|register\|login'

# IP-based limiting
grep -rn 'req\.ip\|x-forwarded-for\|ipAddress.*limit' --include='*.js' --include='*.ts' --exclude-dir=node_modules .
```

Verify:
- Signup endpoint rate-limited (recommended: 5/hour per IP)
- Login endpoint rate-limited (recommended: 10/minute per IP, 100/hour per account)
- Account lockout after repeated failures (recommended: 5 attempts, 15-minute lockout)
- CAPTCHA or proof-of-work after threshold

## Trial Management Patterns

### Time-Based Trials

```bash
# Trial expiry logic
grep -rn 'trial.*expir\|trialEnd\|trial_ends_at\|trialDays\|FREE_TRIAL' --include='*.js' --include='*.ts' --exclude-dir=node_modules .

# Subscription status checks
grep -rn 'isTrialing\|subscription.*status\|plan.*type\|isTrial' --include='*.js' --include='*.ts' --exclude-dir=node_modules .
```

Checklist:
- [ ] Trial start date recorded on account creation
- [ ] Trial duration configurable (env var or admin setting)
- [ ] Grace period after trial expiry (recommended: 3-7 days)
- [ ] Data preserved after trial ends (not deleted)
- [ ] Clear UI indicators showing trial status and days remaining
- [ ] Automated email sequence: welcome, mid-trial, 3-day warning, expired

### Feature-Gated Trials

```bash
# Feature flag checks
grep -rn 'hasFeature\|featureEnabled\|canAccess\|isFeatureAvailable\|planIncludes\|checkEntitlement' --include='*.js' --include='*.ts' --exclude-dir=node_modules .

# Plan/tier definitions
grep -rn 'plans\|tiers\|features.*plan\|PLAN_\|FREE\|STARTER\|PRO\|ENTERPRISE' --include='*.js' --include='*.ts' --exclude-dir=node_modules .
```

Checklist:
- [ ] Feature matrix defined (which features per plan)
- [ ] Feature checks at both API and UI level
- [ ] Graceful degradation (show locked features with upgrade prompt, not errors)
- [ ] Feature usage tracked for conversion analysis

### Usage-Capped Trials

```bash
# Usage tracking / metering
grep -rn 'usage.*limit\|quota\|metering\|usageCount\|apiCalls.*limit\|rateLimit.*plan' --include='*.js' --include='*.ts' --exclude-dir=node_modules .
```

Checklist:
- [ ] Usage counters per resource type (API calls, storage, seats, records)
- [ ] Soft limits with warnings before hard cutoff
- [ ] Usage dashboard visible to user
- [ ] Reset period defined (monthly, per-billing-cycle)

## Team Invitation Flow

### Invite Mechanism

```bash
# Invitation logic
grep -rn 'invite\|invitation\|addMember\|teamMember\|joinTeam\|inviteCode' --include='*.js' --include='*.ts' --exclude-dir=node_modules .

# Role assignment on invite
grep -rn 'role.*invite\|invite.*role\|assignRole\|memberRole\|ROLE_\|owner\|admin\|member\|viewer' --include='*.js' --include='*.ts' --exclude-dir=node_modules .
```

Checklist:
- [ ] Invite tokens single-use and time-limited (72 hours recommended)
- [ ] Role assigned at invite time (not default admin)
- [ ] Inviter must have permission to invite (role check)
- [ ] Invited user sees team context on signup (not blank slate)
- [ ] Pending invites visible and revocable by team admin
- [ ] Rate limit on invite sends (prevent spam)

### Domain Verification

```bash
# Domain-based auto-join
grep -rn 'domain.*verify\|verifiedDomain\|allowedDomains\|emailDomain\|autoJoin' --include='*.js' --include='*.ts' --exclude-dir=node_modules .
```

Checklist:
- [ ] Domain verification via DNS TXT record or email to admin@domain
- [ ] Auto-join only for verified domains
- [ ] Domain verification revocable by team owner
- [ ] Users from verified domain get default role (not admin)

## Data Seeding Checklist

### Demo Data

```bash
# Seed/demo data logic
grep -rn 'seed\|demo.*data\|sampleData\|populateDemo\|createDemo\|onboarding.*data' --include='*.js' --include='*.ts' --exclude-dir=node_modules .
```

Verify:
- [ ] Demo data created for new tenants (not empty workspace)
- [ ] Demo data clearly labeled as sample (easy to distinguish and delete)
- [ ] Demo data covers primary use cases (shows value immediately)
- [ ] Bulk delete option for demo data when user is ready
- [ ] Demo data does not count toward usage quotas

### Default Settings

```bash
# Default configuration on tenant creation
grep -rn 'defaultSettings\|defaultConfig\|initialSettings\|setupDefaults\|tenantDefaults' --include='*.js' --include='*.ts' --exclude-dir=node_modules .
```

Verify:
- [ ] Sensible defaults set (timezone, locale, notification preferences)
- [ ] Settings discoverable in UI (not hidden in admin panel)
- [ ] Defaults documented for API consumers

### Onboarding Tours

```bash
# Product tour / onboarding UI
grep -rn 'tour\|onboarding.*step\|walkthrough\|tooltip.*guide\|shepherd\|intro\.js\|product-tour\|checklist.*onboard' --include='*.js' --include='*.ts' --include='*.tsx' --include='*.jsx' --exclude-dir=node_modules .
```

Verify:
- [ ] First-run experience guides user to primary action
- [ ] Tour dismissible and re-accessible from help menu
- [ ] Progress tracked (which steps completed)
- [ ] Tour adapted to user role (admin sees setup steps, member sees usage steps)

## Activation Metrics

### Time-to-Value (TTV)

Key metric: how long from signup to first meaningful action.

```bash
# Event tracking / analytics
grep -rn 'track(\|analytics\.\|mixpanel\|amplitude\|segment\.\|posthog\.\|event.*track' --include='*.js' --include='*.ts' --include='*.tsx' --exclude-dir=node_modules .

# Activation event definitions
grep -rn 'activation\|aha.*moment\|firstAction\|onboarded\|setupComplete' --include='*.js' --include='*.ts' --exclude-dir=node_modules .
```

Recommended activation events to track:
- Account created (timestamp baseline)
- Email verified
- First login after signup
- First meaningful action (domain-specific: first project created, first API call, first team member added)
- Setup wizard completed
- First integration connected

### Feature Adoption

Track which features users engage with during trial:

- Feature usage by plan tier
- Features correlated with conversion
- Features never used (candidates for onboarding emphasis)
- Time to first use of each core feature

### Conversion Triggers

```bash
# Upgrade / conversion logic
grep -rn 'upgrade\|convert\|subscribe\|checkout\|paywall\|billing.*create\|createSubscription' --include='*.js' --include='*.ts' --exclude-dir=node_modules .

# Conversion tracking
grep -rn 'trial.*convert\|conversion.*rate\|upgradeFrom\|planChange' --include='*.js' --include='*.ts' --exclude-dir=node_modules .
```

Recommended conversion analysis:
- Trial-to-paid conversion rate by signup source
- Feature usage patterns that predict conversion
- Time-in-trial before conversion (optimize trial length)
- Upgrade friction points (where users abandon checkout)

## Report Format

```
# Onboarding Flow Audit -- {date}

## Scope
- Signup flow: [audited | not found]
- Trial management: [time-based | feature-gated | usage-capped | none]
- Team invitations: [audited | not found]
- Data seeding: [audited | not found]
- Activation tracking: [audited | not found]

## Summary
| Area | Status | Issues |
|------|--------|--------|
| Email verification | PASS/FAIL | X issues |
| Password policy | PASS/FAIL | X issues |
| Rate limiting | PASS/FAIL | X issues |
| Trial management | PASS/FAIL | X issues |
| Invitations | PASS/FAIL | X issues |
| Data seeding | PASS/FAIL | X issues |
| Activation metrics | PASS/FAIL | X issues |

## Findings

### [HIGH] No rate limiting on signup endpoint
  File: src/routes/auth.js:15
  Code: `router.post('/signup', signupHandler)`
  Fix: Add rate-limiting middleware: `router.post('/signup', rateLimit({ max: 5, windowMs: 3600000 }), signupHandler)`
  Risk: Abuse, spam account creation, enumeration attacks.

## Recommendations
- [ ] Implement missing controls (listed above)
- [ ] Add activation event tracking for TTV measurement
- [ ] Set up conversion funnel dashboard
- [ ] Schedule A/B tests for onboarding flow improvements
```
