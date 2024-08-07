import requests
from requests import HTTPError
import xml.etree.ElementTree as ET
from client.redis import get_redis_client
from time import time
from models.redis_cache import ServerInfo
from utils.scheduler import run_on_schedule


class ServerStatusUpdater:
    class Constants:
        DATA_CENTER_SERVER_URL = "http://gls.ddo.com/GLS.DataCenterServer/Service.asmx"
        SOAP_ACTION = "http://www.turbine.com/SE/GLS/GetDatacenters"
        CONTENT_TYPE = "text/xml; charset=utf-8"
        BODY = '<?xml version="1.0" encoding="utf-8"?><soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema"><soap:Body><GetDatacenters xmlns="http://www.turbine.com/SE/GLS"><game>DDO</game></GetDatacenters></soap:Body></soap:Envelope>'

    def __init__(self):
        self.redis_client = get_redis_client()
        self.previous_server_status = {}

    def query_worlds(self):
        """Query the data center server for the list of worlds."""
        worlds = []
        response = requests.post(
            self.Constants.DATA_CENTER_SERVER_URL,
            headers={
                "SOAPAction": self.Constants.SOAP_ACTION,
                "Content-Type": self.Constants.CONTENT_TYPE,
            },
            data=self.Constants.BODY,
        )
        if response.status_code != 200:
            raise HTTPError(
                f"Failed to query data center server: {response.status_code}"
            )
        response_text = response.text
        root = ET.fromstring(response_text)
        for datacenter in root.iter("{http://www.turbine.com/SE/GLS}Datacenter"):
            for world in datacenter.iter("{http://www.turbine.com/SE/GLS}World"):
                name = world.find("{http://www.turbine.com/SE/GLS}Name").text
                status_server = world.find(
                    "{http://www.turbine.com/SE/GLS}StatusServerUrl"
                ).text
                order = int(world.find("{http://www.turbine.com/SE/GLS}Order").text)
                worlds.append(
                    {
                        "name": name,
                        "status_server": status_server,
                        "order": order,
                    }
                )
        return worlds

    def update_worlds(self, worlds) -> dict[str, dict]:
        """Query the status server for each world and update the server status."""
        server_status: dict[str, dict] = {}
        for world in worlds:
            try:
                is_online = False
                response = requests.get(world["status_server"])
                if response.status_code != 200:
                    raise HTTPError(
                        f"Failed to query status server for {world['name']}: {response.status_code}"
                    )
                root = ET.fromstring(response.text)
                world["allow_billing_role"] = root.find("allow_billing_role").text
                world["world_full"] = root.find("world_full").text
                world["name"] = root.find("name").text
                if "Wayfinder" in world["name"]:
                    world["name"] = "Wayfinder"
                if (
                    "StormreachGuest" in world["allow_billing_role"]
                    or "StormreachStandard" in world["allow_billing_role"]
                    or "StormreachLimited" in world["allow_billing_role"]
                ):
                    is_online = True
                server_info = ServerInfo(
                    index=world["order"],
                    last_status_check=time(),
                    is_online=is_online,
                )
                model_dump = server_info.model_dump(exclude_none=True)
                server_status[world["name"].lower()] = model_dump
            except Exception:
                server_status[world["name"].lower()] = ServerInfo(
                    last_status_check=time(), is_online=False
                ).model_dump(exclude_none=True)
        return server_status

    def update_server_status(self):
        try:
            worlds = self.query_worlds()
            server_status = self.update_worlds(worlds)
            if not self.previous_server_status:
                previous_server_status = server_status
            for server in server_status:
                # Debounce the status:
                if (
                    server in previous_server_status
                    and server_status[server] != previous_server_status[server]
                ):
                    previous_server_status[server] = server_status[server]
                    print(f"Current status for {server} doesn't match previous status.")
                    continue
                self.redis_client.json().merge(
                    name="game_info",
                    path=f"servers.{server}",
                    obj=server_status[server],
                )
                previous_server_status[server] = server_status[server]
        except Exception as e:
            print(f"Failed to update server status: {e}")


def get_server_status_scheduler(interval: int = 60) -> tuple[callable, callable]:
    server_status_updater = ServerStatusUpdater()
    start_schedule, stop_schedule = run_on_schedule(
        server_status_updater.update_server_status, interval
    )
    return start_schedule, stop_schedule
