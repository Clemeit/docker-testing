import os

from client.redis import initialize_redis
from routes.characters import characters_bp
from routes.health import health_bp
from routes.lfms import lfms_bp
from routes.servers import servers_bp
from sanic import Sanic
from sanic.request import Request
from sanic.response import json
from utils.routes import is_route_unsecured

app = Sanic("ddo-audit")
app.blueprint([lfms_bp, characters_bp, servers_bp, health_bp])


API_KEY = os.getenv("API_KEY")


@app.listener("before_server_start")
async def setup_db(app, loop):
    initialize_redis()


@app.middleware("request")
async def check_api_key(request: Request):
    if is_route_unsecured(request):
        return
    api_key = request.headers.get("X-API-KEY")
    if not api_key or api_key != API_KEY:
        return json({"error": "Invalid API key"}, status=401)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, workers=1)
