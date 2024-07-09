from time import time

from client.redis import get_redis_client
from constants.server import SERVER_NAMES_LOWER
from models.server import Server
from sanic import Blueprint
from sanic.request import Request
from sanic.response import json
from utils.validate_input import validate_server_info_key, validate_server_name

servers_bp = Blueprint(name="ServersBlueprint", url_prefix="/servers", version=1)
redis_client = get_redis_client()


@servers_bp.patch("/")
async def update_server_status(request: Request):
    """
    Updates the status of all servers in the server info dictionary.
    """
    servers: dict[str, Server] = request.json
    for server, value in servers.items():
        if not validate_server_name(server):
            return json(body={"message": f"invalid server name '{server}'"}, status=400)
        redis_client.json().merge(
            name="server_info",
            path=f"{server}",
            obj={**value, "last_updated": time()},
        )
    return json(body={"message": "server status updated"}, status=202)


@servers_bp.get("/")
async def get_all_servers(request: Request):
    """
    Fetches all server info for all servers from the server info dictionary.
    Optionally filters the response by specific fields.
    """
    try:
        all_servers = {}
        for server in SERVER_NAMES_LOWER:
            value = await get_server_by_name(request, server)
            value = value.raw_body
            all_servers[server] = value
    except Exception as e:
        return json(
            body={"message": f"an error occurred while fetching data: {str(e)}"},
            status=500,
        )
    return json(body=all_servers, status=200)


@servers_bp.get("/<server>")
async def get_server_by_name(request: Request, server: str):
    """
    Fetches all server info for a specific server from the server info dictionary.
    Optionally filters the response by specific fields.
    """
    if not validate_server_name(server):
        return json(body={"message": f"invalid server name '{server}'"}, status=400)
    try:
        value = redis_client.json().get("server_info", server)
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


@servers_bp.get("/<server>/<key>")
async def get_value_by_server_and_key(request: Request, server: str, key: str):
    """
    Fetches a specific value for a specific server from the server info dictionary.
    Optionally filters the response by specific fields.
    """
    if not validate_server_name(server):
        return json(body={"message": f"invalid server name '{server}'"}, status=400)
    if not validate_server_info_key(key):
        return json(body={"message": f"invalid server info key '{key}'"}, status=400)
    try:
        value = redis_client.json().get("server_info", f"{server}.{key}")
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
