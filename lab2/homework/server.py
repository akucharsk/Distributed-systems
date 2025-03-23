import fastapi
import httpx
import os
from starlette.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import math
from urllib.parse import quote_plus
from threading import Lock

EARTH_RADIUS_KM = 6371
PIXABAY_API_KEY = os.environ.get('PIXABAY_API_KEY')

state = {"top_id": 0}
lock = Lock()

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


def united_shortened(string: str):
    if not string.lower().startswith("united"):
        return string
    return "".join(map(lambda s: s.capitalize()[0], string.split()))


def lon(longitude):
    if longitude < 0:
        return f"{-longitude}W"
    return f"{longitude}E"


def lat(latitude):
    if latitude < 0:
        return f"{-latitude}S"
    return f"{latitude}N"


def _make_batch_uri(query=""):
    return f"http://ip-api.com/batch?{quote_plus(query)}"


def _make_self_uri(query=""):
    return f"http://ip-api.com/json/?{quote_plus(query)}"


def _make_pixabay_uri(city: str, country: str = ''):
    country = "" if country == "" else "+" + quote_plus(country)
    return (f"https://pixabay.com/api/?key={PIXABAY_API_KEY}"
            f"&q={quote_plus(city)}{country}"
            f"&pretty=true")


@app.get("/")
async def root(request: fastapi.Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/api/batch")
async def batch(data: list[str]):
    timeout = httpx.Timeout(timeout=10.0, read=10.0, write=10.0)
    async with httpx.AsyncClient(timeout=timeout) as client:
        current_addr = await client.get(_make_self_uri())
        current_addr = current_addr.json()
        response = await client.post(_make_batch_uri(), json=data)

        resp = response.json()

    fails = [res for res in resp if res["status"] == 'fail']
    if fails:
        return fastapi.responses.JSONResponse(fails, 400)

    async with httpx.AsyncClient(timeout=timeout) as client:
        for location in resp:

            images = await client.get(_make_pixabay_uri(city=location['city']))
            images = images.json()
            location["images"] = [img["webformatURL"] for img in images["hits"][:5]]

    my_loc = current_addr["lat"], current_addr["lon"]
    for loc in resp:
        loc["distance"] = round(distance(*my_loc, loc["lat"], loc["lon"]), 2)
        loc["lon"] = lon(loc["lon"])
        loc["lat"] = lat(loc["lat"])
    resp.sort(key=lambda x: x["distance"])
    with lock:
        resp_id = state["top_id"]
        state[resp_id] = resp
        state["top_id"] += 1

    return fastapi.responses.JSONResponse({"id": resp_id, "resp": resp}, response.status_code)


@app.get("/result/{id}")
async def result(request: fastapi.Request, id: int):
    with lock:
        res = state.get(id)
    if res is None:
        return fastapi.responses.JSONResponse({"id": id, "message": "Not Found"}, status_code=404)
    return templates.TemplateResponse("result.html", {"request": request, "state": res})


@app.get("/result/json/{id}")
async def result(id: int):
    with lock:
        res = state.get(id)
    if res is None:
        return fastapi.responses.JSONResponse({"id": id, "message": "Not found"}, status_code=404)
    return fastapi.responses.JSONResponse({"id": id, "resp": res})


@app.delete("/result/{id}")
async def result(id: int):
    with lock:
        deleted = state.pop(id, None)
    if not deleted:
        return fastapi.responses.JSONResponse({"id": id, "message": "Result not found"}, status_code=404)
    return fastapi.responses.JSONResponse({"id": id, "message": "Deleted"}, status_code=200)
