import requests
from datetime import datetime
from bs4 import BeautifulSoup
import re
import tokens
from time import sleep

from slacker import Slacker

slack = Slacker(tokens.SLACK_BOT)
notify_ch = 'wiki通知'
notify_renraku_ch = 'wiki通知_連絡事項'

def notify(ch, update):
    message = f'<{update.link}|{update.title}>'
    slack.chat.post_message(ch, message, as_user=True)

class Update:
    def __init__(self, title, date, link):
        self.title = title
        self.date = date
        self.link = link

def get_updates():
    url = 'http://www2.teu.ac.jp/kiku/wiki/?RecentChanges'
    auth = {'Authorization': tokens.WIKI}
    response = requests.get(url, headers=auth)

    soup = BeautifulSoup(response.text, 'html.parser')

    data = []
    for e in soup.select('#body li'):
        date_str = re.sub(' \(.\) ', ' ', e.next)
        date = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S - ')
        a = e.find('a')
        data.append(Update(a.text, date, a.get('href')))
    return data

def get_importants():
    with open('./importants.list', 'r') as f:
        data = f.read().split('\n')[:-1]
    return data

def get_ignores():
    with open('./ignores.list', 'r') as f:
        data = f.read().split('\n')[:-1]
    return data

# last = datetime(2020, 1, 14)
last = datetime.now()
while True:
    sleep(1)
    updates = list(filter(lambda x: x.date > last, get_updates()))

    if updates:
        last = updates[0].date
        for v in updates[::-1]:
            if v.title not in get_ignores():
                notify(notify_ch, v)

            if v.title.endswith('連絡事項') or v.title in get_importants():
                notify(notify_renraku_ch, v)
