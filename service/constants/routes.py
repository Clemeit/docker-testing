import re

UNSECURED_ROUTES = [
    ("GET", r"^/health$"),
    ("GET", r"^/characters.*$"),
    ("GET", r"^/lfms.*$"),
    ("GET", r"^/servers.*$"),
    ("GET", r"^/game.*$"),
]
VERSION_PATTERN = re.compile(r"^/v\d+/")
