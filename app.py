import sys
from io import BytesIO

import telegram
from flask import Flask, request, send_file

from fsm import TocMachine

import bs4
from bs4 import BeautifulSoup
import requests

API_TOKEN = '385048749:AAEqaJO5GIdjJSDfMEkSdAn0wNK_18VOoP0'
WEBHOOK_URL = 'https://bf96dbf0.ngrok.io/hook'

app = Flask(__name__)
bot = telegram.Bot(token=API_TOKEN)
machine = TocMachine(
    states=[
        'searchBoard',
        'articles',
        'lastPage',
		'chooseArticle',
		'count'
    ],
    transitions=[
        {
            'trigger': 'advance',
            'source': 'searchBoard',
            'dest': 'articles',
        },
        {
            'trigger': 'advance',
            'source': 'articles',
            'dest': 'searchBoard',
            'conditions': 'rechoose'
        },
        {
            'trigger': 'advance',
            'source': 'articles',
            'dest': 'lastPage',
            'conditions': 'goto_lastPage'
        },
        {
            'trigger': 'advance',
            'source': 'articles',
            'dest': 'chooseArticle',
            'conditions': 'read_article'
        },
        {
            'trigger': 'advance',
            'source': 'lastPage',
            'dest': 'lastPage',
            'conditions': 'goto_lastPage'
        },
        {
            'trigger': 'advance',
            'source': 'lastPage',
            'dest': 'chooseArticle',
            'conditions': 'read_article'
        },

        {
            'trigger': 'advance',
            'source': 'chooseArticle',
            'dest': 'searchBoard',
            'conditions': 'backto_search'
        },
        {
            'trigger': 'go_back',
            'source': [
                'state1',
                'state2'
            ],
            'dest': 'user'
        }
    ],
    initial='searchBoard',
    auto_transitions=False,
    show_conditions=True,
)


def _set_webhook():
    status = bot.set_webhook(WEBHOOK_URL)
    if not status:
        print('Webhook setup failed')
        sys.exit(1)
    else:
        print('Your webhook URL has been set to "{}"'.format(WEBHOOK_URL))


@app.route('/hook', methods=['POST'])
def webhook_handler():
    update = telegram.Update.de_json(request.get_json(force=True), bot)
    print(update.message)
    print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!11')
    machine.advance(update)

    return 'ok'


@app.route('/show-fsm', methods=['GET'])
def show_fsm():
    byte_io = BytesIO()
    machine.graph.draw(byte_io, prog='dot', format='png')
    byte_io.seek(0)
    return send_file(byte_io, attachment_filename='fsm.png', mimetype='image/png')


if __name__ == "__main__":
    _set_webhook()
    app.run()
