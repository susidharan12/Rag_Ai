---
page_id: v3-errors
sdk_version: v3
page_type: reference
---

# Error code reference

Every Nimbus API error response includes a machine-readable `code` field.
The table below lists every code the v3 SDK raises client-side or passes
through from the gateway.

## Codes

| Code | Name             | Retryable | Description                                   |
|------|------------------|-----------|------------------------------------------------|
| 400  | INVALID_ARGUMENT | no        | Request payload failed schema validation.       |
| 401  | UNAUTHENTICATED  | no        | Missing or invalid API key.                     |
| 403  | FORBIDDEN        | no        | API key lacks the required scope.               |
| 404  | NOT_FOUND        | no        | The requested resource does not exist.          |
| 409  | CONFLICT         | no        | Idempotency key reused with a different payload.|
| 429  | RATE_LIMITED     | yes       | Too many requests; honor `retry_backoff_ms`.    |
| 500  | INTERNAL         | yes       | Unexpected server error.                        |
| 503  | UNAVAILABLE      | yes       | Gateway is temporarily overloaded.              |

## Example

```python
from nimbus.errors import NimbusError

try:
    client.send(message="order.created")
except NimbusError as e:
    if e.code == "RATE_LIMITED":
        print("retryable:", e.retryable)
    else:
        raise
```

## Notes

Only `RATE_LIMITED`, `INTERNAL`, and `UNAVAILABLE` are retryable. The SDK's
built-in retry loop in `Client.send()` will not retry any other code.
