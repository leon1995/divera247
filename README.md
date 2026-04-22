# divera247

An async Python client for the [DIVERA 24/7](https://www.divera247.com/) REST API
and WebSocket push stream, built on [`httpx`](https://www.python-httpx.org/)
and [`pydantic`](https://docs.pydantic.dev/).

## Installation

```bash
pip install divera247
# or, with uv:
uv add 'divera247'
```

### Optional: WebSocket streaming

The push-event WebSocket subscription talks to `wss://ws.divera247.com/ws` via
[`httpx-ws`](https://pypi.org/project/httpx-ws/), which is kept out of the
default install for users who only need the REST API. Install it through the
`ws` extra:

```bash
pip install 'divera247[ws]'
# or, with uv:
uv add 'divera247[ws]'
```

## Quickstart

```python
import anyio
from divera247 import AccessKeyAuth, Divera247Client


async def main() -> None:
    async with Divera247Client(auth=AccessKeyAuth('YOUR_ACCESS_KEY')) as client:
        alarms = await client.alarm.get_alarms()
        for alarm in alarms.data or []:
            print(alarm)


anyio.run(main)
```

Every v2 endpoint group is exposed as a lazily-instantiated attribute on
`Divera247Client`:

| Attribute | Endpoint group |
| --- | --- |
| `client.alarm` | `/api/v2/alarms` |
| `client.attachment` | `/api/v2/attachments` |
| `client.auth_api` | `/api/v2/auth` |
| `client.dashboard` | `/api/v2/dashboard` |
| `client.event` | `/api/v2/events` |
| `client.file` | `/api/v2/file` |
| `client.message` | `/api/v2/messages` |
| `client.message_channel` | `/api/v2/message-channels` |
| `client.news` | `/api/v2/news` |
| `client.operations` | `/api/v2/operations` |
| `client.password` | `/api/v2/password` |
| `client.pull` | `/api/v2/pull` |
| `client.reporttype` | `/api/v2/reporttypes` |
| `client.shift_plans` | `/api/v2/shift-plans` |
| `client.statusgeber` | `/api/v2/statusgeber` |
| `client.using_vehicle` | `/api/v2/using-vehicles` |
| `client.using_vehicle_crew` | `/api/v2/using-vehicles/...` |
| `client.using_vehicle_property` | `/api/v2/using-vehicles/...` |

## Authentication

Three auth flows are provided in `divera247.auth`, all of which set the
`Authorization: Bearer <token>` header so the same credentials work for both
REST and WebSocket:

```python
from divera247 import AccessKeyAuth, JwtAuth, RefreshingJwtAuth

# Static access key (simplest; no token refresh).
AccessKeyAuth('YOUR_ACCESS_KEY')

# Pre-obtained JWT.
JwtAuth('eyJhbGciOi...')

# Access-key backed JWT that is fetched on first use and refreshed shortly
# before `exp`. Safe to share between concurrent tasks.
RefreshingJwtAuth('YOUR_ACCESS_KEY')
```

## Error handling

HTTP errors and envelope errors (`success: false`) are both funnelled through
the hierarchy in `divera247.errors`:

```python
from divera247 import (
    DiveraAPIError,
    DiveraAuthError,
    DiveraRateLimitError,
    DiveraValidationError,
)

try:
    await client.alarm.get_alarms()
except DiveraAuthError:
    ...                               # 401 / 403
except DiveraRateLimitError as exc:
    await anyio.sleep(exc.retry_after or 1)
except DiveraValidationError as exc:
    print(exc.errors)                 # field -> message mapping
except DiveraAPIError as exc:
    print(exc.status_code, exc.body)  # catch-all for other HTTP errors
```

Endpoints that return the standard `{"success": ..., "data": ...}` envelope
can be additionally guarded with `ensure_success(parsed)` when `success=false`
bodies should turn into exceptions.

## Customising the HTTP client

`Divera247Client` is deliberately a thin wrapper: its own constructor only
takes the `auth`, an optional `base_url`, and an optional pre-built
`session`. Anything you'd normally configure on an `httpx.AsyncClient` --
timeouts, headers (including `User-Agent`), proxies, transports, event hooks
-- is done by building your own client and passing it in via `session=`:

```python
import httpx

async with httpx.AsyncClient(
    auth=AccessKeyAuth('...'),
    base_url='https://app.divera247.com/api/',
    timeout=httpx.Timeout(60.0, connect=15.0),
    headers={'User-Agent': 'my-app/1.0', 'Accept-Language': 'de'},
    proxy='http://proxy.local:3128',
    verify=False,
) as external:
    client = Divera247Client(auth=AccessKeyAuth('...'), session=external)
    ...
```

When a `session=` is passed the caller keeps ownership: the session is
**not** closed when the client is exited.

## WebSocket streaming

Two entry points live in `divera247.websocket`:

- `subscribe_websocket(client, ...)` yields events from a single session and
  exits when the server disconnects. Use it when you want to drive your own
  reconnect policy.
- `stream_websocket(client, ...)` wraps `subscribe_websocket` in a jittered
  exponential-backoff reconnect loop. Use it when you want a "just keep me
  subscribed" iterator.

```python
from divera247.websocket import (
    ClusterPullEvent,
    UnknownEvent,
    UserStatusEvent,
    stream_websocket,
)

async for event in stream_websocket(client, ucr_id=527_459):
    match event:
        case UserStatusEvent(ucr=ucr, status=status):
            ...                                   # status is a PullStatusData
        case ClusterPullEvent(cluster=cluster, pull=pull):
            ...                                   # re-fetch pull.type (e.g. "alarm") + pull.id
        case UnknownEvent():
            ...                                   # forward-compatible fallback
```

`WebSocketAuthenticationError` propagates out of the loop so an unusable
credential doesn't get retried forever.

## API schemas

The `schemas/` directory contains the vendor-published OpenAPI YAML files
that this client was built against -- see [`schemas/README.md`](schemas/README.md)
for details and the mapping to `divera247.endpoints` / `divera247.models`.
