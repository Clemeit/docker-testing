import requests
from requests import HTTPError
import xml.etree.ElementTree as ET
from client.redis import get_redis_client
from time import time

redis_client = (
    get_redis_client()
)  # For some reason, this seems to be a separate instance of the Redis client

DATA_CENTER_SERVER_URL = "http://gls.ddo.com/GLS.DataCenterServer/Service.asmx"
SOAP_ACTION = "http://www.turbine.com/SE/GLS/GetDatacenters"
CONTENT_TYPE = "text/xml; charset=utf-8"
BODY = '<?xml version="1.0" encoding="utf-8"?><soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema"><soap:Body><GetDatacenters xmlns="http://www.turbine.com/SE/GLS"><game>DDO</game></GetDatacenters></soap:Body></soap:Envelope>'


def query_worlds():
    """Query the data center server for the list of worlds."""
    worlds = []
    response = requests.post(
        DATA_CENTER_SERVER_URL,
        headers={"SOAPAction": SOAP_ACTION, "Content-Type": CONTENT_TYPE},
        data=BODY,
    )
    if response.status_code != 200:
        raise HTTPError(f"Failed to query data center server: {response.status_code}")
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
                    "world": name,
                    "status_server": status_server,
                    "order": order,
                }
            )
    return worlds


def update_worlds(worlds):
    """Query the status server for each world and update the server status."""
    server_status = {}
    for world in worlds:
        is_online = False
        response = requests.get(world["status_server"])
        if response.status_code != 200:
            raise HTTPError(
                f"Failed to query status server for {world['world']}: {response.status_code}"
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
        server_status[world["name"].lower()] = {
            "status": is_online,
            "index": world["order"],
        }
    return server_status


def update_server_status():
    try:
        worlds = query_worlds()
        server_status = update_worlds(worlds)
        print("Updating server status...")
        for server_name, info in server_status.items():
            redis_client.json().merge(
                name="server_info",
                path=server_name,
                obj={**info, "last_updated": time()},
            )
        print(redis_client.json().get("server_info"))  # TODO: remove
    except Exception as e:
        print(f"Failed to update server status: {e}")
