"""
This class is responsible for storing all the information about the current state of a chess game.
It will also be responsible for determining valid moves at the current state. It will also keep a move log.
"""


class GameState:
    def __init__(self):
        # Board is an 8x8 2d list, each element of the list has 2 characters
        # Fist character represents the color of the piece, 'b' or 'w'
        # The second character represents the type of the piece, 'K', 'Q', 'R', 'B', 'N' or 'p'
        # "--" - represents an empty space with no piece.
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"],
        ]
        self.move_functions = {"p": self.get_pawn_moves, "R": self.get_rook_moves, "N": self.get_knight_moves,
                               "B": self.get_bishop_moves, "Q": self.get_queen_moves, "K": self.get_king_moves}

        self.white_to_move = True
        self.move_log = []

    """
    Takes a Move as a parameter and executes it (not working for castling and en-passant)
    """
    def make_move(self, move):
        self.board[move.start_row][move.start_column] = "--"
        self.board[move.end_row][move.end_column] = move.piece_moved
        self.move_log.append(move)  # Log the move so we can undo it later
        self.white_to_move = not self.white_to_move

    """
    Undo the last move made
    """
    def undo_move(self):
        if len(self.move_log) != 0:
            move = self.move_log.pop()
            self.board[move.start_row][move.start_column] = move.piece_moved
            self.board[move.end_row][move.end_column] = move.piece_captured
            self.white_to_move = not self.white_to_move

    """
    All moves considering checks
    """
    def get_valid_moves(self):
        #TODO: fix check filtering on all moves
        return self.get_all_possible_moves()

    """
    All moves without considering checks
    """
    def get_all_possible_moves(self):
        moves = []
        for row in range(len(self.board)):
            for col in range(len(self.board[row])):
                turn = self.board[row][col][0]
                if (turn == 'w' and self.white_to_move) or (turn == 'b' and not self.white_to_move):
                    piece = self.board[row][col][1]
                    self.move_functions[piece](row, col, moves)

        return moves
    """
    Get all the pawn moves for the pawn located at row, col and add these moves to the list
    """
    def get_pawn_moves(self, row, col, moves):
        if self.white_to_move:  # White pawn moves
            if self.board[row - 1][col] == "--":  # One square pawn advance
                moves.append(Move((row, col), (row - 1, col), self.board))
                if row == 6 and self.board[row - 2][col] == "--": # Two square pawn advance
                    moves.append(Move((row, col), (row - 2, col), self.board))
            if col - 1 >= 0:  # Captures to the left
                if self.board[row - 1][col - 1][0] == 'b':  # Enemy piece to capture
                    moves.append(Move((row, col), (row - 1, col - 1), self.board))
            if col + 1 <= 7:  # Captures to the right
                if self.board[row - 1][col + 1][0] == 'b':  # Enemy piece to capture
                    moves.append(Move((row, col), (row - 1, col + 1), self.board))
        else:  # Black pawn moves
            if self.board[row + 1][col] == "--":  # One square pawn advance
                moves.append(Move((row, col), (row + 1, col), self.board))
                if row == 1 and self.board[row + 2][col] == "--":  # Two square pawn advance
                    moves.append(Move((row, col), (row + 2, col), self.board))
            if col - 1 >= 0:  # Captures to the left
                if self.board[row + 1][col - 1][0] == 'w':  # Enemy piece to capture
                    moves.append(Move((row, col), (row + 1, col - 1), self.board))
            if col + 1 <= 7:  # Captures to the right
                if self.board[row + 1][col + 1][0] == 'w':  # Enemy piece to capture
                    moves.append(Move((row, col), (row + 1, col + 1), self.board))

    """ 
    Get all the rook moves for the pawn located at row, col and add these moves to the list
    """
    def get_rook_moves(self, row, col, moves):
        pass

    """ 
    Get all the bishop moves for the pawn located at row, col and add these moves to the list
    """
    def get_bishop_moves(self, row, col, moves):
        pass

    """ 
    Get all the knight moves for the pawn located at row, col and add these moves to the list
    """
    def get_knight_moves(self, row, col, moves):
        pass

    """ 
    Get all the queen moves for the pawn located at row, col and add these moves to the list
    """
    def get_queen_moves(self, row, col, moves):
        pass

    """ 
    Get all the king moves for the pawn located at row, col and add these moves to the list
    """
    def get_king_moves(self, row, col, moves):
        pass


class Move:
    # Maps keys to values
    # key : value
    ranks_to_rows = {"1": 7, "2": 6, "3": 5, "4": 4,
                     "5": 3, "6": 2, "7": 1, "8": 0}
    rows_to_ranks = {v: k for k, v in ranks_to_rows.items()}
    files_to_cols = {"a": 0, "b": 1, "c": 2, "d": 3,
                     "e": 4, "f": 5, "g": 6, "h": 7}
    cols_to_files = {v: k for k, v in files_to_cols.items()}

    def __init__(self, start_square, end_square, board):
        self.start_row = start_square[0]
        self.start_column = start_square[1]
        self.end_row = end_square[0]
        self.end_column = end_square[1]
        self.piece_moved = board[self.start_row][self.start_column]
        self.piece_captured = board[self.end_row][self.end_column]
        self.move_id = self.start_row * 1000 + self.start_column * 100 + self.end_row * 10 + self.end_column

    """
    Overriding the equals method
    """
    def __eq__(self, other):
        if isinstance(other, Move):
            return self.move_id == other.move_id
        return False

    def get_chess_notation(self):
        # TODO: make this more "real" chess notation like
        return self.get_rank_file(self.start_row, self.start_column) \
               + self.get_rank_file(self.end_row, self.end_column)

    def get_rank_file(self, row, col):
        return self.cols_to_files[col] + self.rows_to_ranks[row]