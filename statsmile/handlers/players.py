#!/usr/bin/env python3

from motor import Op

from tornado.gen import engine
from tornado.web import asynchronous

from statsmile.common.json_code import json_encode
from .base import BaseHandler

array = dict()


class PlayersHandler(BaseHandler):

    def prepare(self):
        super().prepare()
        self.set_header('Content-Type', 'application/json; charset=UTF-8')

    @asynchronous
    @engine
    def get(self):
        cursor = self.db.users.find({}, limit=10)
        array['players'] = yield Op(cursor.to_list)
        self.write(json_encode(array))
        self.finish()


class PlayerHandler(BaseHandler):

    def prepare(self):
        super().prepare()
        self.set_header('Content-Type', 'application/json; charset=UTF-8')

    @asynchronous
    @engine
    def get(self, user_id):
        array['player'] = yield Op(self.db.users.find_one, {'steam_id32': int(user_id)})
        if not array['player']:
            return self.send_error(404)
        self.write(json_encode(array))
        self.finish()