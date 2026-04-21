# Divera 24/7 API schemas

These YAML files are the OpenAPI specifications published by DIVERA 24/7 on
<https://api.divera247.com/> at the time each Python module below was written.
They are **not** used at runtime -- the Pydantic models under
`src/divera247/models/` and endpoint classes under
`src/divera247/endpoints/` are hand-written against these documents, so the
files here serve as:

1. Reference material for reviewers and contributors, and
2. The source of truth when regenerating or hand-updating the Python layer
   against a new vendor release.

## Mapping

Each YAML file maps to one module pair (`endpoints/<name>.py` +
`models/<name>.py`):

| Schema file | Python module |
| --- | --- |
| `api_v2_alarm.yaml` | `divera247.endpoints.alarm` / `divera247.models.alarm` |
| `api_v2_attachment.yaml` | `divera247.endpoints.attachment` / `divera247.models.attachment` |
| `api_v2_auth.yaml` | `divera247.endpoints.auth` / `divera247.models.auth` |
| `api_v2_dashboard.yaml` | `divera247.endpoints.dashboard` / `divera247.models.dashboard` |
| `api_v2_event.yaml` | `divera247.endpoints.event` / `divera247.models.event` |
| `api_v2_file.yaml` | `divera247.endpoints.file` / `divera247.models.file` |
| `api_v2_message.yaml` | `divera247.endpoints.message` / `divera247.models.message` |
| `api_v2_message-channel.yaml` | `divera247.endpoints.message_channel` / `divera247.models.message_channel` |
| `api_v2_news.yaml` | `divera247.endpoints.news` / `divera247.models.news` |
| `api_v2_operations.yaml` | `divera247.endpoints.operations` / `divera247.models.operations` |
| `api_v2_password.yaml` | `divera247.endpoints.password` / `divera247.models.password` |
| `api_v2_pull.yaml` | `divera247.endpoints.pull` / `divera247.models.pull` |
| `api_v2_reporttype.yaml` | `divera247.endpoints.reporttype` / `divera247.models.reporttype` |
| `api_v2_shift-plans.yaml` | `divera247.endpoints.shift_plans` / `divera247.models.shift_plans` |
| `api_v2_statusgeber.yaml` | `divera247.endpoints.statusgeber` / `divera247.models.statusgeber` |
| `api_v2_using-vehicle.yaml` | `divera247.endpoints.using_vehicle` / `divera247.models.using_vehicle` |
| `api_v2_using-vehicle-crew.yaml` | `divera247.endpoints.using_vehicle_crew` / `divera247.models.using_vehicle_crew` |
| `api_v2_using-vehicle-property.yaml` | `divera247.endpoints.using_vehicle_property` / `divera247.models.using_vehicle_property` |

The WebSocket protocol (`wss://ws.divera247.com/ws`) is not part of the
published OpenAPI documents; its event envelope and authentication handshake
are reverse-engineered in `divera247.websocket`.

## Documentation language

`Field(description=...)` strings mirror the German wording from the upstream
schemas so they round-trip into error messages and generated docs unchanged.
Docstrings, type annotations and tests are written in English; prefer English
for any new prose.
