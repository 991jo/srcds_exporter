import asyncio
import logging
import re
import argparse

from aiohttp import web
from aiorcon import RCON
from jinja2 import Template

# Logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# If possible, try to use uvloop for better performance
try:
    import uvloop
    uvloop.install()
    logger.info("Using uvloop")
except Exception:
    pass

# Statistic Mapper
STATS_MAPPING = {
    "In": "NetIn",
    "Out": "NetOut",
    "+-ms": "varms",
    "~tick": "vartick",
    "Svms": "svarms"
}

# if the server is running in single server mode the target specification
# has to be done via the commandline.
# requests with a target specification are answered with 404.
single_server_mode = False

# Parse response file
with open("response.j2", "r") as f:
    t = f.read()
    template = Template(t, trim_blocks=True, lstrip_blocks=True,)


async def rcon_query(ip, port, password):
    """
    queries the server given by ip and port with the stats and status commands
    and returns the answer
    """
    # this first wait_for is to work around something which is maybe
    # a bug in aiorcon
    rcon = await asyncio.wait_for(RCON.create(ip,
                                              port,
                                              password,
                                              # the loop is required due to a
                                              # bug in aiorcon. See
                                              # https://github.com/skmendez/aiorcon/pull/1
                                              loop=asyncio.get_event_loop(),
                                              timeout=1,
                                              auto_reconnect_attempts=2),
                                  2)

    status = await asyncio.wait_for(rcon("status"), 2)
    stats = await asyncio.wait_for(rcon("stats"), 2)
    rcon.close()
    return status, stats


async def handler(request):
    """
    Main handle function, receives prometheus requests and queries
    a game server
    """

    if request.path == "/metrics":
        try:
            target = request.query["target"]
            targets = target.split(":")
            ip = targets[0]
            port = targets[1]
            password = request.query["password"]
            print(ip, port, password)

            status, stats = await rcon_query(ip, port, password)

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

                key, value = (a.strip() for a in line.split(":", 1))

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
            lines = stats.splitlines()
            names = lines[0].split()
            values = lines[1].split()

            # Replace stats
            for i, name in enumerate(names):
                if name in STATS_MAPPING.keys():
                    names[i] = STATS_MAPPING[name]

            values = [float(v) for v in values]

            server_dict = {**server_dict, **dict(zip(names, values))}

            return web.Response(text=template.render(**server_dict))

        except Exception as e:
            # TODO improve exception handling
            logger.exception(e)
            resp = ("# HELP srcds_up is the gameserver reachable\n"
                    "# TYPE srcds_up gauge\n"
                    "srcds_up 0")

            return web.Response(text=resp)

    return web.Response(text="invalid path", status=404)


async def start_webserver(loop, bind_address, port):
    """ Startsup the server """
    server = web.Server(handler)

    await loop.create_server(server, bind_address, port)


if __name__ == "__main__":
    argparser = argparse.ArgumentParser(description=(
            "srcds_exporter, an prometheus exporter for SRCDS based games "
            "like CSGO, L4D2 and TF2"))
    argparser.add_argument("--port", type=int, default=9200,
                           help="the port to which the exporter binds")
    argparser.add_argument("--address", type=str, default="localhost",
                           help="the address to which the exporter binds")
    argparser.add_argument("--password", type=str, default=None,
                           help="the password that is used if the exporter "
                                "is run in single server mode")
    argparser.add_argument("--server_address", type=str, default="localhost",
                           help="the address which is queried if the is "
                                "exporter is run in single server mode")
    argparser.add_argument("--server_port", type=int, default=27015,
                           help="the queried which is queried if the is "
                                "exporter is run in single server mode")
    args = argparser.parse_args()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(start_webserver(loop, args.address, args.port))
    loop.run_forever()
