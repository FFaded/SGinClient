import tkinter as tk

from PIL import Image, ImageTk


class Model:
    def __init__(self):
        self.cards = None

    def update(self, cards):
        self.cards = cards


class View:

    MAX_AMOUNT_OF_CARDS = 11

    def __init__(self, client, card_width=50, card_height=73):
        self.client = client
        self.hand = []
        self._model = None
        self._card_width = card_width
        self._card_height = card_height
        self._card_images = [None] * 10
        self._card_to_discard = None
        self._selected_card = None
        self.root = tk.Tk()
        self.root.title('Gin Client')
        self._init_view()
        self.update_hand(['Ah', 'Ks', 'Ah', 'Ks', 'Ah', 'Ks', 'Ah', 'Ks', 'Ah', 'Ks'])
        self.update_discarded_card('As')

    def stop(self):
        self.root.destroy()

    def start(self):
        self.root.protocol("WM_DELETE_WINDOW", self.stop)
        self.root.mainloop()

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
                        card.configure(bg='gray94')

    def lay(self):
        if self._card_to_discard:
            self.discarded_card_label.image = self._card_to_discard.image
            self.discarded_card_label.configure(image=self.discarded_card_label.image)
            self._card_to_discard.configure(image='')
            self._card_to_discard.configure(bg='gray94')
            self._card_to_discard.image = None
            self._card_to_discard = None

    def draw(self):
        pass

    def steal(self):
        pass

    def _init_view(self):
        # frames
        self.main_frame = tk.Frame(self.root, height=73)
        self.separator_frame = tk.Frame(self.root, height=10, bg='gainsboro')
        self.menu_frame = tk.Frame(self.root, height=50, bg='white')
        self.buttons_frame = tk.Frame(self.menu_frame, bg='white')

        # menu
        self.drawing_button = tk.Button(self.buttons_frame, text='Draw', command=self.draw)
        self.stealing_button = tk.Button(self.buttons_frame, text='Steal', command=self.steal)
        self.laying_button = tk.Button(self.buttons_frame, text='Lay card', command=self.lay)

        # display
        self.menu_frame.pack(fill=tk.X)
        self.separator_frame.pack(fill=tk.X, pady=10)
        self.main_frame.pack(expand=0)
        self.buttons_frame.pack(side=tk.TOP)
        self.laying_button.pack(side=tk.LEFT, padx=5)
        self.drawing_button.pack(side=tk.LEFT, padx=5)
        self.stealing_button.pack(side=tk.LEFT, padx=5)

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

    def update_hand(self, model):
        for i in range(self.MAX_AMOUNT_OF_CARDS):
            if i < len(model):
                img = ImageTk.PhotoImage(Image.open('assets/img/{}.png'.format(model[i])))
            else:
                img = ''
            self.hand[i].image = img
            self.hand[i].configure(image=img)

    def update_discarded_card(self, card):
        img = ImageTk.PhotoImage(Image.open('assets/img/{}.png'.format(card)))
        self.discarded_card_label.image = img
        self.discarded_card_label.configure(image=img)
