from socket import socket

from client_lib.tui import ConnectFour
from client_lib.users import User, Users

class MessageHandler:

    def __init__(self, logger, ui: ConnectFour, sock: socket):
        self.logger = logger
        self.ui = ui
        self.sock = sock

    def handle_message(self, message):
        self.logger.debug(f'Received {message} from server')
        result = message.get("result")
        if result is not None:
            self.process_result(result, message)
        else:
            broadcast = message.get("broadcast")
            if broadcast is not None:
                self.process_broadcast(broadcast, message)


    def process_result(self, result, message):
        if result == "move":
            return
        if result == "connection":
            # Exceeds max allowed player count
            if message.get("status") == "refused":
                reason = message.get("reason")
                print(f'Can not connect to server: {reason}')


    def process_broadcast(self, broadcast, message):
        if broadcast == "state":
            state = message.get("state")
            self.handle_state(state, message)
        if broadcast == "connection_status":
            self.logger.info(f'new connection to server: host: {message.get("host")}, port {message.get("port")}')
            return
        if broadcast == "game_status":
            self.handle_game_status(message)
        if broadcast == "game_win":
            self.handle_game_win(message)
        if broadcast == "game_draw":
            self.handle_game_draw(message)

    def handle_game_draw(self, message):
        board = self.format_board(message.get("board"))
        self.ui.post_message(self.ui.DrawMessage(board))

    def handle_game_win(self, message):
        winner_host = message.get("winner_host")
        winner_port = int(message.get("winner_port"))
        board = self.format_board(message.get("board"))
        self.ui.post_message(self.ui.WinnerMessage(winner_host,winner_port,board))

    def handle_state(self, state: str, message):
        if state == "pregame":
            self.ui.post_message(self.ui.PregameMessage())
        elif state == "waiting":
            self.ui.post_message(self.ui.WaitingMessage())
        elif state == "run":
            localAddr = self.sock.getsockname()
            user0 = message.get("user0")
            user1 = message.get("user1")
            if user0.get("host") == localAddr[0] and user0.get("port") == localAddr[1]:
                local = User(True,user0.get("host"),int(user0.get("port")),user0.get("name"),int(user0.get("value")))
                remote = User(False,user1.get("host"),int(user1.get("port")),user1.get("name"),int(user1.get("value")))
            else:
                remote = User(False,user0.get("host"),int(user0.get("port")),user0.get("name"),int(user0.get("value")))
                local = User(True,user1.get("host"),int(user1.get("port")),user1.get("name"),int(user1.get("value")))
            users: Users = Users(local, remote)
            if users.local.host == message.get("first_player_host") and users.local.port == int(message.get("first_player_port")):
                users.first = users.local
            else:
                users.first = users.remote
            board = self.format_board(message.get("board"))
            self.ui.post_message(self.ui.RunMessage(users, board))

    def handle_game_status(self, message):
        turn_count = int(message.get("turn_count"))
        mover_host = message.get("expected_mover_host")
        mover_port = int(message.get("expected_mover_port"))
        board = self.format_board(message.get("board"))
        self.ui.post_message(self.ui.StatusMessage(turn_count,mover_host,mover_port,board))

    def format_board(self, board):
        self.logger.debug("in format_board")
        self.logger.debug(board)
        new_board = {}
        for loc_str, value in board.items():
            locs = loc_str.split()
            new_board[(int(locs[0]), int(locs[1]))] = int(value)
        self.logger.debug(new_board)
        return new_board





