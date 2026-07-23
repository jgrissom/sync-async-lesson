#!/usr/bin/env bash
# ============================================================
# Deploy the cloud scoreboard to Azure App Service.
#
#   ./deploy.sh <globally-unique-app-name> [resource-group]
#
# First run creates everything (resource group, plan, app);
# re-running the same command redeploys. Overridable via env:
#   LOCATION  (default centralus)
#   SKU       (default F1, free — class night uses <10% of its daily
#             CPU/bandwidth quotas; escape hatch if ever needed:
#             az appservice plan update --sku B1, no redeploy)
#   RESET_KEY (default: keep existing app setting, else generate)
#
# The smoke test at the end is intentionally read-only, so a
# mid-course redeploy never touches live scores.
# ============================================================
set -euo pipefail

APP_NAME="${1:-${APP_NAME:-}}"
RG="${2:-${RESOURCE_GROUP:-rg-iot-scoreboard}}"
LOCATION="${LOCATION:-centralus}"
SKU="${SKU:-F1}"

if [[ -z "$APP_NAME" ]]; then
  echo "usage: ./deploy.sh <globally-unique-app-name> [resource-group]" >&2
  exit 1
fi

for tool in az npm dotnet curl; do
  command -v "$tool" >/dev/null || { echo "missing required tool: $tool" >&2; exit 1; }
done

cd "$(dirname "${BASH_SOURCE[0]}")"

az account show >/dev/null 2>&1 || az login

echo "==> Building React frontend into Scoreboard.Api/wwwroot/app"
(cd frontend && npm ci --silent && npm run build)

echo "==> Deploying $APP_NAME ($RG, $LOCATION, $SKU)"
(cd Scoreboard.Api && az webapp up \
    --name "$APP_NAME" \
    --resource-group "$RG" \
    --location "$LOCATION" \
    --os-type Linux \
    --runtime "DOTNETCORE:10.0" \
    --sku "$SKU") || {
  echo "Deploy failed. If the runtime was rejected, check available ones:" >&2
  echo "  az webapp list-runtimes --os linux | grep -i dotnet" >&2
  exit 1
}

echo "==> Allowing plain HTTP (boards can't do TLS; https still works for browsers)"
az webapp update -g "$RG" -n "$APP_NAME" --set httpsOnly=false --output none

if [[ -z "${RESET_KEY:-}" ]]; then
  RESET_KEY="$(az webapp config appsettings list -g "$RG" -n "$APP_NAME" \
      --query "[?name=='RESET_KEY'].value | [0]" -o tsv)"
  if [[ -n "$RESET_KEY" ]]; then
    echo "==> Keeping existing RESET_KEY"
  else
    RESET_KEY="$(openssl rand -hex 8)"
    echo "==> Generated RESET_KEY: $RESET_KEY   <-- save this"
  fi
fi

echo "==> App settings (SQLite in /home so it survives redeploys)"
az webapp config appsettings set -g "$RG" -n "$APP_NAME" \
    --settings RESET_KEY="$RESET_KEY" SCOREBOARD_DB_PATH=/home/scoreboard.db \
    --output none

HOST="$APP_NAME.azurewebsites.net"
echo "==> Smoke test (read-only; tolerates cold start)"
ok=""
for _ in $(seq 1 12); do
  if curl -sf --max-time 10 "http://$HOST/scores" >/dev/null 2>&1; then ok=1; break; fi
  sleep 5
done
if [[ -n "$ok" ]]; then
  echo "    plain-http GET /scores: OK"
  curl -s "http://$HOST/scores"; echo
else
  echo "    WARNING: http://$HOST/scores not answering yet — check" >&2
  echo "    az webapp log tail -g $RG -n $APP_NAME" >&2
fi

cat <<EOT

Deployed. URLs:
  Leaderboard : https://$HOST/          (projector; /classic/ is the fallback page)
  Scalar docs : https://$HOST/scalar
  Boards use  : SCOREBOARD_HOST = "$HOST"
                SCOREBOARD_PORT = 80

Next steps:
  1. Decisive test: TinyPICO on any Wi-Fi with the values above -> run the
     Session 4 B2 POST snippet -> row appears on the leaderboard.
  2. Before class, wipe test data (names are kept):
     curl "https://$HOST/reset?key=$RESET_KEY"
EOT
