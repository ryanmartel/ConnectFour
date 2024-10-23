class Game:

    def __init__(self):
        self.state = "waiting"
        self.board = self.new_board()
        self.player_names = {}
        self.player_addrs = []
        self.connected_players = 0
        # What turn is the game on
        self.turn = 0
        # Who's turn is it referenced by address
        self.whos_move = None

    def getGameState(self):
        return self.state

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

    def turn_count(self):
        return self.turn_count

    def next_player_turn(self):
        return self.whos_move

    def add_player(self, addr):
        self.player_addrs.append(addr)
        self.connected_players = self.connected_players + 1

    def remove_player(self, addr):
        self.player_names.pop(addr)
        if addr in self.player_names:
            self.player_addrs.remove(addr)
            self.connected_players = self.connected_players - 1

    def setPregame(self):
        if self.isWaiting() and self.num_players() == 2:
            self.state = "pregame"

    # Using address information as key, set player's name
    def set_player_name(self, player_name, addr):
        self.player_names[addr] = player_name

    def name(self, addr):
        return self.player_names.get(addr)

    

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
