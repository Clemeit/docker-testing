from time import time

from sanic.request import Request
from sanic.response import json

from client.redis import get_redis_client
from constants.server import SERVER_NAMES_LOWER
from models.server import Server
from utils.validate_input import validate_server_name

redis_client = get_redis_client()


async def set(request: Request, data_type: str):
    """
    Sets the character/lfm data for all servers in the character/lfm dictionary.
    """
    servers: dict[str, Server] = request.json
    for server, value in servers.items():
        if not validate_server_name(server):
            return json(body={"message": f"invalid server name '{server}'"}, status=400)
        data = value["data"]
        redis_client.json().set(
            name=f"{data_type}:{server}",
            path=f"{data_type}",
            obj={datum["id"]: datum for datum in data},
        )
        update_count_and_last_updated(server, data_type)
    return json(body={"message": f"{data_type} set"}, status=202)


async def update(request: Request, data_type: str):
    """
    Updates the character/lfm data for all servers in the character/lfm dictionary.
    This works by updating characters/lfms (those passed in by the "data" key)
    and removing newly lost characters/lfms (those passed in by the "removed" key).
    """
    servers: dict[str, Server] = request.json
    for server, value in servers.items():
        if not validate_server_name(server):
            return json(body={"message": f"invalid server name '{server}'"}, status=400)
        updated_data = value["data"]  # an array of full character/lfm dictionaries
        removed_data = value["removed"]  # an array of character/lfm ids
        if data_type == "characters":
            # TODO: all of the characters that are staged for removal need to first be added to database for long-term storage
            pass
        # use redis pipeline to update characters/lfms and remove the old ones
        with redis_client.pipeline() as pipe:
            if updated_data:
                pipe.json().merge(
                    name=f"{data_type}:{server}",
                    path=f"{data_type}",
                    obj={datum["id"]: datum for datum in updated_data},
                )
            for data_id in removed_data:
                pipe.json().delete(f"{data_type}:{server}", f"{data_type}.{data_id}")
            pipe.execute()
        update_count_and_last_updated(server, data_type)
    return json(body={"message": f"{data_type} updated"}, status=202)


async def get_by_server(request: Request, server: str, data_type: str):
    """
    Fetches all character/lfm info for a specific server from the character/lfm dictionary.
    Optionally filters the response by specific fields.
    """
    if not validate_server_name(server):
        return json(body={"message": f"invalid server name '{server}'"}, status=400)
    try:
        value = redis_client.json().get(f"{data_type}:{server}", ".")
        if value is None:
            return json(body={"message": f"{data_type} data not found"}, status=404)
        fields_list = request.args.getlist("fields", [])
        if fields_list:
            value = {key: value[key] for key in fields_list if key in value}
    except Exception as e:
        return json(
            body={"message": f"an error occurred while fetching data: {str(e)}"},
            status=500,
        )
    return json(body=value, status=200)


async def get_all(request: Request, data_type: str):
    """
    Fetches all character/lfm info for all servers from the character/lfm dictionary.
    Optionally filters the response by specific fields.
    """
    try:
        all_data = {}
        for server in SERVER_NAMES_LOWER:
            value = await get_by_server(request, server, data_type)
            value = value.raw_body
            if value is None:
                continue
            all_data[server] = value
    except Exception as e:
        return json(
            body={"message": f"an error occurred while fetching data: {str(e)}"},
            status=500,
        )
    return json(body=all_data, status=200)


def update_count_and_last_updated(server: str, data_type: str):
    """
    Updates the character/lfm count and last updated time for a specific server.
    """
    data_type_singular = data_type[:-1]
    data_count = redis_client.json().objlen(f"{data_type}:{server}", data_type)
    redis_client.json().merge(
        name=f"{data_type}:{server}",
        path=".",
        obj={f"{data_type_singular}_count": data_count, "last_updated": time()},
    )
    return data_count
