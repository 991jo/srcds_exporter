import asyncio
import re
import json
from loogging import getLogger

from socket import AF_INET
from aiohttp import web
from aiorcon import RCON
from jinja2 import Template, Environment

# Logger
logger = getLogger()


# Statistic Mapper
STATS_MAPPING = {
    "In": "NetIn",
    "Out": "NetOut",
    "+-ms": "varms",
    "~tick": "vartick",
    "Svms": "svarms"
}


# Parse response file
with open("response.j2","r") as f:
    t = f.read()
    template = Template(t, trim_blocks=True, lstrip_blocks=True,)


async def handler(request):
    """ Main handle function, receives prometheus requests and queries
    a game server """

    if request.path == "/metrics":
        try:
            target  = request.query["target"]
            targets = target.split(":")
            ip = targets[0]
            port = targets[1]
            password = request.query["password"]

            # this first wait_for is to work around something which is maybe
            # a bug in aiorcon
            rcon = await asyncio.wait_for(
                RCON.create(
                    ip,
                    port,
                    password,
                    timeout=1,
                    auto_reconnect_attempts=2
                ),
                2
            )

            status = await asyncio.wait_for(rcon("status"), 2)
            stats = await asyncio.wait_for(rcon("stats"), 2)
            rcon.close()

            server_dict = {
                "ip": ip,
                "port": port,
                "target": target
            }

            # parse status
            status = status.splitlines()
            for line in status:
                # break at the empty line between the key-value pairs and the
                # players
                if line.strip() == "":
                    break

                key, value = (a.strip() for a in line.split(":",1))

                # Switch case for some keys

                if key == "players":  # Players
                    m = re.match(
                        "(?P<players>\d+)\D+(?P<bots>\d+)\D+(?P<max_players>\d+)\\.*",
                        value
                    )

                    if m:
                        server_dict = {**server_dict, **m.groupdict()}

                elif key == "hostname":  # Hostname
                    server_dict["hostname"] = value

                else:
                    pass

            # parse stats
            names, values, _ = [a.split() for a in stats.splitlines()]

            # Replace stats
            for i, name in enumerate(names):
                if name in STATS_MAPPING.keys():
                    names[i] = STATS_MAPPING[name]

            values = [float(v) for v in values]
            stats_dict = dict(zip(names, values))

            server_dict = {**server_dict, **dict(zip(names, values))}

            return web.Response(text=template.render(**server_dict))

        except Exception as e:
            # TODO improve exception handling
            logger.error(e)
            resp = "# HELP srcds_up is the gameserver reachable" + \
                   "# TYPE srcds_up gauge" + \
                   "srcds_up 0"

            return web.Response(text=resp)

    return web.Response(text="invalid path", status=404)


async def start_webserver(loop, bind_address, port):
    """ Startsup the server """
    server = web.Server(handler)

    await loop.create_server(server, bind_address, port)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(start_webserver(loop, "localhost", 9200))
    loop.run_forever()
