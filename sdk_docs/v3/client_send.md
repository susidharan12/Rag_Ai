---
page_id: v3-client-send
sdk_version: v3
page_type: reference
---

# Client.send()

`Client.send()` transmits a single message to the Nimbus event bus and waits
for the broker to acknowledge receipt. In SDK v3 the method gained an
automatic retry loop with exponential backoff, replacing the fixed-delay
retry behavior from v2.

## Parameters

| Name              | Type   | Default | Required |
|-------------------|--------|---------|----------|
| message           | str    | —       | yes      |
| retry_backoff_ms  | int    | 500     | no       |
| timeout_ms        | int    | 30000   | no       |
| max_retries       | int    | 3       | no       |
| idempotency_key   | str    | None    | no       |

`retry_backoff_ms` controls the base delay between retry attempts. Each
subsequent retry doubles this value (exponential backoff) until
`max_retries` is exhausted. The default of `500` was chosen in v3 to reduce
thundering-herd retries against the broker under load; v2 used a fixed
`retry_ms` delay of `250` with no exponential growth.

## Example

```python
from nimbus import Client

client = Client(api_key="sk_live_...")

response = client.send(
    message="order.created",
    retry_backoff_ms=750,
    max_retries=5,
    idempotency_key="order-8842",
)

print(response.status)
```

## Notes

If the broker returns a `429 RATE_LIMITED` response, `Client.send()` will
honor `retry_backoff_ms` before retrying rather than failing immediately.
See the [error reference](./errors.md) for which codes are retryable.
