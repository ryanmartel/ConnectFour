class Game:

    def __init__(self, local_value):
        self.game_active = True;
        self.state = 0
        self.board = self.new_board()
        self.local_value = local_value

    # returns the current game counter on move. This ensures the total count 
    # can be verified by the server
    def local_move(self, location):
        if not self.game_active or self.board[location] != 0:
            return (location, -1);
        return (location, self.state);

    def update_game(self, board, state):
        self.board = board
        self.state = state

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
