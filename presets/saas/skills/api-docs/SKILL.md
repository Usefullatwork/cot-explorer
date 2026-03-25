---
name: api-docs
description: Generate OpenAPI specs from code, validate existing specs against implementation, and generate client examples for API endpoints.
user-invocable: true
---

# API Documentation Skill

Generate, validate, and maintain API documentation by scanning route definitions, validation schemas, and controller implementations.

$ARGUMENTS

## Generation Workflow

### Step 1: Discover Routes

Scan for route registrations:

```bash
# Express routes
grep -rn 'router\.\(get\|post\|put\|patch\|delete\)(' --include='*.js' --include='*.ts' --exclude-dir=node_modules .

# App-level route mounting
grep -rn 'app\.use(' --include='*.js' --include='*.ts' --exclude-dir=node_modules . | grep -v 'middleware\|cors\|helmet\|morgan\|express\.\(json\|urlencoded\)'
```

### Step 2: Extract Validation Schemas

For each route, find the validation middleware:

```bash
# Zod schemas
grep -rn 'z\.object\|z\.string\|z\.number\|z\.array' --include='*.js' --include='*.ts' --exclude-dir=node_modules .

# express-validator
grep -rn 'body(\|param(\|query(' --include='*.js' --include='*.ts' --exclude-dir=node_modules . | grep -v 'req\.body\|req\.param\|req\.query'
```

### Step 3: Extract Response Shapes

Analyze controller functions for response patterns:

```bash
# JSON responses
grep -rn 'res\.json\|res\.status' --include='*.js' --include='*.ts' --exclude-dir=node_modules --exclude-dir=__tests__ .
```

### Step 4: Generate OpenAPI Spec

Produce a valid OpenAPI 3.0.3 specification with:

```yaml
openapi: 3.0.3
info:
  title: API Name
  version: 1.0.0
  description: Generated from source code analysis
  contact:
    name: API Support
servers:
  - url: http://localhost:3000/api
    description: Development
paths:
  /endpoint:
    get:
      summary: Short description
      operationId: uniqueOperationId
      tags: [Domain]
      security:
        - bearerAuth: []
      parameters: []
      responses:
        '200':
          description: Success
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ResponseType'
        '401':
          description: Unauthorized
        '404':
          description: Not found
components:
  securitySchemes:
    bearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT
  schemas:
    ErrorResponse:
      type: object
      properties:
        error:
          type: object
          properties:
            code:
              type: string
            message:
              type: string
```

### Step 5: Generate Client Examples

For each endpoint, generate examples in three formats:

**cURL:**
```bash
curl -X GET https://api.example.com/v1/resource \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json"
```

**TypeScript (Axios):**
```typescript
const response = await axios.get('/v1/resource', {
  headers: { Authorization: `Bearer ${token}` },
});
```

**Python (requests):**
```python
response = requests.get(
    'https://api.example.com/v1/resource',
    headers={'Authorization': f'Bearer {token}'}
)
```

## Validation Mode

When validating an existing spec against the codebase:

1. List all routes in code that are not in the spec (undocumented)
2. List all spec paths that do not exist in code (stale docs)
3. Compare request schemas: validation code vs spec definitions
4. Compare auth requirements: middleware vs spec security
5. Compare rate limits: limiter config vs spec descriptions

## Report Format

```
# API Documentation Report -- {date}

## Coverage
| Category | Documented | Total | Coverage |
|----------|-----------|-------|----------|
| Endpoints | X | Y | Z% |
| Request schemas | X | Y | Z% |
| Response schemas | X | Y | Z% |
| Auth documented | X | Y | Z% |

## Undocumented Endpoints
[path, method, handler file]

## Stale Documentation
[spec paths that no longer exist in code]

## Schema Mismatches
[endpoint, field, spec says X, code says Y]

## Generated Artifacts
- openapi.yaml -- Full OpenAPI 3.0.3 specification
- docs/api.md -- Human-readable API reference
- examples/ -- Client code examples per endpoint
```

## REST Convention Checks

When generating or validating, enforce:

- Plural nouns for resources: `/users`, `/orders` (not `/user`, `/order`)
- Consistent error format: `{ "error": { "code": "string", "message": "string" } }`
- HTTP methods match operations: GET=read, POST=create, PUT=replace, PATCH=update, DELETE=remove
- Standard status codes: 200, 201, 400, 401, 403, 404, 409, 422, 429, 500
- Pagination on list endpoints with consistent format
- Location header on 201 Created responses
