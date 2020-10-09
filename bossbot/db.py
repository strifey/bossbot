import os.path
import sqlite3

from xdg import XDG_DATA_HOME


DEFAULT_DB_FILE = 'bossbot.sql'
GR_SETUP_TABLE = 'CREATE TABLE GR_OAUTH_SETUP_DATA(user_id INTEGER PRIMARY KEY, gr_username TEXT, oauth_token TEXT, oauth_secret TEXT)'
GR_OAUTH_TABLE = 'CREATE TABLE GR_OAUTH_ACCESS(user_id INTEGER PRIMARY KEY, gr_username TEXT, access_token TEXT, access_secret TEXT)'


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
            self.conn.commit()

    def cursor(self, *args, **kwargs):
        return self.conn.cursor(*args, **kwargs)

    def store_tmp_gr_oauth(self, user_id, gr_username, oauth_token, oauth_secret):
        cursor = self.cursor()
        cursor.execute(
            'INSERT INTO GR_OAUTH_SETUP_DATA VALUES (?, ?, ?, ?)',
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
            'INSERT INTO GR_OAUTH_ACCESS VALUES (?, ?, ?, ?)',
            (user_id, gr_username, access_token, access_secret),
        )
        self.conn.commit()

    def fetch_user_oauth_access(self, user_id):
        cursor = self.cursor()
        return cursor.execute(
            'SELECT * FROM GR_OAUTH_ACCESS WHERE user_id=:user_id',
            {'user_id': user_id},
        ).fetchone()
