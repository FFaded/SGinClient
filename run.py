from core.client import CommandGinClient

# client = GinClient()
# main = MainThread(client)
# main.start()
#
# client.view.start()
#

client = CommandGinClient()
client.init_game()
client.start_game()
