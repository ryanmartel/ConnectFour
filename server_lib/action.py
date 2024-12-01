import json
import struct


class Action:

    def __init__(self, logger):
        self.logger = logger

    def serialize(self, msg):
        bjson = bytes(json.dumps(msg), encoding="utf-8")
        return struct.pack(f'<i{len(bjson)}s', len(bjson), bjson)

    # Requests
    # play_count gives the current game counter. this ensures consistency in plays
    def game_status(self, turn_count, expected_mover, board):
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

    def game_win(self, board, winner):
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

    def connection_start(self, addr):
        data = {
                "broadcast": "connection_status",
                "host": addr[0],
                "port": addr[1],
                "status": "connected"
                }
        return self.serialize(data)

    def connection_end(self, addr):
        data = {
                "broadcast": "connection_status",
                "host": addr[0],
                "port": addr[1],
                "status": "closed"
                }
        return self.serialize(data)

    def player_ready(self, num_waiting_on):
        data = {
                "broadcast": "ready_status",
                "num_waiting_on": num_waiting_on
                }
        return self.serialize(data)

    def set_waiting(self):
        data = {
                "broadcast": "state",
                "state": "waiting"
                }
        return self.serialize(data)

    def set_pregame(self):
        data = {
                "broadcast": "state",
                "state": "pregame"
                }
        return self.serialize(data)

    def set_run(self, first_player, users):
        data = {
                "broadcast": "state",
                "state": "run",
                "first_player_host": first_player.host,
                "first_player_port": first_player.port,
                }
        for index, (_, user) in enumerate(users.connected_users.items()):
            data[f"user{index}"] = {
                    "host": user.host,
                    "port": user.port,
                    "name": user.name,
                    "value": user.value
                    }
        return self.serialize(data)


    def finish_game(self, winner):
        data = {
                "broadcast": "state",
                "state": "finished",
                "winner": winner
                }
        return self.serialize(data)

    # Responses

    def move(self, err):
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

    def ping(self):
        data = {
                "result": "pong"
                }
        return self.serialize(data)

    def connection_refuse(self):
        data = {
                "result": "connection",
                "status": "refused",
                }
        return self.serialize(data)

    def connection(self):
        data = {
                "result": "connection",
                "status": "connected",
                }
        return self.serialize(data)

    def ok(self):
        data = {
                "result": "ok"
                }
        return self.serialize(data)

    def err(self, err):
        data = {
                "result": "err",
                "error": err
                }
        return self.serialize(data)



