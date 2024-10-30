class Users:
    
    def __init__(self, logger):
        # Key: user addr
        # Value: User
        self.connected_users = {}
        self.logger = logger

    def num_players(self):
        return len(self.connected_users)


    def get_user(self, addr):
        user = self.connected_users.get(addr)
        if user is None:
            self.logger.error(f"Did not find user with host: {addr[0]}, port: {addr[1]}")
            raise UserNotFoundError
        return user

    def are_names_set(self):
        for user in self.connected_users.values():
            if not user.is_named():
                return False
        return True

    def are_values_set(self):
        for user in self.connected_users.values():
            if not user.is_valued():
                return False
        return True
    
    def add_user(self, user):
        if len(self.connected_users) == 2:
            self.logger.error(f"Attempted to add too many users!")
            raise TooManyUsersError
        self.connected_users[user.addr] = user
        self.logger.info(f"Added user host: {user.host}, port: {user.port}")

    def remove_user(self, addr):
        user = self.connected_users.pop(addr)
        if user is not None:
            self.logger.info(f"Removed user host: {user.host}, port: {user.port}")

    def set_user_name(self, addr, name):
        user = self.connected_users.get(addr)
        if user is None:
            self.logger.error(f"Did not find user with host: {addr[0]}, port: {addr[1]}")
            raise UserNotFoundError
        user.set_name(name)
            
    def set_values(self):
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

class User:

    def __init__(self, addr):
        self.addr = addr
        self.host = addr[0]
        self.port = addr[1]
        self.name = ""
        self.value = 0


    def set_name(self, name):
        self.name = name

    def set_value(self, value):
        self.value = value

    def is_named(self):
        if self.name != "":
            return True
        return False

    def is_valued(self):
        if self.value != 0:
            return True
        return False

    

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
