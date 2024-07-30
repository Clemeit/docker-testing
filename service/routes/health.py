from sanic import Blueprint
from sanic.response import json

from client.postgres import persist_characters_to_db

health_bp = Blueprint(name="HealthBlueprint", url_prefix="/health", version=1)


@health_bp.get("/")
async def health(_):
    persist_characters_to_db()
    return json(body={"message": "OK"}, status=200)
