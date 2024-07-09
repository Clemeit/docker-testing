import re

from constants.routes import UNSECURED_ROUTES, VERSION_PATTERN
from sanic.request import Request


def is_route_unsecured(request: Request) -> bool:
    stripped_path = VERSION_PATTERN.sub("/", request.path)
    for method, pattern in UNSECURED_ROUTES:
        if request.method == method and re.match(pattern, stripped_path):
            return True
    return False
