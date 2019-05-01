import re
import socket
import threading
import time

from config import CONFIG
from core.model import Model
from core.ui import View
from utils.logs import create_logger

MESSAGES = {
    'l': '_lay',
    'd': 'draw',
    'k': 'knock',
    'nk': 'not knock',
    's': 'steal',
    'h': 'hello',
    'g': 'game'
}

LOGGER = create_logger()


class ProtocolError(Exception):
    pass


class BaseClient:

    BUFFER_SIZE = 1024

    def __init__(self, user_name='John Doe'):
        self.user_name = user_name
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.starting_situation = None

    def init_game(self):
        response = self._send_message('h')
        if response != 'ack':
            raise ProtocolError('Expected "ack"')

        for i in range(3):
            role = self._read_message()

        if role != 'first':
            self.starting_situation = self._read_message()

    def start_game(self):
        while True:
            self.play_round()
            self._read_message()

    def play_round(self):
        self._step_one()

        self._update_cards()

        self._step_two()

        self._update_cards()

        self._step_three()

    def _send_message(self, code):
        splitted = code.split(' ')
        if splitted[0] in MESSAGES.keys():
            data = '{}: {}'.format(self.user_name, ' '.join(splitted)).encode('utf-8')
            self.socket.sendto(data, (CONFIG['HOST'], CONFIG['PORT']))
        else:
            raise ProtocolError('The message could not be understood')

        return self._read_message()

    def _read_message(self):
        data = self.socket.recv(self.BUFFER_SIZE).decode('utf-8')
        LOGGER.info(data)
        return data

    def _step_one(self):
        pass

    def _step_two(self):
        pass

    def _step_three(self):
        pass

    def _update_cards(self):
        pass


class CommandGinClient(BaseClient):
    def __init__(self, user_name='John Doe'):
        super().__init__(user_name)
        self.cards = None

    def _step_one(self):
        self._read_message()
        while True:
            LOGGER.info('Draw or steal ? (d/s)')
            action = input().lower()
            if action in ['d', 's']:
                self._send_message(action)
                break
            else:
                LOGGER.info('You got to type "s" or "d"')

    def _step_two(self):
        while True:
            LOGGER.info('Which card to lay down ?')
            card = input()
            if card in self.cards:
                self._send_message('l {}'.format(card))
                break
            else:
                LOGGER.info('You got to type a card from your hand')

    def _step_three(self):
        LOGGER.info('Would you like to knock ? (y/n)')
        choice = input()
        choice = 'k' if choice == 'y' else 'nk'
        self._send_message(choice)

    def _update_cards(self):
        cards_as_string = self._read_message()
        self.cards = cards_as_string.split('|')[1].strip().split(',')


class GinClient(BaseClient):
    DRAWING = 0
    LAYING = 1
    KNOCKING = 2

    def __init__(self, user_name='John Doe'):
        super().__init__(user_name)
        self.model = Model()
        self.view = View(self)
        self.action = None
        self.card = None
        self.choice = None
        self.state = None

    def init_game(self):
        super(GinClient, self).init_game()
        if self.starting_situation:
            self._parse_hand(self.starting_situation)
            self.view.update(self.model)

    def _step_one(self):
        self._parse_hand(self._read_message())
        self.view.model = self.model
        self.view.update(self.model)
        LOGGER.info('Draw or steal ?')
        self.state = self.DRAWING
        while not self.action:
            time.sleep(1)

        score_message = self._send_message(self.action)
        self.action = None
        self.score = (re.sub('[^0-9]', '', score_message))
        self.state = self.LAYING
        print(self.model.discarded_card)
        print(self.model.hand)

    def _step_two(self):
        LOGGER.info('Which card to lay down ?')
        while not self.card:
            time.sleep(1)

        score_message = self._send_message('l {}'.format(self.card))
        self.card = None
        self.score = (re.sub('[^0-9]', '', score_message))
        self.state = self.KNOCKING

    def _step_three(self):
        LOGGER.info('Would you like to knock ?')
        while not self.choice:
            time.sleep(1)

        score_message = self._send_message(self.choice)
        self.choice = None
        self.score = (re.sub('[^0-9]', '', score_message))
        self.state = self.DRAWING

    def _update_cards(self):
        self._parse_hand(self._read_message())
        self.view.update(self.model)

    def _parse_hand(self, msg):
        self.model.discarded_card, hand = msg.replace(' ', '').split('|')
        self.model.hand = hand.split(',')


class MainThread(threading.Thread):
    def __init__(self, client):
        threading.Thread.__init__(self)
        self.client = client

    def run(self):
        self.client.init_game()
        self.client.start_game()

