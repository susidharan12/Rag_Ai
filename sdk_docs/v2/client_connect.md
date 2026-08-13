---
page_id: v2-client-connect
sdk_version: v2
page_type: reference
---

# Client.connect()

`Client.connect()` opens a pooled connection to the Nimbus gateway.

## Parameters

| Name         | Type | Default | Required |
|--------------|------|---------|----------|
| endpoint     | str  | —       | yes      |
| api_key      | str  | —       | yes      |
| pool_size    | int  | 5       | no       |
| keepalive_ms | int  | 15000   | no       |

`pool_size` sets the maximum number of concurrent TCP connections held open
to the gateway.

## Example

```python
from nimbus import Client

client = Client.connect(
    endpoint="gateway.nimbus.example.com",
    api_key="sk_live_...",
)
```

## Notes

v2 is in maintenance mode. v3 doubles the default `pool_size` to `10`.
