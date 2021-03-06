#!/usr/bin/env python3

import math

from motor import Op
from tornado.gen import engine
from tornado.web import asynchronous
from .base import BaseHandler
from bson import ObjectId
from statsmile.common import libs


class UserHandler(BaseHandler):
    @asynchronous
    @engine
    def get(self, sid):

        black_list = [7, 9, 15]

        session = None

        if self.current_user:
            session = yield Op(self.db['users'].find_one, {'_id': self.current_user['userid']})

        user = yield Op(self.db['users'].find_one, {'_id': ObjectId(sid)})

        if user is None:
            return self.send_error(404)

        matches, match = yield [
            Op(self.db['matches'].find({"players.account_id": user["steamid32"], "game_mode": {"$nin": black_list},
                                        'players.hero_id': {'$nin': [0]}},
                                       {"radiant_win": 1, "cluster": 1, "duration": 1, "start_time": 1, "game_mode": 1,
                                        "lobby_type": 1, "match_id": 1,
                                        "players": {"$elemMatch": {"account_id": user["steamid32"]}}},
                                       sort=[('start_time', -1)], limit=10).to_list),
            Op(self.db['matches'].find({"players.account_id": user["steamid32"],
                                        "game_mode": {"$nin": black_list}, 'players.hero_id': {'$nin': [0]}},
                                       sort=[('start_time', -1)], limit=1).to_list)]

        self.render("user.html", title="Dashboard", user=user, session=session, matches=matches,
                    match=match, heroes=libs.heroes, cluster=libs.cluster, mode=libs.mode)


class UserMatchesHandler(BaseHandler):
    @asynchronous
    @engine
    def get(self, sid):

        black_list = [7, 9, 15]

        pg = int(self.get_argument('page', 1))
        hero = self.get_argument('hero', 'all')

        if hero == 'all':
            pass
        else:
            if not int(hero) in libs.heroes.keys():
                return self.send_error(404)

        session = None

        if self.current_user:
            session = yield Op(self.db['users'].find_one, {'_id': self.current_user['userid']})

        user = yield Op(self.db['users'].find_one, {'_id': ObjectId(sid)})

        if user is None:
            return self.send_error(404)

        pages = yield Op(self.db["matches"].find({"players.account_id": user['steamid32'],
                                                  "game_mode": {"$nin": black_list},
                                                  'players.hero_id': {'$nin': [0]}}).count)
        max_pages = math.ceil(pages / 20)

        if pg > max_pages:
            return self.send_error(404)

        if hero == 'all':
            matches = yield Op(self.db["matches"].find(
                {"players.account_id": user["steamid32"], "game_mode": {"$nin": black_list},
                 'players.hero_id': {'$nin': [0]}},
                {"game_mode": 1, "start_time": 1, "duration": 1, "cluster": 1,
                 "match_id": 1, "radiant_win": 1, "lobby_type": 1,
                 "players": {"$elemMatch": {"account_id": user["steamid32"]}}},
                sort=[('start_time', -1)], limit=20).skip((pg-1)*20).to_list)
        else:
            matches = yield Op(self.db['matches'].find(
                {'game_mode': {'$nin': black_list},
                 'players': {'$elemMatch': {'account_id': user['steamid32'], 'hero_id': int(hero)}}},
                {"game_mode": 1, "start_time": 1, "duration": 1, "cluster": 1,
                 "match_id": 1, "radiant_win": 1, "lobby_type": 1,
                 'players': {'$elemMatch': {'account_id': user['steamid32']}}},
                sort=[('start_time', -1)], limit=20).skip((pg-1)*20).to_list)

        self.render("user.html", title="Matches", user=user, session=session, matches=matches, max_pages=max_pages,
                    page=pg, hero_current=hero, heroes=libs.heroes, cluster=libs.cluster, mode=libs.mode)


class UserHeroesHandler(BaseHandler):
    @asynchronous
    @engine
    def get(self, sid):

        session = None

        if self.current_user:
            session = yield Op(self.db['users'].find_one, {'_id': self.current_user['userid']})

        user = yield Op(self.db['users'].find_one, {'_id': ObjectId(sid)})

        if user is None:
            return self.send_error(404)

        self.render("user.html", title="Heroes", user=user, session=session, heroes=libs.heroes)


class UserRecordsHandler(BaseHandler):
    @asynchronous
    @engine
    def get(self, sid):

        session = None

        if self.current_user:
            session = yield Op(self.db['users'].find_one, {'_id': self.current_user['userid']})

        user = yield Op(self.db['users'].find_one, {'_id': ObjectId(sid)})

        if user is None:
            return self.send_error(404)

        kills, deaths, assists, gpm = yield [

            Op(self.db["matches"].aggregate,
               [{"$match": {"players.account_id": user["steamid32"], "game_mode": {"$nin": [7, 9, 15]}}},
                {"$project": {"match_id": 1, "radiant_win": 1, "start_time": 1, "players.kills": 1,
                              "players.account_id": 1, "players.player_slot": 1, "players.hero_id": 1}},
                {"$unwind": "$players"},
                {"$match": {"players.account_id": user["steamid32"]}},
                {"$sort": {"players.kills": -1}},
                {"$limit": 1}]),

            Op(self.db["matches"].aggregate,
               [{"$match": {"players.account_id": user["steamid32"], "game_mode": {"$nin": [7, 9, 15]}}},
                {"$project": {"match_id": 1, "radiant_win": 1, "start_time": 1, "players.deaths": 1,
                              "players.account_id": 1, "players.player_slot": 1, "players.hero_id": 1}},
                {"$unwind": "$players"},
                {"$match": {"players.account_id": user["steamid32"]}},
                {"$sort": {"players.deaths": -1}},
                {"$limit": 1}]),

            Op(self.db["matches"].aggregate,
               [{"$match": {"players.account_id": user["steamid32"], "game_mode": {"$nin": [7, 9, 15]}}},
                {"$project": {"match_id": 1, "radiant_win": 1, "start_time": 1, "players.assists": 1,
                              "players.account_id": 1, "players.player_slot": 1, "players.hero_id": 1}},
                {"$unwind": "$players"},
                {"$match": {"players.account_id": user["steamid32"]}},
                {"$sort": {"players.assists": -1}},
                {"$limit": 1}]),

            Op(self.db["matches"].aggregate,
               [{"$match": {"players.account_id": user["steamid32"], "game_mode": {"$nin": [7, 9, 15]}}},
                {"$project": {"match_id": 1, "radiant_win": 1, "start_time": 1, "players.gold_per_min": 1,
                              "players.account_id": 1, "players.player_slot": 1, "players.hero_id": 1}},
                {"$unwind": "$players"},
                {"$match": {"players.account_id": user["steamid32"]}},
                {"$sort": {"players.gold_per_min": -1}},
                {"$limit": 1}])]

        self.render("user.html", title="Records", user=user, session=session,
                    records=(kills['result'], deaths['result'], assists['result'], gpm['result']),
                    heroes=libs.heroes, cluster=libs.cluster, mode=libs.mode)