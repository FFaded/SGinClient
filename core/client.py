import re
import socket

from config import CONFIG
from core.ui import Model, View
from utils.logs import create_logger

MESSAGES = {
    'l': 'lay',
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
        self.cards = None

    def start_game(self):
        response = self._send_message('h')
        if response != 'ack':
            raise ProtocolError('Expected "ack"')

        for i in range(3):
            role = self._read_message()

        if role != 'first':
            self._read_message()

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
        self.cards = cards_as_string.split('|')[1].strip().split(' ')


class GinClient(BaseClient):
    def __init__(self, user_name='John Doe'):
        super().__init__(user_name)
        self.model = Model()
        self.view = View()

    def _step_one(self):
        self._read_message()
        # show discard or steal
        LOGGER.info('Draw or steal ?')
        # waiting for action
        action = input().lower()
        score_message = self._send_message(action)
        self.score = (re.sub('[^0-9]', '', score_message))
        # update view

    def _step_two(self):
        # show which card to lay down
        LOGGER.info('Which card to lay down ?')
        # waiting for action
        card = input()
        score_message = self._send_message('l {}'.format(card))
        self.score = (re.sub('[^0-9]', '', score_message))

    def _step_three(self):
        LOGGER.info('Would you like to knock ?')
        # waiting for action
        choice = input()
        score_message = self._send_message(choice)
        self.score = (re.sub('[^0-9]', '', score_message))
        print(self.score)

    def _update_cards(self):
        cards_as_string = self._read_message()
        self.cards = cards_as_string.split('|')[1].strip().split(' ')
        # update view
