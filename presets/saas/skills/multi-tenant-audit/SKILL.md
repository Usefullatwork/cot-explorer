---
name: multi-tenant-audit
description: >
  Audit multi-tenant SaaS applications for tenant isolation, data leakage,
  query scoping, and shared resource boundaries. Use when user says "tenant audit",
  "multi-tenant check", "isolation review", or "tenant security".
user-invocable: true
model: opus
effort: high
context: fork
argument-hint: "[scope: db|api|cache|all]"
---

# Multi-Tenant Isolation Audit

Audit a SaaS codebase for tenant isolation violations, cross-tenant data leakage risks, query scoping gaps, and shared resource boundary issues.

$ARGUMENTS

## Isolation Patterns -- Decision Framework

| Pattern | When to Use | Pros | Cons |
|---------|-------------|------|------|
| **Database-per-tenant** | Regulated industries, large enterprise tenants | Strongest isolation, easy backup/restore per tenant | High ops overhead, connection pool scaling |
| **Schema-per-tenant** | Medium tenants needing logical separation | Good isolation, shared infra | Schema migration complexity, connection routing |
| **Row-level (tenant_id)** | High tenant count, uniform data model | Simple ops, shared pool | Requires discipline in every query, index overhead |
| **Hybrid** | Mixed tenant tiers (free=shared, enterprise=dedicated) | Flexible per-tier SLA | Complex routing logic |

Choose the pattern that matches the codebase, then apply the corresponding audit checklist below.

## Scan Categories

### 1. Query Scoping Verification

Every database query touching tenant data MUST include a tenant_id filter. Scan for violations:

```bash
# SQL queries missing tenant_id in WHERE clause
grep -rn 'SELECT.*FROM' --include='*.js' --include='*.ts' --exclude-dir=node_modules --exclude-dir=dist . | grep -v 'tenant_id\|tenant_Id\|tenantId\|TENANT_ID'

# ORM queries without tenant scope
grep -rn '\.findMany\|\.findAll\|\.find({' --include='*.js' --include='*.ts' --exclude-dir=node_modules . | grep -v 'tenantId\|tenant_id\|where.*tenant'

# Raw queries (high risk -- no ORM protection)
grep -rn 'raw(\|rawQuery\|sequelize\.query\|\$queryRaw\|\.raw(' --include='*.js' --include='*.ts' --exclude-dir=node_modules .

# DELETE/UPDATE without tenant scope (critical)
grep -rn 'DELETE FROM\|UPDATE.*SET' --include='*.js' --include='*.ts' --exclude-dir=node_modules . | grep -v 'tenant_id\|tenantId'
```

Flag every result. DELETE and UPDATE without tenant scope are CRITICAL severity.

### 2. JOIN Operations -- Cross-Tenant Leak Risk

JOINs that do not scope both tables to the same tenant can leak data:

```bash
# JOIN statements (check both sides have tenant_id)
grep -rn 'JOIN.*ON' --include='*.js' --include='*.ts' --exclude-dir=node_modules .

# Subqueries (verify inner query is tenant-scoped)
grep -rn 'WHERE.*IN\s*(' --include='*.js' --include='*.ts' --exclude-dir=node_modules .
```

For each JOIN, verify:
- Left table is scoped to tenant_id
- Right table is scoped to the same tenant_id
- No implicit cross-tenant joins through shared lookup tables

### 3. API Endpoint Tenant Extraction

The tenant_id MUST come from the authenticated session/token, never from request params or body:

```bash
# Tenant ID from request params (VIOLATION)
grep -rn 'req\.params\.tenant\|req\.query\.tenant\|req\.body\.tenant' --include='*.js' --include='*.ts' --exclude-dir=node_modules .

# Tenant ID from headers (acceptable only if auth middleware validates)
grep -rn 'req\.headers.*tenant\|x-tenant' --include='*.js' --include='*.ts' --exclude-dir=node_modules .

# Correct: tenant from auth context
grep -rn 'req\.user\.tenant\|req\.auth\.tenant\|currentTenant\|getTenantId' --include='*.js' --include='*.ts' --exclude-dir=node_modules .
```

### 4. Shared Resource Boundary Checks

#### Cache Isolation

```bash
# Cache keys without tenant prefix (VIOLATION)
grep -rn 'redis\.get\|redis\.set\|cache\.get\|cache\.set\|\.getCache\|\.setCache' --include='*.js' --include='*.ts' --exclude-dir=node_modules .

# Verify all cache keys include tenant namespace
# Pattern: cache.set(`tenant:${tenantId}:resource:${id}`, ...)
```

For each cache operation, verify the key includes a tenant prefix. Shared cache without tenant namespacing is HIGH severity.

