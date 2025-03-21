import fastapi
import httpx
import os
import json
from starlette.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import math

EARTH_RADIUS_KM = 6371

state = []

app = fastapi.FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


def hsin(angle):
    return math.pow(math.sin(angle / 2), 2)


def distance(lat_1, lon_1, lat_2, lon_2):
    [lat_1, lon_1, lat_2, lon_2] = list(map(math.radians, [lat_1, lon_1, lat_2, lon_2]))
    d_lon = lon_2 - lon_1
    d_lat = lat_2 - lat_1
    print(d_lat, d_lon, lat_1, lat_2, lon_1, lon_2)
    return 2 * EARTH_RADIUS_KM * math.asin(math.sqrt(hsin(d_lat) + math.cos(lat_1) * math.cos(lat_2) * hsin(d_lon)))


def _make_batch_uri(query=""):
    return f"http://ip-api.com/batch?{query}"


def _make_self_uri(query=""):
    return f"http://ip-api.com/json/?{query}"


@app.get("/")
async def root():
    return fastapi.responses.FileResponse(os.path.join("static", "index.html"))


@app.post("/api/batch")
async def batch(request: fastapi.Request):
    data = await request.json()
    async with httpx.AsyncClient() as client:
        current_addr = await client.get(_make_self_uri())
        current_addr = current_addr.json()
        resp = await client.post(_make_batch_uri(), json=data)
        resp = resp.json()

    my_loc = current_addr["lat"], current_addr["lon"]
    for loc in resp:
        loc["distance"] = distance(*my_loc, loc["lat"], loc["lon"])
    resp = {"id": len(state), "resp": resp}
    state.append(resp)

    return resp


@app.get("/result/{id}")
async def result(request: fastapi.Request):
    state_id = int(request.path_params["id"])
    res = state[state_id]
    return templates.TemplateResponse("result.html", {"request": request, "state": res})
