import os
import time
import uuid

import psycopg
from psycopg.types.json import Jsonb

DB = os.getenv('FULFILLMENT_DB_URL', 'postgresql://logist:logist_demo@postgres:5432/fulfillment_db')


def connect():
    return psycopg.connect(DB)


def bootstrap():
    for _ in range(50):
        try:
            with connect() as database:
                database.execute(
                    "CREATE TABLE IF NOT EXISTS orders("
                    "order_id text primary key, store_id text, channel text, total numeric, "
                    "status text, created_at numeric, updated_at numeric)"
                )
                database.execute(
                    "CREATE TABLE IF NOT EXISTS order_outbox("
                    "event_id text primary key, order_id text not null references orders(order_id), "
                    "event_type text not null, payload jsonb not null, created_at numeric not null, "
                    "published_at numeric)"
                )
                database.execute(
                    "CREATE TABLE IF NOT EXISTS processed_order_events("
                    "event_id text primary key, processed_at numeric not null)"
                )
            return
        except Exception:
            time.sleep(1)


def list_orders():
    with connect() as database:
        rows = database.execute(
            "SELECT order_id,store_id,channel,total,status,created_at,updated_at "
            "FROM orders ORDER BY created_at DESC LIMIT 20"
        ).fetchall()
    return [
        {
            'orderId': row[0],
            'storeId': row[1],
            'channel': row[2],
            'total': float(row[3]),
            'status': row[4],
            'createdAt': row[5],
            'updatedAt': row[6],
        }
        for row in rows
    ]


def create_order(order):
    order_id = 'ORD-' + uuid.uuid4().hex[:6].upper()
    event_id = uuid.uuid4().hex
    now = time.time()
    event = {
        'eventId': event_id,
        'orderId': order_id,
        'event': 'ORDER_CREATED',
        'storeId': order.storeId,
    }
    with connect() as database:
        database.execute(
            "INSERT INTO orders VALUES (%s,%s,%s,%s,'WAITING',%s,%s)",
            (order_id, order.storeId, order.channel, order.total, now, now),
        )
        database.execute(
            "INSERT INTO order_outbox(event_id,order_id,event_type,payload,created_at) "
            "VALUES (%s,%s,'ORDER_CREATED',%s,%s)",
            (event_id, order_id, Jsonb(event), now),
        )
    return {'orderId': order_id, 'status': 'WAITING', 'eventStatus': 'PENDING'}