#!/usr/bin/env python3
# steamstats\__init__.py

import os
import logging
import sys
import tornado.ioloop
import tornado.web

from pymongo import MongoClient
from . import classes
from . import config


class SteamStats(tornado.web.Application):
    """
    Class SteamStats
    Main, main and main
    """
    def __init__(self):
        """
        Init function
        Settings, handlers, connect to db
        """
        settings = {
            "cookie_secret": config.SECRET_KEY,
            "gzip": True,
            "debug": True,
            "login_url": "/auth/login",
            "template_path": os.path.join(os.path.dirname(__file__), "templates"),
            "static_path": os.path.join(os.path.dirname(__file__), "static"),
            }

        handlers = [
            ("/", classes.MainHandler),
            ("/auth/login", classes.AuthHandler),
            ("/auth/logout", classes.LogoutHandler),
            ("/about", classes.AboutHandler),
            ('/user/(.*)', classes.UserHandler),
            ('/search', classes.SearchHandler),
            ]

        try:
            client = MongoClient("localhost", 27017)
            self.db = client["users_stats"]
            logging.info("MongoDB is connected")
        except:
            logging.fatal("Database connection can\'t be established, terminating")
            sys.exit(1)

        super(SteamStats, self).__init__(handlers, **settings)
        self.listen(8888)
        logging.info("Steam Stats server is started")


class UpdateServer(tornado.web.Application):
    """
    Main update class
    """
    def __init__(self):
        """
        Connect to database and run update server
        """
        try:
            client = MongoClient("localhost", 27017)
            self.db = client["users_stats"]
            logging.info("MongoDB is connected")
        except:
            logging.fatal("Database connection can\'t be established, terminating")
            sys.exit(1)

        super(UpdateServer, self).__init__()
        self.scheduler = tornado.ioloop.PeriodicCallback(self.update, 60000 * 1)
        self.listen(8844)
        logging.info("Update Server is started")


    def update(self):
        """
        Get and update
        """
        logging.info("Periodic test is complete")
