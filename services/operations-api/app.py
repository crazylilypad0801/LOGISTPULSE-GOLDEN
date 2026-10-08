from fastapi import FastAPI
import time

from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from fastapi import Request, Response
from routes import router
from telemetry import start_mqtt_consumer

REQ=Counter("logistpulse_http_requests_total","HTTP requests",["service","method","path","status"])
LAT=Histogram("logistpulse_http_request_duration_seconds","HTTP latency",["service","path"])

def instrument(app, service):
    @app.middleware("http")
    async def metrics(request: Request, call_next):
        started=time.time(); response=await call_next(request); elapsed=time.time()-started
        path=request.url.path
        REQ.labels(service,request.method,path,str(response.status_code)).inc()
        LAT.labels(service,path).observe(elapsed)
        return response
    @app.get("/metrics", include_in_schema=False)
    def metrics_endpoint():
        return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

app=FastAPI(title="LOGISTPULSE Smart Operations API",version="1.0.0")
instrument(app,"operations-api")
start_mqtt_consumer()
app.include_router(router)

@app.get('/health')
def health(): return {'status':'UP','service':'operations-api'}
