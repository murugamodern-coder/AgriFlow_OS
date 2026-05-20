# MinIO / S3 Lifecycle Policy (AgriFlow attachments)

Apply on the bucket used for Frappe `private/files` when MinIO is the object store.

## Recommended rules

| Prefix | Action | After |
|--------|--------|-------|
| `backups/` | Expire | 90 days |
| `temp/` | Expire | 7 days |
| `*` (default) | Transition to IA (if supported) | 180 days |

## Example (mc CLI)

```bash
mc ilm rule add myminio/agriflow-files --expire-days 90 --prefix "backups/"
```

## Cost control

- Enable versioning only on production buckets that require audit  
- Pair with weekly `bench backup` and Phase 24 retention on DB rows  
