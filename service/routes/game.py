from time import time

from sanic import Blueprint
from sanic.request import Request
from sanic.response import json

from client.redis import get_redis_client
from constants.server import SERVER_NAMES_LOWER
from models.server import Server
from utils.validate_input import validate_server_info_key, validate_server_name

game_bp = Blueprint(name="GameBlueprint", url_prefix="/game", version=1)
redis_client = get_redis_client()


@game_bp.patch("/")
async def update_game_status(request: Request):
    """
    Updates the status of game in the game_info dictionary.
    """
    game: dict[str, dict] = request.json
    servers: dict[str, Server] = game.get("servers", {})
    for server, value in servers.items():
        if not validate_server_name(server):
            return json(body={"message": f"invalid server name '{server}'"}, status=400)
        redis_client.json().merge(
            name="game_info",
            path=f"servers.{server}",
            obj=value,
        )
    return json(body={"message": "server status updated"}, status=202)


@game_bp.get("/")
async def get_game_info(request: Request):
    """
    Fetches all server info for all servers from the game_info dictionary.
    Optionally filters the response by specific fields.
    """
    try:
        game_info = redis_client.json().get("game_info")
    except Exception as e:
        return json(
            body={"message": f"an error occurred while fetching data: {str(e)}"},
            status=500,
        )
    return json(body=game_info, status=200)


@game_bp.get("/<server>")
async def get_server_by_name(request: Request, server: str):
    """
    Fetches all server info for a specific server from the game_info dictionary.
    Optionally filters the response by specific fields.
    """
    if not validate_server_name(server):
        return json(body={"message": f"invalid server name '{server}'"}, status=400)
    try:
        value = redis_client.json().get("game_info", server)
        if value is None:
            return json(body={"message": "server info not found"}, status=404)
        args_fields_list = request.args.getlist("fields", [])
        if args_fields_list:
            value = {key: value[key] for key in args_fields_list if key in value}
    except Exception as e:
        return json(
            body={"message": f"an error occurred while fetching data: {str(e)}"},
            status=500,
        )
    return json(body=value, status=200)


@game_bp.get("/<server>/<key>")
async def get_value_by_server_and_key(request: Request, server: str, key: str):
    """
    Fetches a specific value for a specific server from the game_info dictionary.
    Optionally filters the response by specific fields.
    """
    if not validate_server_name(server):
        return json(body={"message": f"invalid server name '{server}'"}, status=400)
    if not validate_server_info_key(key):
        return json(body={"message": f"invalid server info key '{key}'"}, status=400)
    try:
        value = redis_client.json().get("game_info", f"{server}.{key}")
        if value:
            args_fields_list = request.args.getlist("fields", [])
            if args_fields_list:
                value = {key: value[key] for key in args_fields_list if key in value}
    except Exception as e:
        return json(
            body={"message": f"an error occurred while fetching data: {str(e)}"},
            status=500,
        )
    return json(body=value, status=200)
