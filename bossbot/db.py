import os.path
import sqlite3
import tempfile
from datetime import datetime

from xdg import XDG_DATA_HOME


DEFAULT_DB_FILE = 'bossbot.sql'
BOSSBOT_DB_SCHEMA = '''\
CREATE TABLE IF NOT EXISTS GR_OAUTH_SETUP_DATA(
    user_id INTEGER PRIMARY KEY, gr_username TEXT, oauth_token TEXT, oauth_secret TEXT
);
CREATE TABLE IF NOT EXISTS GR_OAUTH_ACCESS(
    user_id INTEGER PRIMARY KEY, gr_username TEXT, access_token TEXT, access_secret TEXT
);
CREATE TABLE IF NOT EXISTS LASTFM_USERS(
    user_id INTEGER PRIMARY KEY, lastfm_username TEXT
);
CREATE TABLE IF NOT EXISTS LETTERBOXD_SUBS(
    letterboxd_username TEXT NOT NULL,
    channel_id INTEGER NOT NULL,
    last_announced TIMESTAMP NOT NULL,
    PRIMARY KEY (letterboxd_username, channel_id)
);
CREATE TABLE KARMA_TRACKER(
    user_id INTEGER PRIMARY KEY,
    plus_karma INTEGER,
    minus_karma INTEGER
);
'''


class BossDB:
    schema_ran = False
    testing_tmpfile = None

    def __init__(
        self,
        testing=True,
        db_file=XDG_DATA_HOME.joinpath(DEFAULT_DB_FILE),
    ):
        # use tmpfile db for testing purposes
        if testing and self.testing_tmpfile is None:
            BossDB.testing_tmpfile = tempfile.NamedTemporaryFile().name

        self.db_file = db_file if not testing else self.testing_tmpfile
        self.conn = sqlite3.connect(
            self.db_file,
            detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES,
        )

        if not self.schema_ran:
            cursor = self.conn.cursor()
            cursor.executescript(BOSSBOT_DB_SCHEMA)
            self.conn.commit()
            BossDB.schema_ran = True

    def cursor(self, *args, **kwargs):
        return self.conn.cursor(*args, **kwargs)

class KarmaDB(BossDB):
    def set_user_karma(self, user_id, plus_karma, minus_karma):
        cursor = self.cursor()
        cursor.execute(
            (
                'INSERT INTO KARMA_TRACKER VALUES (?, ?, ?) '
                'ON CONFLICT(user_id) DO UPDATE SET '
                'plus_karma=excluded.plus_karma, minus_karma=excluded.minus_karma'
            ),
            (user_id, plus_karma, minus_karma),
        )
        self.conn.commit()

    def get_user_karma(self, user_id):
        cursor = self.cursor()
        plus_karma = cursor.execute(
            'SELECT plus_karma FROM KARMA_TRACKER WHERE user_id=:user_id',
            {'user_id': user_id},
        ).fetchone()
        minus_karma = cursor.execute(
            'SELECT minus_karma FROM KARMA_TRACKER WHERE user_id=:user_id',
            {'user_id': user_id},
        ).fetchone()
        self.conn.commit()
        if not plus_karma:
            self.set_user_karma(user_id, 0, 0)
            return (0, 0)
        return (plus_karma[0], minus_karma[0])

    def increment_user_karma(self, user_id):
        plus_karma, minus_karma = self.get_user_karma(user_id)
        self.set_user_karma(user_id, plus_karma + 1, minus_karma)

    def decrement_user_karma(self, user_id):
        plus_karma, minus_karma = self.get_user_karma(user_id)
        self.set_user_karma(user_id, plus_karma, minus_karma + 1)


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

class LastFMDB(BossDB):
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


class AlreadySubbedError(Exception):
    pass


class LetterboxdDB(BossDB):
    def sub_letterboxd_user(self, letterboxd_username, channel_id):
        cursor = self.cursor()

        try:
            cursor.execute(
                ('INSERT INTO LETTERBOXD_SUBS VALUES (?, ?, ?);'),
                (letterboxd_username, channel_id, datetime.now()),
            )
        except sqlite3.IntegrityError:
            raise AlreadySubbedError

        self.conn.commit()
        return cursor.execute(
            'SELECT * FROM LETTERBOXD_SUBS WHERE letterboxd_username=? AND channel_id=?;',
            (letterboxd_username, channel_id)
        ).fetchone()

    def unsub_letterboxd_user(self, letterboxd_username, channel_id):
        cursor = self.cursor()
        cursor.execute(
            ('DELETE FROM LETTERBOXD_SUBS WHERE letterboxd_username=? AND channel_id=?;'),
            (letterboxd_username, channel_id),
        )
        self.conn.commit()

    def get_all_subs(self):
        return self.cursor().execute('SELECT* FROM LETTERBOXD_SUBS').fetchall()

    def set_last_announced(self, letterboxd_username, channel_id, last_announced):
        cursor = self.cursor()
        cursor.execute(
            ('UPDATE LETTERBOXD_SUBS SET last_announced=:last_announced WHERE letterboxd_username=:letterboxd_username AND channel_id=:channel_id;'),
            {'letterboxd_username': letterboxd_username, 'channel_id': channel_id, 'last_announced': last_announced},
        )
        self.conn.commit()
