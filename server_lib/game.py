from server_lib.users import NotEnoughUsersError, UserNotFoundError

class Game:

    def __init__(self, logger, board, users):
        self.logger = logger
        self.board = board
        self.users = users
        self.state = "waiting"
        # What turn is the game on
        self.turn_count = 0
        # Who's turn is it. returns user
        self.whos_move = None
        # Who started the game user
        self.first_player = None

    def get_turn_count(self):
        return self.turn_count

    def setWaiting(self):
        self.state = "waiting"
        self.first_player = None
        self.whos_move = None
        self.board.clean()
        self.users.clean_connected()
        self.logger.info("State change: waiting")

    def setPregame(self):
        if self.state == "waiting" and self.users.num_players() == 2:
            self.logger.info("State change: pregame")
            self.state = "pregame"
        else:
            self.logger.error(f"Invalid state change to pregame curr state: {self.state}, number of users: {self.users.num_players()}")
            raise InvalidStateTransferError
            
    def setRun(self):
        if self.state == "pregame" and self.users.are_names_set():
            self.logger.info("State change: run")
            self.state = "run"
            try:
                self.first_player = self.users.first_user()
                self.logger.debug(f"First player set as {self.first_player.host}, {self.first_player.port}")
                self.whos_move = self.first_player
            except NotEnoughUsersError:
                self.logger.error(f"Invalid state change to run")
                raise InvalidStateTransferError
        else:
            self.logger.error(f"Invalid state change to run curr state: {self.state}")
            raise InvalidStateTransferError

    def check_win_condition(self):
        return False

    # TODO: Fill in error conditions
    def move(self, addr, column, turn_count):
        try: 
            user = self.users.get_user(addr)
            self.logger.debug(f"Who's move: {self.whos_move.host}, {self.whos_move.port}")
        except UserNotFoundError:
            raise UserNotFoundError
        if user != self.whos_move:
            # It is not this player's turn'
            self.logger.error("Not this players turn")
            raise InvalidOrderError
        if turn_count != self.turn_count:
            # This move uses an invalid game state
            self.logger.error(f"Invalid game state used, got {turn_count}, expected {self.turn_count}")
            raise OutOfDateError
        if column > 6 or column < 0:
            # Outside of board range
            self.logger.error(f"Invalid column: {column}")
            raise InvalidColumnError
        row = self.board.next_row_in_column(column)
        if row is None:
            # row is above board height
            self.logger.error("Invalid row")
            raise InvalidRowError
        self.board.move(column, row, user.value)
        self.turn_count += 1
        self.whos_move = self.users.next_turn(user)
        self.logger.info(f"expecting host: {self.whos_move.host}, port: {self.whos_move.port} to play next")


class InvalidStateTransferError(Exception):
    """Pre-conditions not met for attempted state transfer"""
    pass

class InvalidOrderError(Exception):
    """This turn occured out of expected turn order"""
    pass

class OutOfDateError(Exception):
    """This turn used an old game state"""
    pass

class InvalidColumnError(Exception):
    """Invalid column selection"""
    pass

class InvalidRowError(Exception):
    """This Column is full"""
    pass
