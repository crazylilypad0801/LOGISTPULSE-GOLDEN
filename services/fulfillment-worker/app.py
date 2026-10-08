import json
import os
import time

import psycopg
from kafka import KafkaConsumer, KafkaProducer

DB = os.getenv('FULFILLMENT_DB_URL', 'postgresql://logist:logist_demo@postgres:5432/fulfillment_db')
KAFKA = os.getenv('KAFKA_BOOTSTRAP', 'redpanda:9092')
TOPIC = 'logistpulse.orders'


def conn():
  return psycopg.connect(DB)


def publish_pending(producer):
  with conn() as database:
    events = database.execute(
      "SELECT event_id, payload FROM order_outbox "
      "WHERE published_at IS NULL ORDER BY created_at "
      "LIMIT 10 FOR UPDATE SKIP LOCKED"
    ).fetchall()
    for event_id, payload in events:
      producer.send(TOPIC, payload).get(timeout=10)
      database.execute(
        "UPDATE order_outbox SET published_at=%s WHERE event_id=%s",
        (time.time(), event_id),
      )


def process_order_event(event):
  event_id = event.get('eventId')
  order_id = event.get('orderId')
  if not event_id or not order_id:
    raise ValueError('Order event is missing eventId or orderId')

  with conn() as database:
    processed = database.execute(
      "SELECT 1 FROM processed_order_events WHERE event_id=%s", (event_id,)
    ).fetchone()
    if processed:
      return
    updated = database.execute(
      "UPDATE orders SET status='PREPARING',updated_at=%s "
      "WHERE order_id=%s AND status <> 'READY'",
      (time.time(), order_id),
    )
    if updated.rowcount == 0:
      exists = database.execute(
        "SELECT 1 FROM orders WHERE order_id=%s", (order_id,)
      ).fetchone()
      if not exists:
        raise ValueError(f'Order {order_id} does not exist')
      database.execute(
        "INSERT INTO processed_order_events(event_id,processed_at) VALUES (%s,%s) "
        "ON CONFLICT DO NOTHING",
        (event_id, time.time()),
      )
      return

  time.sleep(4)
  with conn() as database:
    database.execute(
      "UPDATE orders SET status='READY',updated_at=%s WHERE order_id=%s",
      (time.time(), order_id),
    )
    database.execute(
      "INSERT INTO processed_order_events(event_id,processed_at) VALUES (%s,%s) "
      "ON CONFLICT DO NOTHING",
      (event_id, time.time()),
    )


def run():
  while True:
    consumer = None
    producer = None
    try:
      consumer = KafkaConsumer(
        TOPIC,
        bootstrap_servers=KAFKA,
        group_id='kitchen-worker',
        auto_offset_reset='earliest',
        enable_auto_commit=False,
        value_deserializer=lambda value: json.loads(value.decode()),
      )
      producer = KafkaProducer(
        bootstrap_servers=KAFKA,
        value_serializer=lambda value: json.dumps(value).encode(),
      )
      while True:
        publish_pending(producer)
        for messages in consumer.poll(timeout_ms=1000, max_records=1).values():
          for message in messages:
            process_order_event(message.value)
            consumer.commit()
    except Exception as error:
      print(f'fulfillment worker retrying after error: {error}', flush=True)
      if consumer:
        consumer.close()
      if producer:
        producer.close()
      time.sleep(2)


run()
