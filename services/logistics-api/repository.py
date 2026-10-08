import os
import time

import psycopg

DB = os.getenv('LOGISTICS_DB_URL', 'postgresql://logist:logist_demo@postgres:5432/logistics_db')


def connect():
    return psycopg.connect(DB)


def bootstrap():
    for _ in range(40):
        try:
            with connect() as database:
                database.execute(
                    "CREATE TABLE IF NOT EXISTS trucks("
                    "truck_id text primary key, route text, status text, stops_done int, "
                    "stops_total int, eta_min int, temp_c numeric, lat numeric, lon numeric)"
                )
                count = database.execute("SELECT count(*) FROM trucks").fetchone()[0]
                if count == 0:
                    with database.cursor() as cursor:
                        cursor.executemany(
                            "INSERT INTO trucks VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                            [
                                ('TRUCK-017', 'Quito Norte', 'IN_TRANSIT', 6, 11, 28, 3.8, -0.1807, -78.4678),
                                ('TRUCK-023', 'Quito Sur', 'LOADING', 0, 8, 64, 4.2, -0.245, -78.53),
                            ],
                        )
            return
        except Exception:
            time.sleep(1)


def list_trucks():
    with connect() as database:
        return database.execute("SELECT * FROM trucks ORDER BY truck_id").fetchall()


def advance_truck(truck_id):
    with connect() as database:
        return database.execute(
            "UPDATE trucks SET stops_done=LEAST(stops_total,stops_done+1), "
            "eta_min=GREATEST(0,eta_min-6), temp_c=temp_c+(random()-.5)/2 "
            "WHERE truck_id=%s RETURNING stops_done,eta_min,temp_c",
            (truck_id,),
        ).fetchone()