# API Standards

## REST Conventions

### Resource Naming
- Use plural nouns for collections: `/users`, `/orders`, `/products`
- Use singular for singleton sub-resources: `/users/:id/profile`
- Use kebab-case for multi-word resources: `/order-items`, `/payment-methods`
- Nest related resources: `/users/:id/orders`, `/orders/:id/items`
- Maximum nesting depth: 2 levels (`/users/:id/orders/:orderId`)

### HTTP Methods
- `GET` -- Read a resource or list resources (safe, idempotent)
- `POST` -- Create a new resource (not idempotent)
- `PUT` -- Replace an entire resource (idempotent)
- `PATCH` -- Partial update of a resource (idempotent)
- `DELETE` -- Remove a resource (idempotent)

### Status Codes

| Code | Meaning | When to Use |
|------|---------|------------|
| 200 | OK | Successful GET, PUT, PATCH, DELETE |
| 201 | Created | Successful POST (include Location header) |
| 204 | No Content | Successful DELETE with no response body |
| 400 | Bad Request | Invalid request body, missing required fields |
| 401 | Unauthorized | Missing or invalid authentication token |
| 403 | Forbidden | Valid auth but insufficient permissions |
| 404 | Not Found | Resource does not exist |
| 409 | Conflict | Duplicate resource, version conflict |
| 422 | Unprocessable | Valid JSON but failed business rules |
| 429 | Too Many Requests | Rate limit exceeded (include Retry-After header) |
| 500 | Internal Error | Unexpected server error (never expose details) |

### Error Format

Consistent error response structure across all endpoints:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Email address is invalid",
    "details": [
      {
        "field": "email",
        "message": "Must be a valid email address",
        "value": "not-an-email"
      }
    ]
  }
}
```

Error codes should be machine-readable UPPER_SNAKE_CASE strings.
Error messages should be human-readable sentences.

## Authentication

### JWT with Refresh Tokens (Stateless Auth)
- Access token: short-lived (15-30 minutes), signed with RS256 or HS256
- Refresh token: longer-lived (7-30 days), opaque, stored server-side
- Token rotation: issue new refresh token on each refresh, invalidate old
- Replay detection: if a used refresh token is reused, revoke all user tokens
- Transport: `Authorization: Bearer <token>` header

### API Keys (Server-to-Server)
- Prefix with identifiable string: `sk_live_`, `sk_test_`
- Hash before storing (never store plaintext API keys)
- Support key rotation with grace period (old key valid for 24h after rotation)
- Scope keys to specific permissions (read-only, read-write, admin)
- Include key ID in header for fast lookup: `X-API-Key: <key>`

### OAuth 2.0 (Third-Party Integrations)
- Authorization Code flow for web applications
- PKCE extension for single-page apps and mobile
- Short-lived authorization codes (10 minutes max)
- Refresh tokens for long-lived access
- Scope-based permission model

### Rate Limiting
- Apply rate limits on all public endpoints
- Stricter limits on auth endpoints (prevent brute force)
- Include rate limit headers: `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`
- Return `429 Too Many Requests` with `Retry-After` header when exceeded
- Consider sliding window algorithm for smoother limiting

## Versioning

### URL Versioning
- Version in URL path: `/v1/users`, `/v2/users`
- Major version only (no minor/patch in URL)
- Support at most 2 major versions simultaneously

### Deprecation Process
1. Add `Deprecation` header with sunset date to deprecated endpoints
2. Add `Sunset` header with date when endpoint will be removed
3. Document migration path in changelog
4. Email API key holders 90 days before sunset
5. Return `410 Gone` after sunset date

### Changelog
- Document all breaking changes prominently
- Include migration guide for each breaking change
- Use semantic versioning for API versions
- Publish changelog at predictable URL: `/v1/changelog`

## Performance

### Pagination
- Cursor-based preferred for large datasets (consistent with concurrent writes)
- Offset-based acceptable for small, rarely-changing datasets
- Default page size: 20, maximum: 100
- Include pagination metadata in response:
  ```json
  {
    "data": [...],
    "pagination": {
      "cursor": "eyJpZCI6MTIzfQ==",
      "hasMore": true,
      "total": 1542
    }
  }
  ```

### Compression
- Enable gzip/brotli compression for responses over 1KB
- Set `Content-Encoding` header appropriately
- Accept `Accept-Encoding` from clients

### Caching
- `Cache-Control` headers on all GET endpoints
- Immutable data: `Cache-Control: public, max-age=31536000, immutable`
- User-specific data: `Cache-Control: private, no-cache`
- Sensitive data: `Cache-Control: no-store`
- Use `ETag` or `Last-Modified` for conditional requests

### Connection Efficiency
- Connection pooling for database queries
- Keep-Alive for persistent HTTP connections
- Batch endpoints for reducing round trips: `POST /batch`
- Consider GraphQL or field selection (`?fields=id,name,email`) for over-fetching

## Documentation

### Every Endpoint Must Document
- URL path with parameter types
- HTTP method
- Authentication requirement
- Request body schema (with required/optional fields)
- Query parameter options
- All possible response codes with example bodies
- Rate limit information
- At least one curl example

### OpenAPI/Swagger
- Maintain OpenAPI 3.0+ spec in `openapi.yaml`
- Auto-generate where possible, manually curate where needed
- Serve interactive docs at `/api-docs` (Swagger UI)
- Validate spec in CI pipeline
