import json

# Requests

def connect():
    data = {
            "action": "connect",
            }
    return bytes(json.dumps(data),encoding="utf-8")

def disconnect():
    data = {
            "action": "disconnect"
            }
    return bytes(json.dumps(data),encoding="utf-8")

def ping():
    data = {
            "action": "ping"
            }
    return bytes(json.dumps(data),encoding="utf-8")

def ready():
    data = {
            "action": "ready",
            }
    return bytes(json.dumps(data),encoding="utf-8")

def move(location, current_count):
    data = {
            "action": "move",
            "location": location,
            "count": current_count
            }
    return bytes(json.dumps(data),encoding="utf-8")


