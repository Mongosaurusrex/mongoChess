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
        self.white_king_location = (7, 4)
        self.black_king_location = (0, 4)
        self.in_check = False
        self.pins = []
        self.checks = []

    """
    Takes a Move as a parameter and executes it (not working for castling and en-passant)
    """
    def make_move(self, move):
        self.board[move.start_row][move.start_column] = "--"
        self.board[move.end_row][move.end_column] = move.piece_moved
        self.move_log.append(move)  # Log the move so we can undo it later
        self.white_to_move = not self.white_to_move

        # Update the kings location if it is moved
        if move.piece_moved == "wK":
            self.white_king_location = (move.end_row, move.end_column)
        elif move.piece_moved == "bK":
            self.black_king_location = (move.end_row, move.end_column)

    """
    Undo the last move made
    """
    def undo_move(self):
        if len(self.move_log) != 0:
            move = self.move_log.pop()
            self.board[move.start_row][move.start_column] = move.piece_moved
            self.board[move.end_row][move.end_column] = move.piece_captured
            self.white_to_move = not self.white_to_move

            # Update the kings position if its undone
            if move.piece_moved == "wK":
                self.white_king_location = (move.start_row, move.start_column)
            elif move.piece_moved == "bK":
                self.black_king_location = (move.start_row, move.start_column)

    """
    All moves considering checks
    """
    def get_valid_moves(self):
        moves = []
        self.in_check, self.pins, self.checks = self.check_for_pins_and_checks()
        if self.white_to_move:
            king_row = self.white_king_location[0]
            king_col = self.white_king_location[1]
        else:
            king_row = self.black_king_location[0]
            king_col = self.black_king_location[1]
        if self.in_check:
            if len(self.checks) == 1:
                moves = self.get_all_possible_moves()
                check = self.checks[0]
                check_row = check[0]
                check_col = check[1]
                piece_thats_checking = self.board[check_row][check_col]
                valid_squares = []

                if piece_thats_checking[1] == "N":
                    valid_squares = [(check_row, check_col)]
                else:
                    for i in range(1, 8):
                        valid_square = (king_row + check[2] * i, king_col + check[3] * i)
                        valid_squares.append(valid_square)
                        if valid_square[0] == check_row and valid_square[1] == check_col:
                            break

                for i in range(len(moves) - 1, -1, -1):
                    if moves[i].piece_moved[1] != "K":
                        if not (moves[i].end_row, moves[i].end_column) in valid_squares:
                            moves.remove(moves[i])
            else:
                self.get_king_moves(king_row, king_col, moves)
        else:
            moves = self.get_all_possible_moves()

        return moves

    """
    Determine if the enemy can attack the square (row, col)
    """
    def square_under_attack(self, row, col):
        self.white_to_move = not self.white_to_move
        opponent_moves = self.get_all_possible_moves()
        self.white_to_move = not self.white_to_move
        for move in opponent_moves:
            if move.end_row == row and move.end_column == col: # Square is under attack
                return True

        return False
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
        piece_pinned = False
        pin_direction = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piece_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        if self.white_to_move:  # White pawn moves
            if self.board[row - 1][col] == "--":  # One square pawn advance
                if not piece_pinned or pin_direction == (-1, 0):
                    moves.append(Move((row, col), (row - 1, col), self.board))
                    if row == 6 and self.board[row - 2][col] == "--": # Two square pawn advance
                        moves.append(Move((row, col), (row - 2, col), self.board))
            if col - 1 >= 0:  # Captures to the left
                if self.board[row - 1][col - 1][0] == 'b':  # Enemy piece to capture
                    if not piece_pinned or pin_direction == (-1, -1):
                        moves.append(Move((row, col), (row - 1, col - 1), self.board))
            if col + 1 <= 7:  # Captures to the right
                if self.board[row - 1][col + 1][0] == 'b':  # Enemy piece to capture
                    if not piece_pinned or pin_direction == (-1, 1):
                        moves.append(Move((row, col), (row - 1, col + 1), self.board))

        else:  # Black pawn moves
            if self.board[row + 1][col] == "--":  # One square pawn advance
                if not piece_pinned or pin_direction == (1, 0):
                    moves.append(Move((row, col), (row + 1, col), self.board))
                    if row == 1 and self.board[row + 2][col] == "--":  # Two square pawn advance
                        moves.append(Move((row, col), (row + 2, col), self.board))
            if col - 1 >= 0:  # Captures to the left
                if self.board[row + 1][col - 1][0] == 'w':  # Enemy piece to capture
                    if not piece_pinned or pin_direction == (1, -1):
                        moves.append(Move((row, col), (row + 1, col - 1), self.board))
            if col + 1 <= 7:  # Captures to the right
                if self.board[row + 1][col + 1][0] == 'w':  # Enemy piece to capture
                    if not piece_pinned or pin_direction == (1, 1):
                        moves.append(Move((row, col), (row + 1, col + 1), self.board))

    """ 
    Get all the rook moves for the rook located at row, col and add these moves to the list
    """
    def get_rook_moves(self, row, col, moves):
        piece_pinned = False
        pin_direction = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piece_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                if self.board[row][col][1] != "Q":
                    self.pins.remove(self.pins[i])
                break

        directions = ((-1, 0), (0, -1), (1, 0), (0, 1))  # Horizontal movement for rook
        enemy_color = "b" if self.white_to_move else "w"
        for d in directions:
            for i in range(1, 8):
                end_row = row + d[0] * i
                end_col = col + d[1] * i
                if 0 <= end_row < 8 and 0 <= end_col < 8:  # We know that the move is on board
                    if not piece_pinned or pin_direction == d or pin_direction == (-d[0], -d[1]):
                        end_piece = self.board[end_row][end_col]
                        if end_piece == "--":  # An empty space
                            moves.append(Move((row, col), (end_row, end_col), self.board))
                        elif end_piece[0] == enemy_color:  # An enemy piece
                            moves.append(Move((row, col), (end_row, end_col), self.board))
                            break
                        else:  # Friendly piece which is invalid
                            break
                else:  # We're off the board
                    break


    """ 
    Get all the bishop moves for the bishop located at row, col and add these moves to the list
    """
    def get_bishop_moves(self, row, col, moves):
        piece_pinned = False
        pin_direction = ()
        for i in range(len(self.pins) -1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piece_pinned = True
                pin_direction = (self.pins[i][2], self.pins[3])
                self.pins.remove([self.pins[i]])
                break

        directions = ((-1, -1), (-1, 1), (1, -1), (1, 1))  # Bishop diagonals
        enemy_color = "b" if self.white_to_move else "w"
        for d in directions:
            for i in range(1, 8):
                end_row = row + d[0] * i
                end_col = col + d[1] * i
                if 0 <= end_row < 8 and 0 <= end_col < 8:  # We know that the move is on board
                    if not piece_pinned or pin_direction == d or pin_direction == (-d[0], -d[1]):
                        end_piece = self.board[end_row][end_col]
                        if end_piece == "--":  # An empty space
                            moves.append(Move((row, col), (end_row, end_col), self.board))
                        elif end_piece[0] == enemy_color:  # An enemy piece
                            moves.append(Move((row, col), (end_row, end_col), self.board))
                            break
                        else:  # Friendly piece which is invalid
                            break
                else:  # We're off the board
                    break

    """ 
    Get all the knight moves for the knight located at row, col and add these moves to the list
    """
    def get_knight_moves(self, row, col, moves):
        piece_pinned = False
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piece_pinned = True
                self.pins.remove(self.pins[i])
                break

        # The knight moves in an 'L' shaped pattern
        knight_moves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        ally_color = "w" if self.white_to_move else "b"
        for m in knight_moves:  # ...and only once
            end_row = row + m[0]
            end_col = col + m[1]
            if 0 <= end_row < 8 and 0 <= end_col < 8:  # Within bounds of the board
                if not piece_pinned:
                    end_piece = self.board[end_row][end_col]
                    if end_piece[0] != ally_color:  # We are not going to 'step on' an ally piece (empty or enemy piece)
                        moves.append(Move((row, col), (end_row, end_col), self.board))

    """ 
    Get all the queen moves for the queen located at row, col and add these moves to the list
    """
    def get_queen_moves(self, row, col, moves):
        # Essentially the queen is a bishop and rook combined
        self.get_bishop_moves(row, col, moves)
        self.get_rook_moves(row, col, moves)

    """ 
    Get all the king moves for the king located at row, col and add these moves to the list
    """
    def get_king_moves(self, row, col, moves):
        row_moves = (-1, -1, -1, 0, 0, 1, 1, 1)
        col_moves = (-1, 0, 1, -1, 1, -1, 0, 1)
        # The king moves in all directions
        king_moves = ((1, 1), (-1, 1), (1, -1), (-1, -1), (1, 0), (-1, 0), (0, 1), (0, -1))
        ally_color = "w" if self.white_to_move else "b"
        for m in king_moves:  # ...and only once
            end_row = row + m[0]
            end_col = col + m[1]
            if 0 <= end_row < 8 and 0 <= end_col < 8:  # Within bounds of the board
                end_piece = self.board[end_row][end_col]
                if end_piece[0] != ally_color:  # We are not going to 'step on' an ally piece (empty or enemy piece)
                    if ally_color == "w":
                        self.white_king_location = (end_row, end_col)
                    else:
                        self.black_king_location = (end_row, end_col)
                    in_check, pins, checks = self.check_for_pins_and_checks()

                    if not in_check:
                        moves.append(Move((row, col), (end_row, end_col), self.board))
                    if ally_color == "w":
                        self.white_king_location = (row, col)
                    else:
                        self.black_king_location = (row, col)

    """
    Returns is the player is in check, a list of pins and a list of checks
    """
    def check_for_pins_and_checks(self):
        pins = []
        checks = []
        in_check = False

        if self.white_to_move:
            enemy_color = "b"
            ally_color = "w"
            start_row = self.white_king_location[0]
            start_col = self.white_king_location[1]
        else:
            enemy_color = "w"
            ally_color = "b"
            start_row = self.black_king_location[0]
            start_col = self.black_king_location[1]

        # Check outward from king for pins and checks, keep track of pins
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1))
        for j in range(len(directions)):
            direction = directions[j]
            possible_pin = ()
            for i in range(1, 8):
                end_row = start_row + direction[0] * i
                end_col = start_col + direction[1] * i
                if 0 <= end_row < 8 and 0 <= end_col < 8:
                    end_piece = self.board[end_row][end_col]
                    if end_piece[0] == ally_color and end_piece[1] != "K":
                        if possible_pin == ():  # 1st allied piece could be pinned
                            possible_pin = (end_row, end_col, direction[0], direction[1])
                        else:  # 2nd piece is allied, so then its not a pin
                            break
                    elif end_piece[0] == enemy_color:
                        type = end_piece[1]
                        # 5 possibilities in this monster of a conditional
                        # 1.) Orthogonally away from king and piece is a rook
                        # 2.) Diagonally away from a king and piece is a bishop
                        # 3.) 1 square away diagonally from a king and piece is a pawn
                        # 4.) any direction and piece is a queen
                        # 5.) any direction 1 square away and piece is a king
                        if (0 <= j <= 3 and type == "R") or \
                            (4 <= j <= 7 and type == "B") or \
                            (i == 1 and type == "p" and ((enemy_color == "w" and 6 <= j <= 7) or (enemy_color == "b" and 4 <= j <= 5))) or \
                            (type == "Q") or \
                            (i == 1 and type == "K"):
                            if possible_pin == ():  # No piece blocking, so check
                                in_check = True
                                checks.append((end_row, end_col, direction[0], direction[1]))
                                break
                            else:  # Piece is blocking so pin
                                pins.append(possible_pin)
                                break
                        else:  # Enemy piece is not applying check
                            break

        # Check for knight checks
        knight_moves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        for m in knight_moves:
            end_row = start_row + m[0]
            end_col = start_col + m[1]
            if 0 <= end_row < 8 and 0 <= end_col <8:
                end_piece = self.board[end_row][end_col]
                if end_piece[0] == enemy_color and end_piece == "N":
                    in_check = True
                    checks.append((end_row, end_col, m[0], m[1]))

        return in_check, pins, checks

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