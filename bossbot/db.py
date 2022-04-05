import os.path
import sqlite3

from xdg import XDG_DATA_HOME


DEFAULT_DB_FILE = 'bossbot.sql'
GR_SETUP_TABLE = 'CREATE TABLE GR_OAUTH_SETUP_DATA(user_id INTEGER PRIMARY KEY, gr_username TEXT, oauth_token TEXT, oauth_secret TEXT)'
GR_OAUTH_TABLE = 'CREATE TABLE GR_OAUTH_ACCESS(user_id INTEGER PRIMARY KEY, gr_username TEXT, access_token TEXT, access_secret TEXT)'
LASTFM_USER_TABLE = 'CREATE TABLE LASTFM_USERS(user_id INTEGER PRIMARY KEY, lastfm_username TEXT)'
KARMA_TRACKER_TABLE = 'CREATE TABLE KARMA_TRACKER(user_id INTEGER PRIMARY KEY, karma INTEGER)'


class BossDB:
    def __init__(
        self,
        db_file=XDG_DATA_HOME.joinpath(DEFAULT_DB_FILE),
    ):
        self.db_file = db_file
        create = False

        if not os.path.exists(self.db_file):
            create = True

        self.conn = sqlite3.connect(self.db_file)
        if create:
            cursor = self.conn.cursor()
            cursor.execute(GR_SETUP_TABLE)
            cursor.execute(GR_OAUTH_TABLE)
            cursor.execute(LASTFM_USER_TABLE)
            cursor.execute(KARMA_TRACKER_TABLE)
            self.conn.commit()

    def cursor(self, *args, **kwargs):
        return self.conn.cursor(*args, **kwargs)

class KarmaDB(BossDB):
    def set_user_karma(self, user_id, karma):
        cursor = self.cursor()
        cursor.execute(
            (
                'INSERT INTO KARMA_TRACKER VALUES (?, ?) '
                'ON CONFLICT(user_id) DO UPDATE SET '
                'karma=excluded.karma'
            ),
            (user_id, karma),
        )
        self.conn.commit()

    def get_user_karma(self, user_id):
        cursor = self.cursor()
        karma = cursor.execute(
            'SELECT karma FROM KARMA_TRACKER WHERE user_id=:user_id',
            {'user_id': user_id},
        ).fetchone()[0]
        self.conn.commit()
        if not karma:
            self.set_user_karma(user_id, 0)
            return 0
        return karma



class GoodReadsDB(BossDB):
    def store_tmp_gr_oauth(self, user_id, gr_username, oauth_token, oauth_secret):
        cursor = self.cursor()
        cursor.execute(
            (
                'INSERT INTO GR_OAUTH_SETUP_DATA VALUES (?, ?, ?, ?) '
                'ON CONFLICT(user_id) DO UPDATE SET '
                'gr_username=excluded.gr_username, oauth_token=excluded.oauth_token, oauth_secret=excluded.oauth_secret'
            ),
            (user_id, gr_username, oauth_token, oauth_secret),
        )
        self.conn.commit()

    def pop_tmp_gr_oauth(self, user_id):
        cursor = self.cursor()

        user = cursor.execute(
            'SELECT * FROM GR_OAUTH_SETUP_DATA WHERE user_id=:user_id',
            {'user_id': user_id},
        ).fetchone()

        cursor.execute(
            'DELETE FROM GR_OAUTH_SETUP_DATA WHERE user_id=:user_id',
            {'user_id': user_id},
        )
        self.conn.commit()
        return user

    def add_gr_user_oauth_access(self, user_id, gr_username, access_token, access_secret):
        cursor = self.cursor()
        cursor.execute(
            (
                'INSERT INTO GR_OAUTH_ACCESS VALUES (?, ?, ?, ?) '
                'ON CONFLICT(user_id) DO UPDATE SET '
                'gr_username=excluded.gr_username, access_token=excluded.access_token, access_secret=excluded.access_secret'
            ),
            (user_id, gr_username, access_token, access_secret),
        )
        self.conn.commit()

    def fetch_gr_user_oauth_access(self, user_id):
        cursor = self.cursor()
        return cursor.execute(
            'SELECT * FROM GR_OAUTH_ACCESS WHERE user_id=:user_id',
            {'user_id': user_id},
        ).fetchone()

    def store_lastfm_username(self, user_id, lastfm_username):
        cursor = self.cursor()
        cursor.execute(
            (
                'INSERT INTO LASTFM_USERS VALUES (?, ?) '
                'ON CONFLICT(user_id) DO UPDATE SET '
                'lastfm_username=excluded.lastfm_username'
            ),
            (user_id, lastfm_username),
        )
        self.conn.commit()

    def fetch_lastfm_user(self, user_id):
        cursor = self.cursor()
        return cursor.execute(
            'SELECT lastfm_username FROM LASTFM_USERS WHERE user_id=:user_id',
            {'user_id': user_id},
        ).fetchone()
