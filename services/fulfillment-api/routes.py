from fastapi import APIRouter
from pydantic import BaseModel

import repository

router = APIRouter()


class NewOrder(BaseModel):
    storeId: str = 'STORE-042'
    channel: str = 'MOBILE'
    total: float = 18.50


@router.get('/api/fulfillment/orders')
def orders():
    return repository.list_orders()


@router.post('/api/fulfillment/orders', status_code=201)
def create(order: NewOrder):
    return repository.create_order(order)