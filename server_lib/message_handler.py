from server_lib.users import *
from server_lib.users import User
from server_lib.board import Board
from server_lib.game import *

class MessageHandler:

    def __init__(self, logger, action, write_sel, clients):
        self.logger = logger
        self.board = Board(self.logger)
        self.users = Users(self.logger)
        self.game = Game(self.logger, self.board, self.users)
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
                win = self.game.check_win_condition()
                # turn_count, expected_move, board
                self.broadcast(self.action.game_status(self.game.turn_count, self.game.whos_move, self.board.board))
            if action == "set_name":
                res = self.set_name(message, self.clients.get(sock))
                self.respond(res, sock)


    # Add a new user to the users pool. Max connections 
    # should already be validated by server accept_conn
    # Called directly by server
    def new_player_connected(self, addr):
        self.users.add_user(User(addr))
        self.broadcast(self.action.connection_start(addr))
        if self.users.num_players() == 2:
            try:
                self.game.setPregame()
                self.broadcast(self.action.set_pregame())
            except InvalidStateTransferError:
                pass


    # Called directly by server
    def remove_player(self, addr):
        self.users.remove_user(addr)
        self.broadcast(self.action.connection_end(addr))
        self.game.setWaiting()

    
    def set_name(self, msg, addr):
        name = msg.get("name")
        try:
            self.users.set_user_name(addr, name)
            res = self.action.ok()
        except UserNotFoundError:
            res = self.action.err("User with this address was not found")
        self.logger.info(f"set host: {addr[0]} post: {addr[1]} name: {name}")
        if self.users.are_names_set():
            self.users.set_values()
            self.game.setRun()
            self.broadcast(self.action.set_run(self.game.first_player, self.users))
        return res

    def move(self, msg, addr):
        column = msg.get("column")
        turn_count = msg.get("turn-count")
        try:
            self.game.move(addr, int(column), int(turn_count))
            res = self.action.ok()
        except UserNotFoundError:
            res = self.action.err("User with this address was not found")
        except InvalidOrderError:
            res = self.action.err("It is not this users turn")
        except OutOfDateError:
            res = self.action.err("Stale data used for turn")
        except InvalidColumnError:
            res = self.action.err("Column out of range")
        except InvalidRowError:
            res = self.action.err("Column is full")
        except ValueError:
            res = self.action.err("Invalid value passed")
        return res

    def respond(self, msg, sock):
        if msg is not None:
            sock.sendall(msg)

    def broadcast(self, msg):
        for key, _ in self.write_sel.select(0):
            key.fileobj.send(msg)


