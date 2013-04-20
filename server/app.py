# Start server
# All right reserved 2013

import tornado.ioloop

from tornado.options import define, parse_command_line
from steamstats import SteamStats

if __name__ == "__main__":

    define("mongo_host", default="mongodb://localhost:27017/")
    define("mongo_db", default="SteamStats")
    parse_command_line()
    app = SteamStats()

    tornado.ioloop.IOLoop.instance().start()