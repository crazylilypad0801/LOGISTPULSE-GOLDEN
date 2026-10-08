#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${1:-http://localhost:8080}"

wait_for_http_200() {
    local url="$1"
    local http_code
    for attempt in {1..30}; do
        http_code=$(curl -s -o /dev/null -w "%{http_code}" "$url" || true)
        if [[ "$http_code" == "200" ]]; then
            return 0
        fi
        sleep 2
    done
    echo "ERROR - $url did not return HTTP 200 (last status: ${http_code:-no response})"
    return 1
}

echo "=========================================="
echo " LOGISTPULSE - Infrastructure Smoke Test"
echo "=========================================="
echo

echo "[1/7] Console"
curl -fsS "$BASE_URL/" | grep -q "LOGISTPULSE"
echo "OK - Console reachable"
echo

echo "[2/7] Inventory service"
wait_for_http_200 "$BASE_URL/health/inventory"
echo "OK - Inventory API reachable"
echo

echo "[3/7] Logistics service"
wait_for_http_200 "$BASE_URL/health/logistics"
echo "OK - Logistics API reachable"
echo

echo "[4/7] Operations service"
wait_for_http_200 "$BASE_URL/health/operations"
echo "OK - Operations API reachable"
echo

echo "[5/7] Fulfillment service"
wait_for_http_200 "$BASE_URL/health/fulfillment"
echo "OK - Fulfillment API reachable"
echo

echo "[6/7] Edge health routing"

for service in inventory logistics operations fulfillment; do
    wait_for_http_200 "$BASE_URL/health/$service"
    echo "OK - $service -> HTTP 200"
done

echo
echo "[7/7] Domain API routes through Nginx"
for route in \
    /api/inventory/STORE-042 \
    /api/distribution/trucks \
    /api/operations/STORE-042/devices \
    /api/fulfillment/orders; do
    wait_for_http_200 "$BASE_URL$route"
    RESPONSE=$(curl -fsS "$BASE_URL$route")
    python3 -c 'import json,sys; json.load(sys.stdin)' <<<"$RESPONSE"
    echo "OK - $route -> JSON"
done

echo
echo "=========================================="
echo " LOGISTPULSE INFRASTRUCTURE SMOKE PASSED"
echo "=========================================="
echo "Order-domain integration is checked separately by:"
echo "  bash scripts/smoke-orders.sh"
