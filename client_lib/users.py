class User:
    """A single user"""

    def __init__(self, local: bool, host: str, port: int, name: str, value: int) -> None:
        self.is_local = local
        self.host = host
        self.port = port
        self.name = name
        self.value = value

class Users:
    """Stores the client side representation of the games users"""

    def __init__(self, local_user: User, remote_user: User) -> None:
        self.local = local_user
        self.remote = remote_user

    def assign_first(self, user: User) -> None:
        """Assign the first user as the given user"""
        self.first = user

    def get_mover_name(self, host: str, port: int) -> str:
        """Get the name of the next player to move"""
        if self.local.host == host and self.local.port == port:
            return self.local.name
        else:
            return self.remote.name

