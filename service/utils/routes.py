import re

from sanic.request import Request

from constants.routes import UNSECURED_ROUTES, VERSION_PATTERN


def is_route_unsecured(request: Request) -> bool:
    stripped_path = VERSION_PATTERN.sub("/", request.path)
    for method, pattern in UNSECURED_ROUTES:
        if request.method == method and re.match(pattern, stripped_path):
            return True
    return False
