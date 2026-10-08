import os
import time

import psycopg

DB = os.getenv('INVENTORY_DB_URL', 'postgresql://logist:logist_demo@postgres:5432/inventory_db')


def connect():
    return psycopg.connect(DB)


def bootstrap():
    for _ in range(40):
        try:
            with connect() as database:
                database.execute(
                    "CREATE TABLE IF NOT EXISTS inventory("
                    "store_id text, sku text, item_name text, unit text, stock numeric, "
                    "forecast_4h numeric, PRIMARY KEY(store_id,sku))"
                )
                count = database.execute("SELECT count(*) FROM inventory").fetchone()[0]
                if count == 0:
                    with database.cursor() as cursor:
                        cursor.executemany(
                            "INSERT INTO inventory VALUES (%s,%s,%s,%s,%s,%s)",
                            [
                                ('STORE-042', 'CHK', 'Pollo', 'kg', 38, 61),
                                ('STORE-042', 'POT', 'Papas', 'kg', 74, 52),
                                ('STORE-042', 'OIL', 'Aceite', 'L', 21, 30),
                                ('STORE-042', 'PKG', 'Empaques', 'u', 425, 310),
                            ],
                        )
            return
        except Exception:
            time.sleep(1)


def list_inventory(store_id):
    with connect() as database:
        return database.execute(
            "SELECT sku,item_name,unit,stock,forecast_4h FROM inventory "
            "WHERE store_id=%s ORDER BY item_name",
            (store_id,),
        ).fetchall()


def adjust_stock(store_id, sku, delta):
    with connect() as database:
        return database.execute(
            "UPDATE inventory SET stock=stock+%s WHERE store_id=%s AND sku=%s "
            "RETURNING stock",
            (delta, store_id, sku),
        ).fetchone()