from routes.common.common_methods import get_all, get_by_server, set, update
from sanic import Blueprint
from sanic.request import Request

characters_bp = Blueprint(
    name="CharactersBlueprint", url_prefix="/characters", version=1
)


@characters_bp.post("/")
async def set_characters(request: Request):
    """
    Sets the character data for all servers in the character dictionary.
    """
    return await set(request, "characters")


@characters_bp.patch("/")
async def update_characters(request: Request):
    """
    Updates the character data for all servers in the character dictionary.
    This works by updating online characters (those passed in by the "data" key)
    and removing newly logged-out characters (those passed in by the "removed" key).
    """
    return await update(request, "characters")


@characters_bp.get("/<server>")
async def get_characters_by_server(request: Request, server: str):
    """
    Fetches all character info for a specific server from the character dictionary.
    Optionally filters the response by specific fields.
    """
    return await get_by_server(request, server, "characters")


@characters_bp.get("/")
async def get_all_characters(request: Request):
    """
    Fetches all character info for all servers from the character dictionary.
    Optionally filters the response by specific fields.
    """
    return await get_all(request, "characters")
