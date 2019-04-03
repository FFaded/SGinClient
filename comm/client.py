import socket

from config import CONFIG
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


class Client:

    BUFFER_SIZE = 1024

    def __init__(self, user_name='John Doe'):
        self.user_name = user_name
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def _send_message(self, code, reply=True):
        splitted = code.split(' ')
        if splitted[0] in MESSAGES.keys():
            data = '{}: {}'.format(self.user_name, ' '.join(splitted)).encode('utf-8')
            self.socket.sendto(data, (CONFIG['HOST'], CONFIG['PORT']))
        else:
            raise ProtocolError('The message could not be understood')
        if reply:
            return self._read_message()

    def _read_message(self):
        data = self.socket.recv(self.BUFFER_SIZE).decode('utf-8')
        LOGGER.info(data)
        return data


class GinClient(Client):
    def __init__(self, user_name='John Doe'):
        super().__init__(user_name)
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
        self._read_message()
        while True:
            LOGGER.info('Draw or steal ? (d/s)')
            action = input().lower()
            if action in ['d', 's']:
                self._send_message(action, reply=False)
                break
            else:
                LOGGER.info('You got to type "s" or "d"')

        self.get_cards()
        while True:
            LOGGER.info('Which card to lay down ?')
            card = input()
            if card in self.cards:
                self._send_message('l {}'.format(card), reply=False)
                break
            else:
                LOGGER.info('You got to type a card from your hand')

        self.get_cards()
        LOGGER.info('Would you like to knock ? (y/n)')
        choice = input()
        choice = 'k' if choice == 'y' else 'nk'
        self._send_message(choice)

    def get_cards(self):
        cards_as_string = self._read_message()
        self.cards = cards_as_string.split('|')[1].strip().split(' ')
