from sanic import Blueprint
from sanic.request import Request

from routes.common.common_methods import get_all, get_by_server, set, update

lfms_bp = Blueprint(name="LfmBlueprint", url_prefix="/lfms", version=1)


@lfms_bp.post("/")
async def set_lfms(request: Request):
    """
    Sets the lfm data for all servers in the lfm dictionary.
    """
    return await set(request, "lfms")


@lfms_bp.patch("/")
async def update_lfms(request: Request):
    """
    Updates the lfm data for all servers in the lfm dictionary.
    This works by updating current lfms (those passed in by the "data" key)
    and removing newly removed lfms (those passed in by the "removed" key).
    """
    return await update(request, "lfms")


@lfms_bp.get("/")
async def get_all_lfms(request: Request):
    """
    Fetches all lfm info for all servers from the lfm dictionary.
    Optionally filters the response by specific fields.
    """
    return await get_all(request, "lfms")


@lfms_bp.get("/<server>")
async def get_lfms_by_server(request: Request, server: str):
    """
    Fetches all lfm info for a specific server from the lfm dictionary.
    Optionally filters the response by specific fields.
    """
    return await get_by_server(request, server, "lfms")
