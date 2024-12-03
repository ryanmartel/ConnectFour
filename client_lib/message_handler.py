from logging import Logger
from socket import socket

from client_lib.tui import ConnectFour
from client_lib.users import User, Users

class MessageHandler:
    """Parses received messages, performs actions on the client,
    then gives responses as required"""

    def __init__(self, logger: Logger, ui: ConnectFour, sock: socket) -> None:
        self.logger = logger
        self.ui = ui
        self.sock = sock

    def handle_message(self, message: dict) -> None:
        """Base message handler that processes all mesasges that the client receives"""
        self.logger.debug(f'Received {message} from server')
        # Single message to this client from server
        result = message.get("result")
        if result is not None:
            self.process_result(result, message)
        # Broadcast message
        else:
            broadcast = message.get("broadcast")
            if broadcast is not None:
                self.process_broadcast(broadcast, message)


    def process_result(self, result: str, message: dict) -> None:
        """Message handler for single messages to this client"""
        # Response to a move message sent to server
        if result == "move":
            if message.get("move_status") == "rejected":
                self.handle_move_rejected(message)
            else:
                self.handle_move_accepted()
            return
        # Response resulting in generic error
        if result == "err":
            return
        # Connection response message
        if result == "connection":
            # Exceeds max allowed player count
            if message.get("status") == "refused":
                reason = message.get("reason")
                print(f'Can not connect to server: {reason}')


    def process_broadcast(self, broadcast: str, message: dict) -> None:
        """Message handler for braodcast messages sent by the server"""
        if broadcast == "state":
            state = message.get("state")
            if state is not None:
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

    def handle_move_accepted(self) -> None:
        """Response from server that move was accepted"""
        self.ui.post_message(self.ui.MoveMessage())

    def handle_move_rejected(self, message: dict) -> None:
        """Response from server that move was rejected. Hand error message
        over to the TUI"""
        err = message.get("error")
        self.ui.post_message(self.ui.MoveErrorMessage(err))

    def handle_game_draw(self, message: dict) -> None:
        """Message from server that the game has ended in a draw."""
        board = self.format_board(message["board"])
        self.ui.post_message(self.ui.DrawMessage(board))

    def handle_game_win(self, message: dict) -> None:
        """Message from server that a player has won the game."""
        winner_host = message.get("winner_host")
        winner_port = int(message["winner_port"])
        board = self.format_board(message["board"])
        self.ui.post_message(self.ui.WinnerMessage(winner_host,winner_port,board))

    def handle_state(self, state: str, message: dict) -> None:
        """Handle state change sent by the server"""
        if state == "pregame":
            self.ui.post_message(self.ui.PregameMessage())
        elif state == "waiting":
            # Was this a normal state change, or did the other client disconnect?
            disconnect_status = int(message["disconnect"])
            if disconnect_status == 1:
                # other client left game early
                self.ui.post_message(self.ui.WaitingMessage(True))
            else:
                # normal transition to waiting
                self.ui.post_message(self.ui.WaitingMessage(False))

        elif state == "run":
            localAddr = self.sock.getsockname()
            user0 = message["user0"]
            user1 = message["user1"]
            if user0.get("host") == localAddr[0] and user0.get("port") == localAddr[1]:
                local = User(True,user0.get("host"),int(user0.get("port")),user0.get("name"),int(user0.get("value")))
                remote = User(False,user1.get("host"),int(user1.get("port")),user1.get("name"),int(user1.get("value")))
            else:
                remote = User(False,user0.get("host"),int(user0.get("port")),user0.get("name"),int(user0.get("value")))
                local = User(True,user1.get("host"),int(user1.get("port")),user1.get("name"),int(user1.get("value")))
            users: Users = Users(local, remote)
            if users.local.host == message.get("first_player_host") and users.local.port == int(message["first_player_port"]):
                users.first = users.local
            else:
                users.first = users.remote
            board = self.format_board(message["board"])
            self.ui.post_message(self.ui.RunMessage(users, board))

    def handle_game_status(self, message: dict) -> None:
        turn_count = int(message["turn_count"])
        mover_host = message.get("expected_mover_host")
        mover_port = int(message["expected_mover_port"])
        board = self.format_board(message["board"])
        self.ui.post_message(self.ui.StatusMessage(turn_count,mover_host,mover_port,board))

    def format_board(self, board: dict) -> dict:
        """ Format the sent board into a form that is usable by the client.
        This is required because the tuple keys can not be serialized over the std 
        json library"""
        self.logger.debug("in format_board")
        self.logger.debug(board)
        new_board = {}
        for loc_str, value in board.items():
            locs = loc_str.split()
            new_board[(int(locs[0]), int(locs[1]))] = int(value)
        self.logger.debug(new_board)
        return new_board





