# Multi-Tenant Safety Rules

## Query Scoping
- Every database query MUST include tenant_id in the WHERE clause
- Never use admin/global queries without explicit authorization checks
- JOIN operations must scope both tables to the same tenant
- Raw SQL queries require mandatory code review for tenant scoping

## Boundary Validation
- API endpoints must extract tenant_id from auth token, not request params
- File storage paths must include tenant namespace
- Cache keys must be prefixed with tenant identifier
- Queue messages must carry tenant context in metadata

## Rate Limiting
- Per-tenant rate limits on all API endpoints
- Shared resource quotas (storage, compute, API calls) per tenant
- Alert thresholds for abnormal usage patterns

## Audit Logging
- Log all cross-tenant operations with justification
- Log admin access to tenant data with reason and duration
- Retain audit logs for compliance period (minimum 90 days)
