import json
import os

class Action:

    def __init__(self, logger):
        self.logger = logger

    # Requests
    def connect(self):
        data = {
                "action": "connect",
                }
        return bytes(json.dumps(data),encoding="utf-8")

    def disconnect(self):
        data = {
                "action": "disconnect"
                }
        return bytes(json.dumps(data),encoding="utf-8")

    def ping(self):
        data = {
                "action": "ping"
                }
        return bytes(json.dumps(data),encoding="utf-8")

    def ready(self):
        data = {
                "action": "ready",
                }
        return bytes(json.dumps(data),encoding="utf-8")

    def move(self, location, current_count):
        data = {
                "action": "move",
                "location": location,
                "count": current_count
                }
        return bytes(json.dumps(data),encoding="utf-8")


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
        if result == "pong":
            return
        if result == "connection":
            # Exceeds max allowed player count
            if message.get("status") == "refused":
                self.logger.error('Too Many clients currently in game. Max allowed is 2')
                os._exit(1)


    def process_broadcast(self, broadcast, message):
        if broadcast == "gamestate":
            return
        if broadcast == "connection_status":
            print(f'new connection to server: host: {message.get("host")}, port {message.get("port")}')
            return
