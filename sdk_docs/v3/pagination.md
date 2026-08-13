---
page_id: v3-pagination
sdk_version: v3
page_type: reference
---

# list_events() pagination

`list_events()` returns a page of events from the account's event log.
Pagination is cursor-based; each response includes a `next_cursor` field
that should be passed back in on the following call.

## Parameters

| Name    | Type | Default | Required |
|---------|------|---------|----------|
| cursor  | str  | None    | no       |
| limit   | int  | 50      | no       |
| order   | str  | "desc"  | no       |

`limit` accepts any integer from `1` to `200`. Requesting a `limit` above
`200` raises a `ValueError` client-side before the request is even sent;
the server itself would reject it with `400 INVALID_ARGUMENT`.

## Example

```python
page = client.list_events(limit=100, order="asc")

while page.next_cursor:
    page = client.list_events(cursor=page.next_cursor, limit=100, order="asc")
    for event in page.items:
        print(event.id, event.type)
```

## Notes

`order` may be `"asc"` or `"desc"`. Any other value raises
`ValueError("order must be 'asc' or 'desc'")`.
