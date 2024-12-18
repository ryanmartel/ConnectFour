from typing import TypeAlias
from server_lib.users import NotEnoughUsersError, User, UserNotFoundError

class Game:
    """The server's implementation of the game being played.
    The game is managed through various states which determine what is being
    currently expected from users. The gameplay occurs in the 'run' state."""

    Address: TypeAlias = tuple[str, int]

    def __init__(self, logger, board, users):
        self.logger = logger
        self.board = board
        self.users = users
        self.state = "waiting"
        # What turn is the game on
        self.turn_count = 1
        # Who's turn is it. returns user
        self.whos_move = None
        # Who started the game user
        self.first_player = None
        # Player who won the game
        self.winner = None

    def get_turn_count(self) -> int:
        return self.turn_count

    def is_max_turn(self) -> bool:
        """At max turn count a draw will occur"""
        if self.turn_count == 42:
            return True
        return False

    def setWaiting(self) -> None:
        """Sets the game back to the waiting state. This
        is also responsible for cleaning all stateful data prior to the 
        next game"""
        self.state = "waiting"
        self.first_player = None
        self.whos_move = None
        self.board.clean()
        self.turn_count = 1
        self.winner = None
        self.users.clean_connected()
        self.logger.info("State change: waiting")

    def setPregame(self) -> None:
        """Sets the game to the pregame state to gather user's names"""
        if self.state == "waiting" and self.users.num_players() == 2:
            self.logger.info("State change: pregame")
            self.state = "pregame"
        else:
            self.logger.error(f"Invalid state change to pregame curr state: {self.state}, number of users: {self.users.num_players()}")
            raise InvalidStateTransferError
            
    def setRun(self) -> None:
        """Sets the game to the run state, starting the game. Also
        determines who the first player is at this time"""
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

    def setFinished(self, winner: User|None) -> None:
        """Ends the game. If the game is a draw, winner is set to None"""
        if self.state == "run":
            self.logger.info("State change: Finished")
            self.state = "finished"
            self.winner = winner
        else:
            self.logger.error(f"Invalid state change to finished curr state: {self.state}")

    def isFinished(self) -> bool:
        """Get if the game is in the finished state"""
        if self.state == "finished":
            return True
        return False

    def check_win_condition(self, column: int, row: int) -> bool:
        """Checks the last play to see if the game was won on this turn"""
        # Which player value are we checking
        value = self.board.get_value(column, row)
        self.logger.debug(f"value this turn {value}")
        # Only have to check diagnals and vertical if this piece placed on fouth row or higher
        if row >= 3:
            # check down
            score = 1
            rp = row - 1
            while(rp >= 0):
                if self.board.get_value(column, rp) == value:
                    score = score + 1
                    rp = rp - 1
                else:
                    break
            self.logger.debug(f"down check score: {score}")
            if score == 4:
                return True

        # Check left diagnal
        score = 1
        cp = column - 1
        rp = row - 1
        while(rp >= 0 and cp >= 0):
            if self.board.get_value(cp, rp) == value:
                score = score + 1
                rp = rp - 1
                cp = cp - 1
            else:
                break
        cp = column + 1
        rp = row + 1
        while(rp <= 5 and cp <= 6):
            if self.board.get_value(cp, rp) == value:
                score = score + 1
                rp = rp + 1
                cp = cp + 1
            else:
                break
        
        self.logger.debug(f"left diag check score: {score}")
        if score == 4:
            return True

        # Check right diagnal
        score = 1
        cp = column + 1
        rp = row - 1
        while(rp >= 0 and cp <= 6):
            if self.board.get_value(cp, rp) == value:
                score = score + 1
                rp = rp - 1
                cp = cp + 1
            else:
                break
        cp = column - 1
        rp = row + 1
        while(rp <= 5 and cp >= 0):
            if self.board.get_value(cp, rp) == value:
                score = score + 1
                rp = rp + 1
                cp = cp - 1
            else:
                break
        self.logger.debug(f"right diag check score: {score}")
        if score == 4:
            return True

        # Always have to check the horizontal condition
        score = 1
        # check left
        cp = column - 1
        while(cp >= 0):
            if self.board.get_value(cp, row) == value:
                score = score + 1
                cp = cp - 1
            else:
                break
        # check right
        cp = column + 1
        while(cp <= 6):
            if self.board.get_value(cp, row) == value:
                score = score + 1
                cp = cp + 1
            else:
                break
        self.logger.debug(f"horizontal check score: {score}")
        if score == 4:
            return True
        return False

    def move(self, addr: Address, column: int, turn_count: int) -> None:
        """Makes a move at the given column. Raises exceptions on error conditions related 
        to gameplay. On successful move, the game is checked for winning conditions and the turn
        counter is incremented"""
        try: 
            user = self.users.get_user(addr)
            if self.whos_move is not None:
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
        # Check if game won
        self.game_won = self.check_win_condition(column, row)
        if self.game_won:
            self.logger.info("Game won")
            self.setFinished(user)
        # At max turn, the game must be a draw
        elif self.is_max_turn():
            self.logger.info("Game is a Draw")
            self.setFinished(None)
        # Increment turn-count and continue game
        else:
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
