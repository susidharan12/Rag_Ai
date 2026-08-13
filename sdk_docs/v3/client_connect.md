---
page_id: v3-client-connect
sdk_version: v3
page_type: reference
---

# Client.connect()

`Client.connect()` opens a pooled connection to the Nimbus gateway. Call
this once per process; the returned `Client` instance is thread-safe and
reuses connections from the pool for every subsequent `send()` call.

## Parameters

| Name          | Type | Default | Required |
|---------------|------|---------|----------|
| endpoint      | str  | —       | yes      |
| api_key       | str  | —       | yes      |
| pool_size     | int  | 10      | no       |
| keepalive_ms  | int  | 15000   | no       |
| tls           | bool | True    | no       |

`pool_size` sets the maximum number of concurrent TCP connections held open
to the gateway. In SDK v2 the default `pool_size` was `5`; v3 doubled it to
`10` after load testing showed the smaller pool bottlenecked high-throughput
producers.

## Example

```python
from nimbus import Client

client = Client.connect(
    endpoint="gateway.nimbus.example.com",
    api_key="sk_live_...",
    pool_size=20,
)
```

## Notes

`keepalive_ms` determines how long an idle connection is kept in the pool
before being closed. Lowering it reduces idle resource usage at the cost of
more frequent reconnects.
