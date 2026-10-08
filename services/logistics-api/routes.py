from fastapi import APIRouter, HTTPException

import repository

router = APIRouter()


@router.get('/api/distribution/trucks')
def trucks():
    rows = repository.list_trucks()
    return [
        {
            'truckId': row[0],
            'route': row[1],
            'status': row[2],
            'stopsDone': row[3],
            'stopsTotal': row[4],
            'etaMin': row[5],
            'temperatureC': float(row[6]),
            'lat': float(row[7]),
            'lon': float(row[8]),
            'coldChain': 'OK' if row[6] <= 5 else 'ALERT',
        }
        for row in rows
    ]


@router.post('/api/distribution/trucks/{truck_id}/advance')
def advance(truck_id: str):
    row = repository.advance_truck(truck_id)
    if not row:
        raise HTTPException(404, 'Truck not found')
    return {'truckId': truck_id, 'stopsDone': row[0], 'etaMin': row[1], 'temperatureC': float(row[2])}