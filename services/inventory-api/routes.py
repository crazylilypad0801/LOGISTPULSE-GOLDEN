from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

import repository

router = APIRouter()


class Adjustment(BaseModel):
    delta: float


@router.get('/api/inventory/{store_id}')
def inventory(store_id: str):
    rows = repository.list_inventory(store_id)
    return [
        inventory_response(row)
        for row in rows
    ]


def inventory_response(row):
    stock = float(row[3])
    forecast = float(row[4])
    return {
        'sku': row[0],
        'item': row[1],
        'unit': row[2],
        'stock': stock,
        'forecast4h': forecast,
        'risk': 'HIGH' if stock < forecast * 0.75 else ('MEDIUM' if stock < forecast else 'LOW'),
    }


@router.post('/api/inventory/{store_id}/{sku}/adjust')
def adjust(store_id: str, sku: str, adjustment: Adjustment):
    row = repository.adjust_stock(store_id, sku, adjustment.delta)
    if not row:
        raise HTTPException(404, 'SKU not found')
    return {'storeId': store_id, 'sku': sku, 'stock': float(row[0])}