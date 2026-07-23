# Cloud Scoreboard — Azure edition

Cloud-hosted replacement for the classroom scoreboard
([`sessions/04-wifi-iot/code/scoreboard_server.py`](../sessions/04-wifi-iot/code/scoreboard_server.py)).
Same JSON contract, so the boards switch hosts by changing **`SCOREBOARD_HOST`
alone** — and the stdlib server remains the offline/hotspot fallback.

Why cloud: school guest networks often block device-to-device traffic
(client isolation) while allowing outbound internet. Hosting the scoreboard
on Azure turns the risky board→laptop hop into a safe board→internet one.

## What's in the box

| Piece | Where | Serves |
|---|---|---|
| .NET 10 minimal API + SQLite | `Scoreboard.Api/` | `POST /result`, `GET /scores`, `GET /scores/{bench}`, keyed `GET /reset` |
| Scalar API docs | built from OpenAPI | `/scalar` |
| React leaderboard (Vite + TS) | `frontend/` → builds into `Scoreboard.Api/wwwroot/app/` | `/` (redirects to `/app/`) |
| Classic leaderboard page | `Scoreboard.Api/wwwroot/classic/` | `/classic/` (projector fallback) |

One app, one origin — no CORS anywhere. The contract (routes, JSON key
spellings, status codes) is verified byte-compatible against the stdlib
server, including the raw HTTP/1.0 `Connection: close` requests that
`async_http.py` sends. **If you change a route or shape, change the stdlib
server to match** — the two must stay interchangeable.

## Config

| Setting | Default | Notes |
|---|---|---|
| `SCOREBOARD_DB_PATH` | `scoreboard.db` in content root | On Azure set `/home/scoreboard.db` (writable + survives redeploys) |
| `RESET_KEY` | *(unset — reset disabled)* | `GET /reset?key=<value>` wipes scores |

## Run locally

```bash
# API on http://localhost:5080  (serves /scalar, /classic/, and /app/ if built)
cd Scoreboard.Api
dotnet run

# Frontend dev loop with hot reload (proxies /scores + /result to :5080)
cd frontend
npm install
npm run dev
```

## Deploy to Azure

```bash
az login

# 1) Build the React bundle into wwwroot/app
cd frontend && npm ci && npm run build && cd ..

# 2) Create + deploy (from the API project; re-run the same command to redeploy)
cd Scoreboard.Api
az webapp up \
  --name <globally-unique-name> \
  --resource-group rg-iot-scoreboard \
  --location <your-region> \
  --os-type Linux \
  --runtime "DOTNETCORE:10.0" \
  --sku B1

# 3) Allow plain HTTP (the boards' async client can't do TLS) + config.
#    HTTPS still works for browsers — this only stops the forced redirect.
az webapp update -g rg-iot-scoreboard -n <name> --set httpsOnly=false
az webapp config appsettings set -g rg-iot-scoreboard -n <name> \
  --settings RESET_KEY=<pick-a-secret> SCOREBOARD_DB_PATH=/home/scoreboard.db
```

SKU note: B1 (~$13/mo, delete the resource group after the course) is the
safe choice for class night. The F1 free tier works for testing but has a
daily CPU-minutes quota that a 3.5-hour class of polling boards could
plausibly exhaust mid-session.

### Verify after deploy (the decisive test)

```bash
# From any machine — mimic a board (plain http, port 80):
curl -s -X POST http://<name>.azurewebsites.net/result \
  -H "Content-Type: application/json" \
  -d '{"bench": "0", "player": "Blue", "result": "win"}'
curl -s http://<name>.azurewebsites.net/scores

# Then the real thing: a TinyPICO with
#   SCOREBOARD_HOST = "<name>.azurewebsites.net"
#   SCOREBOARD_PORT = 80
# running the Session 4 B2 POST snippet. This works from ANY network with
# internet (home included) — no need to be at the venue.

# Before class: wipe the test rows
curl -s "https://<name>.azurewebsites.net/reset?key=<secret>"
```

Projector: `https://<name>.azurewebsites.net/` (React) or `/classic/`
(fallback page). Docs to show the class: `/scalar`.

## Fallback ladder (class night)

1. **Azure** (primary) — needs outbound internet only; immune to client
   isolation.
2. **Local stdlib server on the phone hotspot** — no internet needed at all;
   announce the laptop's hotspot IP as `SCOREBOARD_HOST`, port 8000.
3. Any student laptop can run `scoreboard_server.py` if the instructor
   laptop dies.

Boards move between rungs by editing two values in `secrets.py`
(`SCOREBOARD_HOST`, `SCOREBOARD_PORT`). Nothing else changes.
