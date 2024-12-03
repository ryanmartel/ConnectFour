from logging import Logger
from random import choice
from typing import TypeAlias


class User:
    """A single user connected to the game."""

    Address: TypeAlias = tuple[str, int]

    def __init__(self, addr: Address) -> None:
        self.addr = addr
        self.host = addr[0]
        self.port = addr[1]
        self.name = ""
        self.value = 0


    def set_name(self, name: str) -> None:
        """Assign user name"""
        self.name = name

    def set_value(self, value: int) -> None:
        """Assign user value"""
        self.value = value

    def is_named(self) -> bool:
        """Is this user named yet"""
        if self.name != "":
            return True
        return False

    def is_valued(self) -> bool:
        """Does this user have a value yet"""
        if self.value != 0:
            return True
        return False

class Users:
    """Manages connected users for the game."""

    Address: TypeAlias = tuple[str, int]
    
    def __init__(self, logger: Logger) -> None:
        self.connected_users = {}
        self.logger = logger

    def num_players(self) -> int:
        """ Return number of currently connected users"""
        return len(self.connected_users)


    def get_user(self, addr: Address) -> User:
        """Return the user found at this address"""
        user = self.connected_users.get(addr)
        if user is None:
            self.logger.error(f"Did not find user with host: {addr[0]}, port: {addr[1]}")
            raise UserNotFoundError
        return user

    def are_names_set(self) -> bool:
        """Check all users if their names are set"""
        for user in self.connected_users.values():
            if not user.is_named():
                return False
        return True

    def are_values_set(self) -> bool:
        """Check all users if their values are set"""
        for user in self.connected_users.values():
            if not user.is_valued():
                return False
        return True
    
    def add_user(self, user: User) -> None:
        """Add the user to connected Users. Does not allow more than two users"""
        if len(self.connected_users) == 2:
            self.logger.error(f"Attempted to add too many users!")
            raise TooManyUsersError
        self.connected_users[user.addr] = user
        self.logger.info(f"Added user host: {user.host}, port: {user.port}")

    def remove_user(self, addr: Address) -> None:
        """Remove the user from the connected users list."""
        user = self.connected_users.pop(addr)
        if user is not None:
            self.logger.info(f"Removed user host: {user.host}, port: {user.port}")

    def set_user_name(self, addr: Address, name: str):
        """Assign a user's name"""
        user = self.connected_users.get(addr)
        if user is None:
            self.logger.error(f"Did not find user with host: {addr[0]}, port: {addr[1]}")
            raise UserNotFoundError
        user.set_name(name)
            
    def set_values(self) -> None:
        """Set the values for the user. The clients use this for the color that the user is playing as"""
        if len(self.connected_users) != 2:
            self.logger.error(f"Incorect number of users during set value action. Expected 2, found {len(self.connected_users)}")
            raise NotEnoughUsersError
        curr = 1
        for user in self.connected_users.values():
            user.set_value(curr)
            if curr == 1:
                curr = -1
            else:
                curr = 1

    def first_user(self) -> User:
        """Randomly pick a user to be the first user for the game"""
        if len(self.connected_users) != 2:
            self.logger.error(f"Incorrect number of users during first user action")
            raise NotEnoughUsersError
        li = list(self.connected_users.keys())
        first_user = self.connected_users.get(choice(li))
        if first_user is None:
            self.logger.error(f"First user failed unexpectadly. None found")
            raise FailedFirstUserError
        return first_user

    def next_turn(self, old_user: User) -> User:
        """Given the last turn's user, give the next turn user"""
        addrs = list(self.connected_users.keys())
        user0 = addrs[0]
        user1 = addrs[1]
        if user0[0] != old_user.host or user0[1] != old_user.port:
            return self.connected_users[user0]
        else:
            return self.connected_users[user1]

    def clean_connected(self) -> None:
        """Cleans the connected Users list. All users names and values removed"""
        for user in self.connected_users.values():
            user.name = ""
            user.value = 0
        self.logger.info("Cleaned connected users")


    

class TooManyUsersError(Exception):
    """Raised when more than two users are attempted to be 
    added to the game"""
    pass

class UserNotFoundError(Exception):
    """Raised when a user is expected to be present, but is 
    not found in the connected list"""
    pass

class NotEnoughUsersError(Exception):
    """Expected two users to be present. Found less than
    two connected"""
    pass

class FailedFirstUserError(Exception):
    """First user selection failed. Returned None"""
    pass
