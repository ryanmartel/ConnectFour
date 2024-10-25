class MessageHandler:

    def __init__(self, logger, game, action, write_sel, clients):
        self.logger = logger
        self.game = game
        self.action = action
        self.write_sel = write_sel
        self.clients = clients

    def handle_message(self, message, sock):
        action = message.get("action")
        if action is not None:
            if action == "ping":
                self.respond(self.action.ping(), sock)

    def new_player_connected(self, addr):
        self.game.add_player(addr)
        if self.game.num_players() == 2:
            self.game.setPregame()
            self.broadcast(self.action.set_pregame())

    def remove_player(self, addr):
        self.game.remove_player(addr)


    def respond(self, msg, sock):
        if msg is not None:
            sock.sendall(msg)


    def broadcast(self, msg):
        for key, _ in self.write_sel.select(0):
            key.fileobj.send(msg)


