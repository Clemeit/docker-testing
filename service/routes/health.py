from sanic import Blueprint
from sanic.response import json

health_bp = Blueprint(name="HealthBlueprint", url_prefix="/health", version=1)


@health_bp.get("/")
async def health(_):
    return json(body={"message": "OK"}, status=200)
