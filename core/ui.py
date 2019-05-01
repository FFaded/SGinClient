import tkinter as tk

from PIL import Image, ImageTk


class View:

    MAX_AMOUNT_OF_CARDS = 11

    def __init__(self, client, card_width=50, card_height=73):
        self.client = client
        self.hand = []
        self.model = None
        self._card_width = card_width
        self._card_height = card_height
        self._card_images = [None] * 10
        self._card_to_discard = None
        self._selected_card = None
        self.root = tk.Tk()
        self.root.title('Gin Client')
        self._init_view()

    def stop(self):
        self.root.destroy()

    def start(self):
        self.root.protocol("WM_DELETE_WINDOW", self.stop)
        self.root.mainloop()

    def update(self, model):
        self._update_hand(model.hand)
        self._update_discarded_card(model.discarded_card)
        self._update_score(model.score)

    def _update_hand(self, hand):
        for i in range(self.MAX_AMOUNT_OF_CARDS):
            if i < len(hand):
                self.hand[i].name = hand[i]
                img = ImageTk.PhotoImage(Image.open('assets/img/{}.png'.format(hand[i])))
            else:
                img = ''
            self.hand[i].image = img
            self.hand[i].configure(image=img)

    def _update_discarded_card(self, card):
        if card:
            self.discarded_card_label.name = card
            img = ImageTk.PhotoImage(Image.open('assets/img/{}.png'.format(card)))
        else:
            img = ''
        self.discarded_card_label.image = img
        self.discarded_card_label.configure(image=img)

    def _update_score(self, score):
        self.score = score

    def _init_view(self):
        # frames
        self.main_frame = tk.Frame(self.root, height=73)
        self.separator_frame = tk.Frame(self.root, height=10, bg='gainsboro')
        self.menu_frame = tk.Frame(self.root, height=50, bg='white')
        self.buttons_frame = tk.Frame(self.menu_frame, bg='white')

        # menu
        self.drawing_button = tk.Button(self.buttons_frame, text='Draw', command=self._draw)
        self.stealing_button = tk.Button(self.buttons_frame, text='Steal', command=self._steal)
        self.laying_button = tk.Button(self.buttons_frame, text='Lay card', command=self._lay)
        self.knocking_button = tk.Button(self.buttons_frame, text='Knock', command=self._knock)
        self.passing_button = tk.Button(self.buttons_frame, text='Pass', command=self._do_not_knock)

        # display
        self.menu_frame.pack(fill=tk.X)
        self.separator_frame.pack(fill=tk.X, pady=10)
        self.main_frame.pack(expand=0)
        self.buttons_frame.pack(side=tk.TOP)
        self.laying_button.pack(side=tk.LEFT, padx=5)
        self.drawing_button.pack(side=tk.LEFT, padx=5)
        self.stealing_button.pack(side=tk.LEFT, padx=5)
        self.passing_button.pack(side=tk.RIGHT, padx=5)
        self.knocking_button.pack(side=tk.RIGHT, padx=5)

        # game area
        for i in range(self.MAX_AMOUNT_OF_CARDS):
            card_label = tk.Label(self.main_frame)
            card_label.pack(side=tk.LEFT, padx=3)
            card_label.bind("<Button-1>", self._select_card)
            card_label.index = i
            self.hand.append(card_label)

        img = ImageTk.PhotoImage(Image.open('assets/img/back.png'))
        stack_label = tk.Label(self.main_frame,
                               width=self._card_width,
                               height=self._card_height,
                               image=img)
        stack_label.image = img
        stack_label.pack(side=tk.RIGHT, padx=3)

        self.discarded_card_label = tk.Label(self.main_frame,
                                             width=self._card_width,
                                             height=self._card_height)
        self.discarded_card_label.pack(side=tk.RIGHT, padx=3)

        vseparator = tk.Canvas(self.main_frame,
                               width=100,
                               height=self._card_height)

        vseparator.pack(side=tk.RIGHT)

    def _lay(self):
        print(self.client.state)
        if self.client.state is self.client.LAYING and self._card_to_discard:
            self.discarded_card_label.image = self._card_to_discard.image
            self.discarded_card_label.configure(image=self.discarded_card_label.image)
            self.discarded_card_label.name = self._card_to_discard.name
            self._card_to_discard.configure(image='')
            self._card_to_discard.configure(bg='gray94')
            self.client.card = self._card_to_discard.name
            self._card_to_discard.image = None
            self._card_to_discard = None
            self.client.state = self.client.KNOCKING

    def _draw(self):
        print(self.client.state)
        if self.client.state is self.client.DRAWING:
            self.client.state = self.client.LAYING
            self.client.action = 'd'

    def _steal(self):
        if self.client.state is self.client.DRAWING:
            self.client.state = self.client.LAYING
            self.hand.append(self.discarded_card_label.name)
            self.client.action = 's'

    def _knock(self):
        if self.client.state is self.client.KNOCKING:
            self.client.state = None
            self.client.choice = 'k'

    def _do_not_knock(self):
        if self.client.state is self.client.KNOCKING:
            self.client.state = None
            self.client.choice = 'nk'

    def _select_card(self, event):
        if self._card_to_discard is self.hand[event.widget.index]:
            self._card_to_discard.configure(bg='gray94')
            self._card_to_discard = None
        else:
            if self.hand[event.widget.index].image:
                self._card_to_discard = self.hand[event.widget.index]
                for card in self.hand:
                    if card is self._card_to_discard:
                        self._card_to_discard.configure(bg='blue')
                    else:
                        self._card_to_discard.configure(bg='gray94')
