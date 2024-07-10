import os

from sanic import Sanic
from sanic.request import Request
from sanic.response import json

from client.postgres import close_db_pool, create_db_pool
from client.redis import close_redis, initialize_redis
from routes.characters import characters_bp
from routes.health import health_bp
from routes.lfms import lfms_bp
from routes.servers import servers_bp
from utils.routes import is_route_unsecured

# Load environment variables
API_KEY = os.getenv("API_KEY")
APP_HOST = os.getenv("APP_HOST")
APP_PORT = int(os.getenv("APP_PORT"))
APP_WORKERS = int(os.getenv("APP_WORKERS") or 1)


# Set up Sanic app
app = Sanic("ddo-audit")
app.blueprint([lfms_bp, characters_bp, servers_bp, health_bp])


# Set up the redis and database connection
@app.listener("before_server_start")
async def set_up_connections(app, loop):
    """Set up the redis and database connection before the server starts."""
    initialize_redis()
    await create_db_pool(app)


# Tear down the database connection
@app.listener("after_server_stop")
async def close_connections(app, loop):
    """Close the redis and database connection after the server stops."""
    close_redis()
    await close_db_pool(app)


# Middleware to check API key for secured routes
@app.middleware("request")
async def check_api_key(request: Request):
    """Check the API key for secured routes."""
    if is_route_unsecured(request):
        return
    api_key = request.headers.get("X-API-KEY")
    if not api_key or api_key != API_KEY:
        return json({"error": "Invalid API key"}, status=401)


# Run the app
if __name__ == "__main__":
    app.run(host=APP_HOST, port=APP_PORT, workers=APP_WORKERS)
