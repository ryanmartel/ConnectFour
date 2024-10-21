import json

# Requests

# play_count gives the current game counter. this ensures consistency in plays
def gamestate(gamestate, play_count):
    data = {
            "broadcast": "gamestate",
            "gamestate": gamestate,
            "count": play_count
            }
    return bytes(json.dumps(data), encoding="utf-8")

def connection_start(addr):
    data = {
            "broadcast": "connection_status",
            "host": addr[0],
            "port": addr[1],
            "status": "connected"
            }
    return bytes(json.dumps(data), encoding="utf-8")

def connection_end(addr):
    data = {
            "broadcast": "connection_status",
            "host": addr[0],
            "port": addr[1],
            "status": "closed"
            }
    return bytes(json.dumps(data), encoding="utf-8")

# Responses

def move(status):
    data = {
            "result": "move",
            "move_status": status
            }
    return bytes(json.dumps(data), encoding="utf-8")

def ping():
    data = {
            "result": "pong"
            }
    return bytes(json.dumps(data), encoding="utf-8")

def handle_message(message):
    action = message["action"]
    if action is not None:
        if action == "ping":
            return ping()

