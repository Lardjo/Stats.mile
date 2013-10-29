#!/usr/bin/env python3
import tornado.escape
import requests

from tornado import httpclient
from tornado.httputil import url_concat
from .base import BaseHandler
from bson import ObjectId


class MainHandler(BaseHandler):

    def get(self):

        settings = self.application.db['settings'].find_one({"apikey": {"$exists": 'true'}})

        if settings is None:
            try:
                errormessage = self.get_argument("error")
            except:
                errormessage = ""
            self.render("get.html", errormessage=errormessage)

        else:
            if self.get_current_user():
                self.render("index.html",
                            session=self.application.db["users"].find_one({"_id": ObjectId(self.current_user)}))
            else:
                self.render("index.html", session=None)

    def check_apikey(self, apikey):

        r = requests.get("https://api.steampowered.com/IDOTA2Match_570/GetMatchHistory/V001/?key={}".format(apikey))

        if r.status_code in (401, 500, 404):
            self.application.logger.fatal("Error! API invalid!")
            return False
        self.application.logger.info("API is valid! Ok")
        return True

    def post(self):

        apikey = self.get_argument('apikey', '')
        auth = self.check_apikey(apikey)

        if auth:
            settings = {"apikey": self.get_argument("apikey")}
            self.application.db["settings"].insert(settings)
            self.redirect("/")
        else:
            error_msg = "?error=" + tornado.escape.url_escape("Your Steam API key a invalid. Please, enter again")
            self.redirect("/" + error_msg)