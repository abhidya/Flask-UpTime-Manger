# Flask-UpTime-Manger
A uptime dashboard that manages, records and automates restarting python websites

## Archive status

This is a compact Flask uptime-manager prototype. It is preserved as an archive/demo and should be reviewed before use on any production service manager.

## Local run notes

- Review `websites.ini` before running so it points only to local or authorized apps.
- Expected third-party dependency: `requests`.
- Keep virtual environments, logs, and local `.env` files out of git.
- The default committed config points at localhost only. Use `UPTIME_CONFIG` or
  `--config` for private machine-specific targets.

## CLI demo

```sh
python3 main.py --config websites.ini --timeout 1 --workers 1 --json
```

Sample output when no local service is listening:

```json
[
  {
    "name": "local-demo",
    "url": "http://localhost:8000",
    "status_code": null,
    "reason": null,
    "elapsed_seconds": null,
    "error": "..."
  }
]
```