#### Queue Isolation

```bash
# Message queue operations
grep -rn 'publish\|subscribe\|enqueue\|addJob\|\.add(\|\.process(' --include='*.js' --include='*.ts' --exclude-dir=node_modules . | grep -i 'queue\|bull\|amqp\|rabbit\|sqs\|pubsub'

# Verify queue names or message payloads include tenant_id
```

#### File Storage Isolation

```bash
# File upload/storage paths
grep -rn 'upload\|putObject\|writeFile\|createWriteStream\|multer\|s3\.put' --include='*.js' --include='*.ts' --exclude-dir=node_modules .

# Storage paths must include tenant namespace: /{tenantId}/uploads/...
# Verify no shared bucket root access
```

### 5. Cross-Tenant Data Leak Detection Patterns

These patterns indicate potential cross-tenant data leakage:

```bash
# Global admin endpoints without tenant filter
grep -rn 'isAdmin\|role.*admin\|superadmin' --include='*.js' --include='*.ts' --exclude-dir=node_modules . | grep -v 'tenant'

# Aggregation queries across tenants
grep -rn 'GROUP BY\|aggregate\|COUNT(\|SUM(\|AVG(' --include='*.js' --include='*.ts' --exclude-dir=node_modules . | grep -v 'tenant'

# List endpoints without tenant filter
grep -rn '\.findMany\|\.findAll\|\.find({})\|SELECT.*FROM.*WHERE' --include='*.js' --include='*.ts' --exclude-dir=node_modules . | grep -v 'tenant'

# Data export/download endpoints
grep -rn 'export\|download\|csv\|xlsx\|report' --include='*.js' --include='*.ts' --exclude-dir=node_modules . | grep -iv 'import\|module\.export'
```

### 6. Database-Level Isolation (if applicable)

For schema-per-tenant or database-per-tenant architectures:

```bash
# Connection string construction (verify tenant routing)
grep -rn 'createConnection\|getConnection\|connectionString\|DATABASE_URL' --include='*.js' --include='*.ts' --exclude-dir=node_modules .

# Schema switching
grep -rn 'SET search_path\|USE.*database\|schema.*tenant' --include='*.js' --include='*.ts' --exclude-dir=node_modules .

# Connection pool per tenant
grep -rn 'createPool\|Pool(\|connectionPool' --include='*.js' --include='*.ts' --exclude-dir=node_modules .
```

## Severity Levels

- **CRITICAL**: Missing tenant_id on DELETE/UPDATE, tenant_id from user input, cross-tenant JOINs, shared cache without namespace
- **HIGH**: Missing tenant_id on SELECT, admin endpoints without tenant scope, file storage without tenant path, queue messages without tenant context
- **MEDIUM**: Aggregation queries across tenants, connection pool shared without tenant routing, missing tenant in audit logs
- **LOW**: Hardcoded tenant IDs in tests, tenant variable naming inconsistency

## Report Format

```
# Multi-Tenant Isolation Audit -- {date}

## Architecture
- Isolation pattern: [database-per-tenant | schema-per-tenant | row-level | hybrid]
- Tenant ID source: [auth token | middleware | request param (VIOLATION)]
- Total tenant-scoped tables: X
- Total endpoints audited: X

## Summary
| Severity | Count |
|----------|-------|
| CRITICAL | X |
| HIGH | X |
| MEDIUM | X |
| LOW | X |

## Findings

### [CRITICAL] Missing tenant_id on DELETE statement
  File: src/services/order.js:87
  Code: `DELETE FROM orders WHERE id = $1`
  Fix: Add `AND tenant_id = $2` to WHERE clause.
  Risk: Any tenant can delete another tenant's orders.

### [HIGH] Cache key without tenant namespace
  File: src/cache/product-cache.js:23
  Code: `cache.set(`product:${id}`, data)`
  Fix: `cache.set(`tenant:${tenantId}:product:${id}`, data)`
  Risk: Tenants may read each other's cached data.

## Checklist
- [ ] Every SELECT includes tenant_id in WHERE
- [ ] Every UPDATE includes tenant_id in WHERE
- [ ] Every DELETE includes tenant_id in WHERE
- [ ] All JOINs scope both tables to same tenant
- [ ] Tenant ID extracted from auth token, not request
- [ ] Cache keys prefixed with tenant identifier
- [ ] Queue messages include tenant context
- [ ] File storage paths include tenant namespace
- [ ] Admin endpoints require explicit tenant override
- [ ] Aggregation queries respect tenant boundaries
- [ ] Connection routing verified for multi-schema/multi-db
- [ ] Audit logs include tenant_id for every operation
```
