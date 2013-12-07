#!/usr/bin/env python3

from bson import ObjectId
from .base import BaseHandler


class SettingsHandler(BaseHandler):

    def get(self):
        if not self.current_user:
            return self.send_error(403)
        session = self.application.db['sessions'].find_one({'_id': self.current_user})
        if not session:
            return self.send_error(400)
        session = self.application.db['users'].find_one({'_id': session['userid']})
        sessions = self.application.db['sessions'].find({'userid': session['_id']}).sort('last_accessed', -1)
        matches_on_base = self.application.db['matches'].find({'players.account_id': session['steamid32']}).count()
        try:
            progress = len(session['matches'])
        except KeyError:
            progress = 0
        self.render('user-settings.html', active="settings", session=session, sessions=sessions,
                    progress_on_base=matches_on_base, progress=progress)