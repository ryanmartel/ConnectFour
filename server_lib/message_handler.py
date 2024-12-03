from logging import Logger
from typing import TypeAlias
from selectors import DefaultSelector
from socket import socket
from server_lib.action import Action
from server_lib.users import *
from server_lib.users import User
from server_lib.board import Board
from server_lib.game import *

class MessageHandler:
    """Parses received messages, performs actions on game,
    then gives responses or broadcasts as required"""

    Address: TypeAlias = tuple[str, int]

    def __init__(self, logger: Logger, action: Action, write_sel: DefaultSelector, clients: dict[socket, Address]) -> None:
        self.logger = logger
        self.board = Board(self.logger)
        self.users = Users(self.logger)
        self.game = Game(self.logger, self.board, self.users)
        self.action = action
        self.write_sel = write_sel
        self.clients = clients

    def handle_message(self, message: dict, sock: socket) -> None:
        """Base message handler that processes all messages that the server receives"""
        action = message.get("action")
        if action is not None:
            if action == "move":
                addr = self.clients.get(sock)
                if addr is not None:
                    res = self.move(message, addr)
                    # Move was successfull.
                    if res is None:
                        self.broadcast(self.action.move(None))
                    # Move caused an error that should be returned to client
                    else:
                        self.respond(res, sock)
                    # Game reachec an end-state
                    if self.game.isFinished():
                        winning_user = self.game.winner
                        # Must be a draw
                        if winning_user is None:
                            self.logger.debug("HIT draw")
                            self.broadcast(self.action.game_draw(self.board))
                        # There is a winner
                        else:
                            self.broadcast(self.action.game_win(self.board, winning_user))
                    # Play continues, ensure clients have up to date status
                    else:
                        if self.game.whos_move is not None:
                            self.broadcast(self.action.game_status(self.game.turn_count, self.game.whos_move, self.board))
            # Pregame, name setting
            if action == "set_name":
                addr = self.clients.get(sock)
                if addr is not None:
                    res = self.set_name(message, addr)
                    self.respond(res, sock)


    def new_player_connected(self, addr: Address) -> None:
        """Add a new user to the users pool. Max connections
        is already validated by the server accept_conn.

        CALLED DIRECTLY BY SERVER
        """

        self.users.add_user(User(addr))
        self.broadcast(self.action.connection_start(addr))
        if self.users.num_players() == 2:
            try:
                self.game.setPregame()
                self.broadcast(self.action.set_pregame())
            except InvalidStateTransferError:
                pass

    def game_finished(self) -> bool:
        """Is the current game finished, yet.
        Convenience wrapper"""
        if self.game.isFinished():
            return True
        return False

    def remove_player(self, addr: Address) -> None:
        """Removes the player on disconnection. If the disconnection
        was unexpected (during a game) then set_waiting is called with True
        to signal the early disconnect.

        CALLED DIRECTLY BY SERVER"""
        self.users.remove_user(addr)
        self.broadcast(self.action.connection_end(addr))
        if not self.game.isFinished():
            self.game.setWaiting()
            self.broadcast(self.action.set_waiting(True))
        else:
            if self.users.num_players() == 0:
                self.game.setWaiting()
                self.broadcast(self.action.set_waiting(False))

    
    def set_name(self, msg: dict, addr: Address) -> bytes:
        """Called when a player sets their name, once
        both users complete this the game is immediately started"""
        name = msg.get("name")
        try:
            if name is not None:
                self.users.set_user_name(addr, name)
                res = self.action.ok()
            else:
                res = self.action.err("Failed to set user name")
        except UserNotFoundError:
            res = self.action.err("User with this address was not found")
        self.logger.info(f"set host: {addr[0]} post: {addr[1]} name: {name}")
        if self.users.are_names_set():
            self.users.set_values()
            self.game.setRun()
            if self.game.first_player is not None:
                self.broadcast(self.action.set_run(self.game.first_player, self.users, self.board))
        return res

    def move(self, msg: dict, addr: Address) -> bytes|None:
        """Move message received from client. Make the move on the game, and report any errors to 
        the client"""
        column = msg.get("column")
        turn_count = msg.get("turn-count")
        try:
            if column is not None and turn_count is not None:
                self.game.move(addr, int(column), int(turn_count))
            res = None
        except UserNotFoundError:
            res = self.action.move("User with this address was not found")
        except InvalidOrderError:
            res = self.action.move("It is not your turn")
        except OutOfDateError:
            res = self.action.move("Stale data used for turn, try again.")
        except InvalidColumnError:
            res = self.action.move("Column out of range")
        except InvalidRowError:
            res = self.action.move("Column is full")
        except ValueError:
            res = self.action.move("Invalid value passed")
        return res

    def respond(self, msg: bytes, sock: socket) -> None:
        """Respond to client who sent the message"""
        if msg is not None:
            sock.sendall(msg)

    def broadcast(self, msg: bytes) -> None:
        """Broadcast message to all clients"""
        for key, _ in self.write_sel.select(0):
            key.fileobj.send(msg)


