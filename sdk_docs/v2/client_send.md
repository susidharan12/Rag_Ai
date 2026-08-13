---
page_id: v2-client-send
sdk_version: v2
page_type: reference
---

# Client.send()

`Client.send()` transmits a single message to the Nimbus event bus and waits
for the broker to acknowledge receipt.

## Parameters

| Name       | Type | Default | Required |
|------------|------|---------|----------|
| message    | str  | —       | yes      |
| retry_ms   | int  | 250     | no       |
| timeout_ms | int  | 15000   | no       |
| max_retries| int  | 3       | no       |

`retry_ms` is the fixed delay between retry attempts. Unlike v3, v2 does not
apply exponential backoff — every retry waits the same `retry_ms` interval.

## Example

```python
from nimbus import Client

client = Client(api_key="sk_live_...")

response = client.send(
    message="order.created",
    retry_ms=500,
    max_retries=5,
)
```

## Notes

v2 is in maintenance mode. New integrations should use the v3 SDK, which
renames `retry_ms` to `retry_backoff_ms` and adds exponential backoff.
