from random import choice

class Game:

    def __init__(self):
        self.state = "waiting"
        self.board = self.new_board()
        self.column_tracker = {
                0: 0,
                1: 0,
                2: 0,
                3: 0,
                4: 0,
                5: 0,
                6: 0,
                }
        # Key: Addr
        # Value: Tuple(player_name, player_value)
        self.player_names = {}
        self.player_addrs = []
        self.connected_players = 0
        # What turn is the game on
        self.turn = 0
        # Who's turn is it referenced by address
        self.whos_move = None
        # Who started the game
        self.first_player = None

    def getGameState(self):
        return self.state

    def getGameStatus(self):
        return (self.board, self.turn, self.whos_move)

    def isWaiting(self):
        if self.state == "waiting":
            return True
        return False

    def isPregame(self):
        if self.state == "pregame":
            return True
        return False

    def isRunning(self):
        if self.state == "run":
            return True
        return False

    def isFinished(self):
        if self.state == "finished":
            return True
        return False
    
    def num_players(self):
        return self.connected_players

    def num_names_assigned(self):
        return len(self.player_names)

    def turn_count(self):
        return self.turn_count

    def next_player_turn(self):
        return self.whos_move

    def add_player(self, addr):
        self.player_addrs.append(addr)
        self.connected_players = self.connected_players + 1
        print(f"new number of connected players! {self.connected_players}")

    def remove_player(self, addr):
        # self.player_names.pop(addr)
        if addr in self.player_addrs:
            self.player_addrs.remove(addr)
            self.connected_players = self.connected_players - 1
        if self.player_names.get(addr) is not None:
            self.player_names.pop(addr)
        print(f"player removed... {self.connected_players}")

    def setWaiting(self):
        self.state = "waiting"

    def setPregame(self):
        if self.isWaiting() and self.num_players() == 2:
            self.state = "pregame"

    def setRun(self):
        if self.isPregame() and len(self.player_names) == 2:
            self.state = "run"
            self.first_player = choice(self.player_addrs)

    # Using address information as key, set player's name
    # Also assigns player value
    def set_player_name(self, player_name, addr):
        len_names = len(self.player_names)
        if len_names == 0:
            play_value = 1
        else:
            play_value = -1
        self.player_names[addr] = (player_name, play_value)


    def name(self, addr):
        return self.player_names.get(addr)

    def check_win_condition(self):
        return None

    # TODO: Fill in error conditions
    def move(self, addr, column, turn_count):
        if addr != self.next_player_turn:
            # It is not this player's turn'
            return "invalid_order"
        if turn_count != self.turn_count:
            # This move uses an invalid game state
            return "out_of_date"
        if column > 6 or column < 0:
            # Outside of board range
            return "invalid_column"
        row = self.next_row_in_column(column)
        if row is None:
            # row is above board height
            return "invalid_row"
        self.board[(column, row)] = self.player_names[addr][1]
        self.turn += 1
        win_res = self.check_win_condition()
        if win_res is None:
            return "success"
        return win_res
        

    # Input column is assumed to be verified by the 'move' method
    def next_row_in_column(self, column):
        ret_row = self.column_tracker.get(column, 6)
        # Above the board height
        if ret_row == 6:
            return None
        self.column_tracker[column] = ret_row + 1
        return ret_row



    def new_board(self):
        return {
                (0,0): 0,
                (0,1): 0,
                (0,2): 0,
                (0,3): 0,
                (0,4): 0,
                (0,5): 0,
                (1,0): 0,
                (1,1): 0,
                (1,2): 0,
                (1,3): 0,
                (1,4): 0,
                (1,5): 0,
                (2,0): 0,
                (2,1): 0,
                (2,2): 0,
                (2,3): 0,
                (2,4): 0,
                (2,5): 0,
                (3,0): 0,
                (3,1): 0,
                (3,2): 0,
                (3,3): 0,
                (3,4): 0,
                (3,5): 0,
                (4,0): 0,
                (4,1): 0,
                (4,2): 0,
                (4,3): 0,
                (4,4): 0,
                (4,5): 0,
                (5,0): 0,
                (5,1): 0,
                (5,2): 0,
                (5,3): 0,
                (5,4): 0,
                (5,5): 0,
                (6,0): 0,
                (6,1): 0,
                (6,2): 0,
                (6,3): 0,
                (6,4): 0,
                (6,5): 0,
                }
