from core.client import CommandGinClient
from core.ui import View
a = CommandGinClient()

b = View(a)
b.start()

a = CommandGinClient()
a.start_game()
