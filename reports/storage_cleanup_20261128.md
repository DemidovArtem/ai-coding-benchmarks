# Verified ECC smoke cleanup — 28 November 2026

Only three stopped benchmark smoke containers were removed after native/configuration/memory archives and retained fixture verification. No images, volumes, bind-mounted fixtures, Sonar state or other projects were removed.

Observed Docker filesystem space recovered: **2,166,738,944 bytes** (approximately 2.17 GB). Concurrent host activity can affect the observed difference.

| Container | Native sessions preserved | Archive bytes | Removed |
| --- | ---: | ---: | --- |
| ecc-native_smoke_003 | 0 | 923 | Yes |
| ecc-native_smoke_004 | 2 | 443,733 | Yes |
| ecc-native-smoke | 0 | 638 | Yes |

The two empty native histories correspond to recorded setup failures before model execution: tracked-source verification and plugin registration. Their failure reports and retained fixtures remain available. The successful activation container retains its root/child native records, ECC state, configuration and closed SQLite backups. Archives omit authentication and reconstructible dependency/plugin caches.

Private archives and file manifests live under ignored `results/storage_cleanup/20261128/`. Each archive was read back and every regular-file hash matched the copied state. Closed SQLite passed integrity checks and contained the captured thread IDs. Host fixtures were hash-recorded; their Git repositories passed fsck where present. All three archives passed before any container was removed.

Use the [public receipt](storage_cleanup_20261128.json) to verify archive SHA-256, then inspect the private manifest and restore regular files with a safe tar data filter. Restore native stores from `closed_sqlite/`, retain fixture bind mounts, and use the pinned runtime/profile. This is preservation evidence, not a fresh native-session continuation test.

[ECC evidence audit](ecc_activation_audit.md) · [Live register](../EXPERIMENT_STATUS.md)
