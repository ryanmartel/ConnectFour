class User:
    """A single user"""

    def __init__(self, local: bool, host: str, port: int, name: str, value: int):
        self.is_local = local
        self.host = host
        self.port = port
        self.name = name
        self.value = value

class Users:
    """Stores the client side representation of the games users"""

    def __init__(self, local_user: User, remote_user: User):
        self.local = local_user
        self.remote = remote_user
        self.first = None

    def assign_first(self, user: User):
        self.first = user

