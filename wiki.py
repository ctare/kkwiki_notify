import requests
from datetime import datetime
from bs4 import BeautifulSoup
import bs4
import re
import tokens
from time import sleep

from slacker import Slacker

slack = Slacker(tokens.SLACK_BOT)
notify_ch = 'wiki通知'
notify_renraku_ch = 'wiki通知_連絡事項'
base_url = 'http://www2.teu.ac.jp/kiku/wiki/'
auth = {'Authorization': tokens.WIKI}

# 通知処理の本体
# notifyを参考にしつつ別媒体を追加していく
def notify(ch, update, attachments=None):
    """
    Args: (ch: 投稿するchannel, update: 投稿内容, attachments: slackのoption)
    Return: None
    """

    message = f'<{update.link}|{update.title}>'
    slack.chat.post_message(ch, message, attachments=attachments, as_user=True)

def notify_XXX(ch, update, attachments=None):
    pass

class Update:
    def __init__(self, title, date, link):
        self.title = title
        self.date = date
        self.link = link

def get_updates():
    url = f'{base_url}?RecentChanges'
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

class DiffElm:
    remove_class = 'diff_removed'
    added_class = 'diff_added'
    colors = {remove_class: '#f00', added_class: 'good'}

    def __init__(self, elm):
        self.elm = elm
        self.diff_type = elm.get('class')[0]
        self.text = elm.text

    @staticmethod
    def selector():
        return f'pre .{DiffElm.remove_class}, pre .{DiffElm.added_class}'

# last = datetime(2020, 1, 14)
# updates = list(filter(lambda x: x.date > last, get_updates()))

def get_diffs(update):
    page = update.link[update.link.index('?') + 1:]
    url = f'{base_url}?cmd=diff&page={page}'
    response = requests.get(url, headers=auth)
    soup = BeautifulSoup(response.text, 'html.parser')

    block = []
    sequence = []
    for elm in soup.find('pre').children:

        if isinstance(elm, bs4.NavigableString):
            if len(elm) != 1 and sequence:
                block.append(sequence)
                sequence = []
        else:
            e = DiffElm(elm)
            if sequence and sequence[0].diff_type != e.diff_type:
                block.append(sequence)
                sequence = [e]
            else:
                sequence.append(e)

    return block

# ------------- main process -------------
# last = datetime(2020, 1, 18)
last = datetime.now()
while True:
    sleep(1) # 取得間隔
    updates = list(filter(lambda x: x.date > last, get_updates()))

    if updates:
        last = updates[0].date
        for v in updates[::-1]:
            if v.title not in get_ignores():
                # 大事じゃない連絡通知

                # 通知処理
                # 通知媒体の変更・追加はnotifyを参照
                notify(notify_ch, v)

            if v.title.endswith('連絡事項') or v.title in get_importants():
                # 大事な連絡通知

                block = get_diffs(v)

                # 通知処理 軽い装飾を添えて
                # 通知媒体の変更・追加はnotifyを参照
                attachments = [{
                    "color": DiffElm.colors[v[0].diff_type],
                    "text": "\n".join(map(lambda x: x.text, v)),
                } for v in block]

                notify(notify_renraku_ch, v, attachments=attachments)
