import json
from logging import Logger
import struct

from typing import TypeAlias

from server_lib.board import Board
from server_lib.users import User, Users


class Action:
    """ Defines actions which are sent to the client(s). These
    actions are sent using the application message protocol, and define the
    output of the server-side Client/Server API"""

    Address: TypeAlias = tuple[str, int]

    def __init__(self, logger: Logger) -> None:
        self.logger = logger

    def serialize(self, msg: dict) -> bytes:
        """Create a byte serialization of the message. message contents
        are encoded in json and prefixed by a fixed size length integer to
        encode the total message size"""
        bjson = bytes(json.dumps(msg), encoding="utf-8")
        return struct.pack(f'<i{len(bjson)}s', len(bjson), bjson)

    def game_status(self, turn_count: int, expected_mover: User, board: Board) -> bytes:
        """Sends the current gameplay status to the clients.
        Any movements made by a player other than expected or by 
        a client with a different turn count will be rejected."""
        data = {
                "broadcast": "game_status",
                "turn_count": turn_count,
                "expected_mover_host": expected_mover.host,
                "expected_mover_port": expected_mover.port,
                }
        data_board = {}
        for loc, value in board.items():
            data_board[f"{loc[0]} {loc[1]}"] = value
        data["board"] = data_board
        return self.serialize(data)

    def game_win(self, board: Board, winner: User) -> bytes:
        """Sends the game winner message to the clients"""
        data = {
                "broadcast": "game_win",
                "winner_host": winner.host,
                "winner_port": winner.port,
                }
        data_board = {}
        for loc, value in board.items():
            data_board[f"{loc[0]} {loc[1]}"] = value
        data["board"] = data_board
        return self.serialize(data)

    def game_draw(self, board: Board) -> bytes:
        """Sends the game draw message to the clients"""
        data = {
                "broadcast": "game_draw",
                "board": {}
                }
        data_board = {}
        for loc, value in board.items():
            data_board[f"{loc[0]} {loc[1]}"] = value
        data["board"] = data_board
        return self.serialize(data)


    def connection_start(self, addr: Address) -> bytes:
        """Sends notification that a new client has connected"""
        data = {
                "broadcast": "connection_status",
                "host": addr[0],
                "port": addr[1],
                "status": "connected"
                }
        return self.serialize(data)

    def connection_end(self, addr: Address) -> bytes:
        """Sends notification that a client has disconnected."""
        data = {
                "broadcast": "connection_status",
                "host": addr[0],
                "port": addr[1],
                "status": "closed"
                }
        return self.serialize(data)

    def set_waiting(self, disconnect: bool) -> bytes:
        """Sets the game state to waiting. If this was caused by a disconnection
        the disconnect field will be 1. otherwise it is 0"""
        data = {
                "broadcast": "state",
                "state": "waiting",
                "disconnect": 0
                }
        if disconnect:
            data["disconnect"] = 1
        return self.serialize(data)

    def set_pregame(self) -> bytes:
        """Sets the game state to pregame"""
        data = {
                "broadcast": "state",
                "state": "pregame"
                }
        return self.serialize(data)

    def set_run(self, first_player: User, users: Users, board: Board) -> bytes:
        """Sets the game state to run. gives first player expected information and
        all connected users information."""
        data = {
                "broadcast": "state",
                "state": "run",
                "first_player_host": first_player.host,
                "first_player_port": first_player.port,
                "board": {},
                }
        for index, (_, user) in enumerate(users.connected_users.items()):
            data[f"user{index}"] = {
                    "host": user.host,
                    "port": user.port,
                    "name": user.name,
                    "value": user.value
                    }
        data_board = {}
        for loc, value in board.items():
            data_board[f"{loc[0]} {loc[1]}"] = value
        data["board"] = data_board
        return self.serialize(data)

    def move(self, err: str|None) -> bytes:
        """The response to a client for making a move.
        The rejected move message is used to pass error information to
        the client to indicate the reason for failed move."""
        if err is None:
            data = {
                    "result": "move",
                    "move_status": "accepted"
                    }
        else:
            data = {
                    "result": "move",
                    "move_status": "rejected",
                    "error": err
                    }
        return self.serialize(data)

    def connection_refuse(self, reason: str) -> bytes:
        """Connection refused response and reason for refusal"""
        data = {
                "result": "connection",
                "status": "refused",
                "reason": reason
                }
        return self.serialize(data)

    def connection(self) -> bytes:
        """Connection connected sucessfully response"""
        data = {
                "result": "connection",
                "status": "connected",
                }
        return self.serialize(data)

    def ok(self) -> bytes:
        """Generic Ok response message"""
        data = {
                "result": "ok"
                }
        return self.serialize(data)

    def err(self, err: str) -> bytes:
        """Generic Error response message"""
        data = {
                "result": "err",
                "error": err
                }
        return self.serialize(data)



