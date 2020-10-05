from time import sleep
from xml.etree import ElementTree

import requests
from requests_oauthlib import OAuth1
from requests_oauthlib import OAuth1Session

user = None
user_token = None
user_secret = None

class GoodReads:
    base_url = 'https://www.goodreads.com/'

    def __init__(self, api_key, api_secret):
        self.api_key = api_key
        self.api_secret = api_secret
        self.session = requests.Session()

    def get(self, *args, **kwargs):
        args = (self.base_url + args[0], *args[1:])
        if 'params' in kwargs:
            kwargs['params']['key'] = self.api_key
        else:
            kwargs['params'] = {}
            kwargs['params']['key'] = self.api_key
        resp = requests.get(*args, **kwargs)
        print(resp.text)
        return ElementTree.fromstring(resp.text)

    def start_oauth(self):
        o_sess = OAuth1Session(self.api_key, client_secret=self.api_secret)

        fetch_resp = o_sess.fetch_request_token(f'{self.base_url}oauth/request_token')
        oauth_token = fetch_resp.get('oauth_token')
        oauth_secret = fetch_resp.get('oauth_token_secret')

        authorization_url = o_sess.authorization_url(f'{self.base_url}oauth/authorize')
        oauth_access_session = OAuth1Session(
            self.api_key,
            client_secret=self.api_secret,
            resource_owner_key=oauth_token,
            resource_owner_secret=oauth_secret,
        )
        return authorization_url, oauth_access_session

    def finish_oauth(self, oauth_access_session):
        access_token_url = f'{self.base_url}oauth/access_token'
        access_token = oauth_access_session._fetch_token(access_token_url)
        return access_token

    def get_currently_reading(self, username, oauth_token, oauth_token_secret):
        resp = self.get('user/show', params={'username': username})
        user_id = resp.find('user').find('id').text

        return self.get(
            'review/list',
            auth=OAuth1(
                self.api_key, self.api_secret,
                oauth_token, oauth_token_secret,
            ),
            params={'v': 2, 'format': 'xml', 'id': user_id, 'shelf': 'currently-reading'},
        )


async def register_gr_user(bot, message):
    gr = GoodReads(
        bot.config['goodreads']['API_KEY'],
        bot.config['goodreads']['API_SECRET'],
    )
    auth_link, finish_sess = gr.start_oauth()
    s = 10
    await message.channel.send(f'Click the link below in the next {s} seconds:\n{auth_link}')
    sleep(s)
    try:
        tokens = gr.finish_oauth(finish_sess)
        global user
        global user_token
        global user_secret
        user = message.content.split()[1]
        user_token = tokens['oauth_token']
        user_secret = tokens['oauth_token_secret']
    except Exception as e:
        print(e)
        await message.channel.send('ugh gross, we failed')
    else:
        await message.channel.send('oauth complete!')


async def handle_gr_cmd(bot, message):
    gr = GoodReads(
        bot.config['goodreads']['API_KEY'],
        bot.config['goodreads']['API_SECRET'],
    )
    global user
    global user_token
    global user_secret
    resp = gr.get_currently_reading(user, user_token, user_secret)
    resp = resp.find('reviews').find('review').find('book').find('title').text
    await message.channel.send(resp)
