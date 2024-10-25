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
    def games_status(self, game_status):
        data = {
                "broadcast": "game_status",
                }
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

    def set_pregame(self):
        data = {
                "broadcast": "state",
                "state": "pregame"
                }
        return self.serialize(data)

    def start_game(self, first_player, game_status):
        pass



    # Responses

    def move(self, status):
        data = {
                "result": "move",
                "move_status": status
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
                "err": err
                }
        return self.serialize(data)



