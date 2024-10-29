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
            if action == "move":
                res = self.move(message, self.clients.get(sock))
                self.respond(res, sock)
                self.broadcast(self.action.game_status(None))
            if action == "set_name":
                self.set_name(message, self.clients.get(sock))


    def new_player_connected(self, addr):
        self.game.add_player(addr)
        if self.game.num_players() == 2:
            self.game.setPregame()
            self.broadcast(self.action.set_pregame())

    def remove_player(self, addr):
        self.game.remove_player(addr)
        self.game.setWaiting()

    def set_name(self, msg, addr):
        name = msg.get("name")
        self.game.set_player_name(name, addr)
        self.logger.info(f"set host: {addr[0]} post: {addr[1]} name: {name}")
        if self.game.num_names_assigned() == 2:
            self.game.setRun()
            self.broadcast(self.action.set_run())

    def move(self, msg, addr):
        column = msg.get("column")
        turn_count = msg.get("turn-count")
        res = self.game.move(addr, column, turn_count)
        return self.action.move(res)

    def respond(self, msg, sock):
        if msg is not None:
            sock.sendall(msg)


    def broadcast(self, msg):
        for key, _ in self.write_sel.select(0):
            key.fileobj.send(msg)


