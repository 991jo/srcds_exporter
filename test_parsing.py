import unittest
from main import SRCDSExporter

class TestParsing(unittest.TestCase):

    def setUp(self):
        self.exporter = SRCDSExporter()

    def test_csgo_status(self):
        data = ("hostname: LinuxGSM\n"
                "version : 1.36.8.7/13687 895/7436 secure  [G:1:2645045]\n"
                "udp/ip  : 172.16.0.17:27015  (public ip: 141.70.125.15)\n"
                "os      :  Linux\n"
                "type    :  community dedicated\n"
                "map     : de_mirage\n"
                "players : 0 humans, 0 bots (16/0 max) (hibernating)\n"
                "\n"
                "# userid name uniqueid connected ping loss state rate adr\n"
                "#end\n")

        server_dict = {}
        self.exporter._parse_status(data, server_dict)
        self.assertEqual(server_dict["hostname"], "LinuxGSM")
        self.assertEqual(server_dict["bots"], "0")
        self.assertEqual(server_dict["players"], "0")
        self.assertEqual(server_dict["max_players"], "16")

    def test_csgo_stats(self):
        data = ("  CPU   NetIn   NetOut    Uptime  Maps   FPS   Players  Svms    +-ms   ~tick\n"
                "  10.0      0.0      0.0   46732     1   64.07       0    5.31    0.08    0.03\n")
        server_dict = dict()
        self.exporter._parse_stats(data, server_dict)
        for key, value in {"CPU": 10, "NetIn": 0, "NetOut": 0, "Uptime": 46732,
                           "Maps": 1, "FPS": 64.07, "Players": 0, "svarms": 5.31,
                           "varms": 0.08, "vartick": 0.03}.items():
            self.assertEqual(server_dict[key], value)

    def test_fof_status(self):
        data = ("hostname: LinuxGSM\n"
                "version : 468/24 0 secure\n"
                "udp/ip  : 0.0.0.0:27015  (public ip: 141.70.124.33)\n"
                "steamid : [A:1:1510767623:12537] (90125840063167495)\n"
                "map     : fof_depot at: 0 x, 0 y, 0 z\n"
                "tags    : \n"
                "players : 0 humans, 0 bots (16 max)\n"
                "edicts  : 606 used of 2048 max\n"
                "# userid name                uniqueid            connected ping loss state  adr\n")

        server_dict = {}
        self.exporter._parse_status(data, server_dict)
        self.assertEqual(server_dict["hostname"], "LinuxGSM")
        self.assertEqual(server_dict["bots"], "0")
        self.assertEqual(server_dict["players"], "0")
        self.assertEqual(server_dict["max_players"], "16")

    def test_fof_stats(self):
        data = ("CPU    In_(KB/s)  Out_(KB/s)  Uptime  Map_changes  FPS      Players  Connects\n"
                "0.00   0.00       0.00        8       0            66.64    0        0\n")
        server_dict = dict()
        self.exporter._parse_stats(data, server_dict)
        for key, value in {"CPU": 0, "NetIn": 0, "NetOut": 0, "Uptime": 8,
                           "Maps": 0, "FPS": 66.64, "Players": 0, "Connects": 0}.items():
            self.assertEqual(server_dict[key], value)

    def test_hl2dm_status(self):
        data = ("hostname: LinuxGSM\n"
                "version : 4630212/24 4630212 insecure (secure mode enabled, disconnected from Steam3)\n"
                "udp/ip  : 0.0.0.0:27015\n"
                "steamid : not logged in\n"
                "map     : dm_lockdown at: 0 x, 0 y, 0 z\n"
                "tags    : alltalk,increased_maxplayers\n"
                "players : 0 humans, 0 bots (16 max)\n"
                "edicts  : 495 used of 2048 max\n"
                "# userid name                uniqueid            connected ping loss state  adr\n")
        server_dict = {}
        self.exporter._parse_status(data, server_dict)
        self.assertEqual(server_dict["hostname"], "LinuxGSM")
        self.assertEqual(server_dict["bots"], "0")
        self.assertEqual(server_dict["players"], "0")
        self.assertEqual(server_dict["max_players"], "16")

    def test_hl2dm_stats(self):
        data = ("CPU    In_(KB/s)  Out_(KB/s)  Uptime  Map_changes  FPS      Players  Connects\n"
                "0.00   0.00       0.00        0       0            66.70    0        0\n")
        server_dict = dict()
        self.exporter._parse_stats(data, server_dict)
        for key, value in {"CPU": 0, "NetIn": 0, "NetOut": 0, "Uptime": 0,
                           "Maps": 0, "FPS": 66.70, "Players": 0, "Connects": 0}.items():
            self.assertEqual(server_dict[key], value)

    def test_tf2_status(self):
        data = ("hostname: LinuxGSM\n"
                "version : 5063830/24 5063830 insecure (secure mode enabled, disconnected from Steam3)\n"
                "udp/ip  : 0.0.0.0:27015\n"
                "steamid : not logged in\n"
                "account : not logged in  (No account specified)\n"
                "map     : cp_badlands at: 0 x, 0 y, 0 z\n"
                "tags    : cp\n"
                "players : 0 humans, 0 bots (16 max)\n"
                "edicts  : 550 used of 2048 max\n"
                "# userid name                uniqueid            connected ping loss state  adr\n")
        server_dict = {}
        self.exporter._parse_status(data, server_dict)
        self.assertEqual(server_dict["hostname"], "LinuxGSM")
        self.assertEqual(server_dict["bots"], "0")
        self.assertEqual(server_dict["players"], "0")
        self.assertEqual(server_dict["max_players"], "16")

    def test_tf2_stats(self):
        data = ("CPU    In_(KB/s)  Out_(KB/s)  Uptime  Map_changes  FPS      Players  Connects\n"
                "0.00   0.00       0.00        0       0            66.67    0        0\n")
        server_dict = dict()
        self.exporter._parse_stats(data, server_dict)
        for key, value in {"CPU": 0, "NetIn": 0, "NetOut": 0, "Uptime": 0,
                           "Maps": 0, "FPS": 66.67, "Players": 0, "Connects": 0}.items():
            self.assertEqual(server_dict[key], value)

    def test_gmod_status(self):
        data = ("hostname: LinuxGSM\n"
                "version : 19.02.18/24 7472 insecure (secure mode enabled, disconnected from Steam3)\n"
                "udp/ip  : 192.0.2.1:27015\n"
                "map     : gm_construct at: 0 x, 0 y, 0 z\n"
                "players : 0 (16 max)\n"
                "\n"
                "# userid name                uniqueid            connected ping loss state  adr\n")
        server_dict = {}
        self.exporter._parse_status(data, server_dict)
        self.assertEqual(server_dict["hostname"], "LinuxGSM")
        self.assertEqual(server_dict["players"], "0")
        self.assertEqual(server_dict["max_players"], "16")

    def test_gmod_stats(self):
        data = ("CPU    In_(KB/s)  Out_(KB/s)  Uptime  Map_changes  FPS      Players  Connects\n"
                "33.00  0.00       0.00        1       0            66.07    0        0\n")
        server_dict = dict()
        self.exporter._parse_stats(data, server_dict)
        for key, value in {"CPU": 33, "NetIn": 0, "NetOut": 0, "Uptime": 1,
                           "Maps": 0, "FPS": 66.07, "Players": 0, "Connects": 0}.items():
            self.assertEqual(server_dict[key], value)

    def test_css_status(self):
        data = ("hostname: LinuxGSM\n"
                "version : 4630212/24 4630212 insecure (secure mode enabled, disconnected from Steam3)\n"
                "udp/ip  : 0.0.0.0:27015\n"
                "steamid : not logged in\n"
                "map     : de_dust2 at: 0 x, 0 y, 0 z\n"
                "tags    :\n"
                "players : 0 humans, 0 bots (16 max)\n"
                "edicts  : 212 used of 2048 max\n"
                "# userid name                uniqueid            connected ping loss state  adr\n")
        server_dict = {}
        self.exporter._parse_status(data, server_dict)
        self.assertEqual(server_dict["hostname"], "LinuxGSM")
        self.assertEqual(server_dict["players"], "0")
        self.assertEqual(server_dict["bots"], "0")
        self.assertEqual(server_dict["max_players"], "16")

    def test_css_stats(self):
        data = ("CPU    In_(KB/s)  Out_(KB/s)  Uptime  Map_changes  FPS      Players  Connects\n"
                "0.00   0.00       0.00        2       0            66.55    0        0\n")
        server_dict = dict()
        self.exporter._parse_stats(data, server_dict)
        for key, value in {"CPU": 0, "NetIn": 0, "NetOut": 0, "Uptime": 2,
                           "Maps": 0, "FPS": 66.55, "Players": 0, "Connects": 0}.items():
            self.assertEqual(server_dict[key], value)
