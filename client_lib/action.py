import json
from logging import Logger
import struct

class Action:
    """ Defines actions which are sent to the server. These
    actions are sent using the application message protocol, and
    define the output of the client-side Clinet/Server API"""

    def __init__(self, logger: Logger) -> None:
        self.logger = logger

    def serialize(self, msg: dict) -> bytes:
        """Create a byte serialization of the message. message contents
        are encoded in json and prefixed by a fixed size length integer to
        encode the total message size"""
        bjson = bytes(json.dumps(msg), encoding="utf-8")
        return struct.pack(f'<i{len(bjson)}s', len(bjson), bjson)

    def connect(self) -> bytes:
        """ Connection message"""
        data = {
                "action": "connect",
                }
        return self.serialize(data)

    def disconnect(self) -> bytes:
        """ Disconnect message"""
        data = {
                "action": "disconnect"
                }
        return self.serialize(data)

    def move(self, column: int, turn_count: int) -> bytes:
        """ Move message. turn-count is the current state information"""
        data = {
                "action": "move",
                "column": column,
                "turn-count": turn_count
                }
        return self.serialize(data)

    def set_name(self, user_name: str) -> bytes:
        """ Set this clients user name"""
        data = {
                "action": "set_name",
                "name": user_name
                }
        return self.serialize(data)

