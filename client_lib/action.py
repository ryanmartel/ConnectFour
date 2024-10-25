import json
import struct

class Action:

    def __init__(self, logger):
        self.logger = logger

    def serialize(self, msg):
        bjson = bytes(json.dumps(msg), encoding="utf-8")
        return struct.pack(f'<i{len(bjson)}s', len(bjson), bjson)

    # Requests
    def connect(self):
        data = {
                "action": "connect",
                }
        return self.serialize(data)

    def disconnect(self):
        data = {
                "action": "disconnect"
                }
        return self.serialize(data)

    def ping(self):
        data = {
                "action": "ping"
                }
        return self.serialize(data)

    def ready(self):
        data = {
                "action": "ready",
                }
        return self.serialize(data)

    def move(self, location, current_count):
        data = {
                "action": "move",
                "location": location,
                "count": current_count
                }
        return self.serialize(data)

