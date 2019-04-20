import tkinter as tk

from PIL import Image, ImageTk

ONE = 1
TWO = 2
THREE = 3

STEPS = {
    'ONE': ONE,
    'TWO': TWO,
    'THREE': THREE
}


class Model:
    def __init__(self):
        self.cards = None

    def update(self, cards):
        self.cards = cards


class View:
    def __init__(self, card_width=50, card_height=73):
        self.hand = []
        self._model = None
        self.root = tk.Tk()
        self.root.title('Gin Client')
        self._card_width = card_width
        self._card_height = card_height
        self._is_drawing_mode = False
        self._is_erasing_mode = False
        self._card_images = [None] * 10
        self.discarded_card = None
        self._step = STEPS['ONE']
        self._init_view()
        self.update_hand(['Ah', 'Ks', 'Ah', 'Ks', 'Ah', 'Ks', 'Ah', 'Ks', 'Ah', 'Ks'])
        self.update_discarded_card('As')

    def stop(self):
        self.root.destroy()

    def start(self):
        self.root.protocol("WM_DELETE_WINDOW", self.stop)
        self.root.mainloop()

    def discard(self, event):
        pass

    # internal methods
    def _init_view(self):
        # frames
        self.main_frame = tk.Frame(self.root, height=73)
        self.separator_frame = tk.Frame(self.root, height=10, bg='gainsboro')
        self.menu_frame = tk.Frame(self.root, height=50, bg='white')
        self.buttons_frame = tk.Frame(self.menu_frame, bg='white')

        # menu
        self.play_and_pause = tk.StringVar()
        self.play_and_pause.set('Pause')
        self.reset_button = tk.Button(self.buttons_frame, text='Reset', command=None)
        self.play_button = tk.Button(self.buttons_frame, textvariable=self.play_and_pause, command=None)

        # display
        self.menu_frame.pack(fill=tk.X)
        self.separator_frame.pack(fill=tk.X, pady=10)
        self.main_frame.pack()
        self.buttons_frame.pack(side=tk.TOP)

        # game area
        for i in range(10):
            card_label = tk.Label(self.main_frame,
                                  width=self._card_width,
                                  height=self._card_height)
            card_label.pack(side=tk.LEFT, padx=3)
            card_label.bind("<Button-1>", self.discard)
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
        for i, card in enumerate(model):
            img = ImageTk.PhotoImage(Image.open('assets/img/{}.png'.format(card)))
            self.hand[i].image = img
            self.hand[i].configure(image=img)

    def update_discarded_card(self, card):
        self.discarded_card = card
        img = ImageTk.PhotoImage(Image.open('assets/img/{}.png'.format(card)))
        self.discarded_card_label.image = img
        self.discarded_card_label.configure(image=img)

