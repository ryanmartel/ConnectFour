class Board:

    def __init__(self, logger):
        self.column_tracker = self.new_column_tracker()
        self.board = self.new_board()
        self.logger = logger

    def next_row_in_column(self, column):
        ret_row = self.column_tracker.get(column, 6)
        # Above the board height
        if ret_row == 6:
            return None
        self.column_tracker[column] = ret_row + 1
        return ret_row

    def move(self, column, row, value):
        self.logger.info(f"Making move at ({column}, {row}) => {value}")
        self.board[(column, row)] = value

    def get_value(self, column, row):
        return self.board[(column, row)]

    def clean(self):
        self.column_tracker = self.new_column_tracker()
        self.board = self.new_board()
        self.logger.info("Cleaned board")

    def new_column_tracker(self):
        return {
                0: 0,
                1: 0,
                2: 0,
                3: 0,
                4: 0,
                5: 0,
                6: 0,
                }

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
