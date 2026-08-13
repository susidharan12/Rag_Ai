---
page_id: v3-auth
sdk_version: v3
page_type: reference
---

# TokenProvider.refresh()

`TokenProvider.refresh()` exchanges a long-lived refresh token for a new
short-lived access token. The SDK calls this automatically when a request
fails with `401 UNAUTHENTICATED`, but it can also be called directly.

## Parameters

| Name          | Type | Default   | Required |
|---------------|------|-----------|----------|
| refresh_token | str  | —         | yes      |
| scope         | str  | "default" | no       |
| force         | bool | False     | no       |

`scope` limits the permissions granted to the returned access token. Passing
`"default"` requests whatever scopes were originally granted to the
refresh token. `force=True` skips the SDK's in-memory token cache and always
performs a network call.

## Example

```python
from nimbus.auth import TokenProvider

provider = TokenProvider(client_id="...", client_secret="...")

token = provider.refresh(
    refresh_token="rt_abc123",
    scope="events:write",
)
```

## Notes

Access tokens returned by `refresh()` expire after 3600 seconds regardless
of the requested `scope`.
