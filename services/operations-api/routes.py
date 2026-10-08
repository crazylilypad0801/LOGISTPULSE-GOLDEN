from fastapi import APIRouter

import repository

router = APIRouter()


@router.get('/api/operations/{store_id}/devices')
def devices(store_id: str):
    results = repository.list_devices(store_id)
    for device in results:
        temperature = float(device.get('temperatureC', 0))
        device['state'] = 'CRITICAL' if temperature >= 8 else ('WARNING' if temperature >= 5 else 'OK')
    return results