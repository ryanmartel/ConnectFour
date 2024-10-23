import json


class Action:

    def __init__(self, logger, game):
        self.logger = logger
        self.game = game

    # Requests

    # play_count gives the current game counter. this ensures consistency in plays
    def gamestate(self, gamestate, play_count):
        data = {
                "broadcast": "gamestate",
                "gamestate": gamestate,
                "count": play_count
                }
        return bytes(json.dumps(data), encoding="utf-8")

    def connection_start(self, addr):
        data = {
                "broadcast": "connection_status",
                "host": addr[0],
                "port": addr[1],
                "status": "connected"
                }
        return bytes(json.dumps(data), encoding="utf-8")

    def connection_end(self, addr):
        data = {
                "broadcast": "connection_status",
                "host": addr[0],
                "port": addr[1],
                "status": "closed"
                }
        return bytes(json.dumps(data), encoding="utf-8")


    # Responses

    def move(self, status):
        data = {
                "result": "move",
                "move_status": status
                }
        return bytes(json.dumps(data), encoding="utf-8")

    def ping(self):
        data = {
                "result": "pong"
                }
        return bytes(json.dumps(data), encoding="utf-8")

    def connection_refuse(self):
        data = {
                "result": "connection",
                "status": "refused",
                }
        return bytes(json.dumps(data), encoding="utf-8")

    def connection(self):
        data = {
                "result": "connection",
                "status": "connected",
                }
        return bytes(json.dumps(data), encoding="utf-8")

    def handle_message(self, message, addr):
        action = message.get("action")
        if action is not None:
            if action == "ping":
                return self.ping()

