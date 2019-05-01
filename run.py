from core.client import MainThread

main = MainThread()
main.start()

main.client.view.start()

#
# client = CommandGinClient()
# client.init_game()
# client.start_game()
