---
page_id: v3-webhooks
sdk_version: v3
page_type: reference
---

# WebhookVerifier.verify()

`WebhookVerifier.verify()` checks the HMAC signature on an inbound webhook
delivery and rejects deliveries whose timestamp is too far in the past,
protecting against replay attacks.

## Parameters

| Name              | Type  | Default | Required |
|-------------------|-------|---------|----------|
| payload           | bytes | —       | yes      |
| signature         | str   | —       | yes      |
| timestamp         | int   | —       | yes      |
| tolerance_seconds | int   | 300     | no       |

`tolerance_seconds` sets how old a webhook's `timestamp` header is allowed
to be before `verify()` raises `WebhookExpiredError`. The default of `300`
(5 minutes) balances clock skew tolerance against replay-attack risk.

## Example

```python
from nimbus.webhooks import WebhookVerifier

verifier = WebhookVerifier(signing_secret="whsec_...")

is_valid = verifier.verify(
    payload=request.body,
    signature=request.headers["Nimbus-Signature"],
    timestamp=int(request.headers["Nimbus-Timestamp"]),
    tolerance_seconds=120,
)
```

## Notes

Raising `tolerance_seconds` above the default is discouraged in
production; it widens the window in which a captured request could be
replayed.
