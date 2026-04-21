# divera247

This package provides an api client wrapper around the divera247 rest api and the websocket stream.

## Installation

```bash
pip install divera247
# or, with uv:
uv add 'divera247'
```

### Optional: WebSocket streaming

The push-event websocket subscription talks to `wss://ws.divera247.com/ws` via [`httpx-ws`](https://pypi.org/project/httpx-ws/), which is kept out of the default install for users who only need the REST API. Install it through the `ws` extra:

```bash
pip install 'divera247[ws]'
# or, with uv:
uv add 'divera247[ws]'
```
