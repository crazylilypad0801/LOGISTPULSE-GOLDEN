#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${1:-http://localhost:8080}"
MAX_WAIT_SECONDS="${2:-90}"

echo "Creating an order through $BASE_URL..."
RAW_RESPONSE=$(curl -sS -w '\n%{http_code}' -X POST "$BASE_URL/api/fulfillment/orders" \
    -H 'Content-Type: application/json' \
    -d '{"storeId":"STORE-042","channel":"SMOKE","total":19.95}')
HTTP_CODE="${RAW_RESPONSE##*$'\n'}"
RESPONSE="${RAW_RESPONSE%$'\n'*}"
if [[ "$HTTP_CODE" != "201" ]]; then
    echo "ERROR - order create returned HTTP $HTTP_CODE: $RESPONSE"
    exit 1
fi

ORDER_ID=$(python3 -c 'import json,sys; print(json.load(sys.stdin)["orderId"])' <<<"$RESPONSE")
STATUS=$(python3 -c 'import json,sys; print(json.load(sys.stdin)["status"])' <<<"$RESPONSE")
EVENT_STATUS=$(python3 -c 'import json,sys; print(json.load(sys.stdin)["eventStatus"])' <<<"$RESPONSE")

if [[ "$STATUS" != "WAITING" || "$EVENT_STATUS" != "PENDING" || -z "$ORDER_ID" ]]; then
    echo "ERROR - unexpected create response: $RESPONSE"
    exit 1
fi

echo "Order $ORDER_ID created; waiting for the kitchen worker..."
DEADLINE=$((SECONDS + MAX_WAIT_SECONDS))
while (( SECONDS < DEADLINE )); do
    RESPONSE=$(curl -fsS "$BASE_URL/api/fulfillment/orders")
    STATUS=$(ORDER_ID="$ORDER_ID" python3 -c '
import json, os, sys
order_id = os.environ["ORDER_ID"]
orders = json.load(sys.stdin)
print(next((order["status"] for order in orders if order["orderId"] == order_id), "MISSING"))
' <<<"$RESPONSE")

    if [[ "$STATUS" == "READY" ]]; then
        echo "OK - order $ORDER_ID reached READY"
        exit 0
    fi
    if [[ "$STATUS" == "MISSING" ]]; then
        echo "ERROR - created order $ORDER_ID was not returned by the orders API"
        exit 1
    fi
    sleep 2
done

echo "ERROR - order $ORDER_ID did not reach READY within ${MAX_WAIT_SECONDS}s (last status: $STATUS)"
exit 1