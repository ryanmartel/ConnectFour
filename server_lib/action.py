import json


class Action:

    def __init__(self, logger):
        self.logger = logger

    def serialize(self, msg):
        return bytes(json.dumps(msg), encoding="utf-8")

    # Requests
    # play_count gives the current game counter. this ensures consistency in plays
    def gamestate(self, gamestate, play_count):
        data = {
                "broadcast": "gamestate",
                "gamestate": gamestate,
                "count": play_count
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



