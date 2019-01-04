import asyncio
import re
import json

from socket import AF_INET
from aiohttp import web
from aiorcon import RCON
from jinja2 import Template, Environment

with open("response.j2","r") as f:
    t = f.read()
    template = Template(t, trim_blocks=True, lstrip_blocks=True,)

async def handler(request):
    if request.path == "/metrics":
        try:
            target  = request.query["target"]
            targets = target.split(":")
            ip = targets[0]
            port = targets[1]
            password = request.query["password"]
            # this first wait_for is to work around something which is maybe a bug in aiorcon
            rcon = await asyncio.wait_for(RCON.create(ip, port, password, loop = asyncio.get_event_loop(), timeout=1, auto_reconnect_attempts=2),2)
            status = await asyncio.wait_for(rcon("status"),2)
            stats = await asyncio.wait_for(rcon("stats"),2)
            rcon.close()

            server_dict = {"ip": ip, "port": port, "target": target}

            # parse status
            status = status.splitlines()
            for line in status:
                # break at the empty line between the key-value pairs and the players
                if line.strip() == "":
                    break

                key, value = (a.strip() for a in line.split(":",1))

                # special parsing for some keys:
                if key == "players":
                    m = re.match(
                            "(?P<players>\d+)\D+(?P<bots>\d+)\D+(?P<max_players>\d+)\\.*",
                            value)

                    if m is not None:
                        server_dict = { **server_dict, **m.groupdict()}
                if key == "hostname":
                    server_dict["hostname"] = value
                else:
                    pass
            # parse stats
            names, values, _ = [a.split() for a in stats.splitlines()]

            stats_mapping = [("In","NetIn"),
                    ("Out","NetOut"),
                    ("+-ms", "varms"),
                    ("~tick", "vartick"),
                    ("Svms", "svarms")]

            for i, name in enumerate(names):
                for key, replacement in stats_mapping:
                    if key == name:
                        names[i] = replacement
                        break

            values = [float(v) for v in values]
            stats_dict = dict(zip(names, values))

            server_dict = { **server_dict, **dict(zip(names, values))}
            return web.Response(text=template.render(**server_dict))

        except Exception as e:
            # TODO improve exception handling
            print(e)
            resp = """# HELP srcds_up is the gameserver reachable
# TYPE srcds_up gauge
srcds_up 0"""
            return web.Response(text=resp)
    return web.Response(text="invalid path", status=404)


async def start_webserver(loop, bind_address, port):
    server = web.Server(handler)

    await loop.create_server(server, bind_address, port)

async def main():
    loop = asyncio.get_event_loop()
    loop.create_task(start_webserver(loop, "localhost", 9200))

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(main())
    loop.run_forever()
