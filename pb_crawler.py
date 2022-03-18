import logging
import time

import requests
from dateutil.parser import parse
from lxml import html
from pymongo import MongoClient

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')


BASEURL = 'https://pastebin.com'
HEADERS = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.82 Safari/537.36"}
UNKNOWN_AUTHORS = ['Guest', 'Unknown', 'Anonymous']
UNTITLED = ['Untitled']


class Paste(object):
    def __init__(self, uid, author, title, content, timestamp):
        self.uid = uid
        self.timestamp = timestamp
        self.author = author
        self.title = title
        self.content = content

    def to_json(self):
        return {'uid': self.uid, 'timestamp': self.timestamp.strftime("%Y-%m-%d %H:%M:%S"), 'author': self.author,
                'title': self.title, 'content': self.content}


def get_page_tree(url):
    page = requests.get(url=url, headers=HEADERS)
    return html.fromstring(page.content)


def get_recent_pastes():
    logging.info('Getting recent pastes')
    tree = get_page_tree(BASEURL)
    count = len(tree.xpath('/html/body/div[1]/div[2]/div[2]/ul/li'))
    uids = list()
    for i in range(count):
        uids.append(tree.xpath(f'/html/body/div[1]/div[2]/div[2]/ul/li[{i + 1}]/a')[0].attrib['href'])
    logging.info(f'Retrieved {count} latest pastes from {BASEURL} ({uids})')
    return uids


def get_paste_data(uid):
    tree = get_page_tree(f'{BASEURL}{uid}')
    try:
        title = tree.xpath('/html/body/div[1]/div[2]/div[1]/div[3]/div[1]/div[3]/div[1]/h1')[0].text
        author = tree.xpath('/html/body/div[1]/div[2]/div[1]/div[3]/div[1]/div[3]/div[2]/div[1]/a')[0].text
        timestamp = tree.xpath('/html/body/div[1]/div[2]/div[1]/div[3]/div[1]/div[3]/div[2]/div[2]/span')[0].attrib['title']
        content = str(tree.xpath('/html/body/div[1]/div[2]/div[1]/div[3]/textarea/text()')[0]).strip()
    except Exception as e:
        logging.error(f'Failed to parse paste from {BASEURL}{uid}, error: {str(e)}')
        return None
    return Paste(uid=uid, author=author if author not in UNKNOWN_AUTHORS else '',
                 title=title if title not in UNTITLED else '',
                 timestamp=parse(timestamp, tzinfos={"CDT": "UTC-5"}), content=content)


if __name__ == "__main__":
    client = MongoClient('mongodb', 27017)
    db = client.pb_crawler
    collection = db.pastes
    logging.info('Starting crawler...')
    while True:
        uids = get_recent_pastes()
        for uid in uids:
            data = get_paste_data(uid)
            if data:
                logging.info(f'Paste: {data.to_json()}')
                collection.update_one({'uid': data.uid}, {'$set': data.to_json()}, upsert=True)

        logging.info('Recrawling in 2m, see this in the meantime: https://www.youtube.com/watch?v=dQw4w9WgXcQ')
        time.sleep(120)
