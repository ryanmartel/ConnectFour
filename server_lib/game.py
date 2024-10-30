from random import choice

class Game:

    def __init__(self, logger, board, users):
        self.logger = logger
        self.state = "waiting"
        self.board = board
        self.users = users
        # What turn is the game on
        self.turn_count = 0
        # Who's turn is it referenced by address
        self.whos_move = None
        # Who started the game
        self.first_player = None

    def get_turn_count(self):
        return self.turn_count

    def next_player_turn(self):
        return self.whos_move

    def setWaiting(self):
        self.state = "waiting"

    def setPregame(self):
        if self.isWaiting() and self.num_players() == 2:
            self.state = "pregame"

    def setRun(self):
        if self.isPregame() and len(self.player_names) == 2:
            self.state = "run"
            self.first_player = choice(self.player_addrs)

    def check_win_condition(self):
        return None

    # TODO: Fill in error conditions
    def move(self, addr, column, turn_count):
        user = self.users.get_user(addr)
        if addr != self.next_player_turn:
            # It is not this player's turn'
            self.logger.error("Not this players turn")
            raise InvalidOrderError
        if turn_count != self.turn_count:
            # This move uses an invalid game state
            self.logger.error("Invalid game state used")
            raise OutOfDateError
        if column > 6 or column < 0:
            # Outside of board range
            self.logger.error(f"Invalid column: {column}")
            raise InvalidColumnError
        row = self.next_row_in_column(column)
        if row is None:
            # row is above board height
            self.logger.error("Invalid row")
            raise InvalidRowError
        self.board[(column, row)] = self.player_names[addr][1]
        self.turn_count += 1
        win_res = self.check_win_condition()
        if win_res is None:
            return "success"
        return win_res



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
