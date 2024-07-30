import os
from time import time

import redis

from constants.server import SERVER_NAMES_LOWER
from models.redis_cache import ServerCharacters, ServerInfo, ServerLFMs

REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = int(os.getenv("REDIS_PORT"))


class RedisSingleton:
    _instance = None
    client: redis.Redis

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            print("Creating Redis client...")
            cls._instance = super(RedisSingleton, cls).__new__(cls, *args, **kwargs)
            cls._instance.client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT)
            # cls._instance.initialize()
        return cls._instance

    def initialize(self):
        # Sets up the redis database with the server names as keys
        if self.client.dbsize() > 0:
            print("Redis database already initialized. Skipping...")
            return
        print("Initializing Redis database...")
        self.client.flushall()
        # server_info = {}
        for index, server in enumerate(SERVER_NAMES_LOWER):
            # info for every server is consolidated into a single dictionary
            # server_info[server] = ServerInfo(
            #     index=index,
            #     created=time(),
            # ).model_dump()

            # characters and lfms for every server are stored in separate dictionaries
            server_characters = ServerCharacters().model_dump()
            server_lfms = ServerLFMs().model_dump()
            self.client.json().set(
                f"characters:{server}", path="$", obj=server_characters
            )
            self.client.json().set(f"lfms:{server}", path="$", obj=server_lfms)

        self.client.json().merge("server_info", path="$", obj={})
        print(self.client.json().get("server_info"))  # TODO: remove

    def close(self):
        self.client.close()

    def get_client(self):
        return self.client


redis_singleton = RedisSingleton()


def get_redis_client():
    return redis_singleton.get_client()


def initialize_redis():
    redis_singleton.initialize()


def close_redis():
    redis_singleton.close()
