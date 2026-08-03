#!/usr/bin/env bash
# Start the petition generator and print the address to share with volunteers.
#
#   ./run.sh              start it
#   ./run.sh --build      rebuild the frontend first (after editing frontend/src)
#   PORT=3000 ./run.sh    use a different port
#
# Keep the window open while it runs. Ctrl-C stops it.
set -euo pipefail

PORT="${PORT:-2026}"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

VENV="$ROOT/.venv/bin"
if [ ! -x "$VENV/uvicorn" ]; then
  echo "No virtualenv found at .venv/" >&2
  echo "Create one and install the backend dependencies:" >&2
  echo "  python3 -m venv .venv" >&2
  echo "  .venv/bin/pip install fastapi uvicorn python-docx pydantic pytest httpx" >&2
  exit 1
fi

# The backend serves the *built* frontend, so dist/ has to exist. Build it on
# first run, or whenever asked — backend edits reload on their own, the UI does not.
if [ ! -d frontend/dist ] || [ "${1:-}" = "--build" ]; then
  echo "Building the frontend…"
  [ -d frontend/node_modules ] || (cd frontend && npm install)
  (cd frontend && npm run build)
  echo
fi

if lsof -nP -iTCP:"$PORT" -sTCP:LISTEN >/dev/null 2>&1; then
  echo "Port $PORT is already in use — the server may already be running." >&2
  echo "Check http://localhost:$PORT, or stop the other process first." >&2
  exit 1
fi

# The .local name survives the router handing out a different IP; the raw
# address is the fallback for devices that cannot resolve it.
LAN_IP="$(ipconfig getifaddr en0 2>/dev/null || ipconfig getifaddr en1 2>/dev/null || true)"
HOST_NAME="$(scutil --get LocalHostName 2>/dev/null || true)"

echo
echo "  SIR-2026 petition generator"
echo "  ---------------------------"
echo "  This Mac          http://localhost:$PORT"
[ -n "$HOST_NAME" ] && echo "  Same wifi         http://$HOST_NAME.local:$PORT"
[ -n "$LAN_IP" ]    && echo "  Same wifi (IP)    http://$LAN_IP:$PORT"
echo
echo "  Anyone on this wifi can open those. Nothing leaves the network."
echo "  Keep this window open — Ctrl-C stops the server."
echo

cd backend
exec "$VENV/uvicorn" app.main:app --reload --host 0.0.0.0 --port "$PORT"
