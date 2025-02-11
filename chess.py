class Piece:
    def __init__(self, color):
        self.color = color

    def __str__(self):
        raise NotImplementedError("Subclasses must implement __str__")

    def is_valid_move(self, start, end, board, last_move=None):
        raise NotImplementedError("Subclasses must implement is_valid_move")


class Pawn(Piece):
    def __init__(self, color):
        super().__init__(color)
        self.has_moved = False

    def __str__(self):
        return 'P' if self.color == 'white' else 'p'

    def is_valid_move(self, start, end, board, last_move=None):
        r1, c1 = start
        r2, c2 = end
        direction = -1 if self.color == "white" else 1  # White moves up (decreasing row), black moves down

        # Forward move (no capture)
        if c1 == c2:
            # One step forward
            if r2 == r1 + direction and board[r2][c2] is None:
                return True
            # Two steps forward on first move
            if (not self.has_moved and r2 == r1 + 2 * direction and 
                board[r1 + direction][c1] is None and board[r2][c2] is None):
                return True

        # Diagonal capture
        if abs(c2 - c1) == 1 and r2 == r1 + direction:
            # Normal capture
            if board[r2][c2] is not None and board[r2][c2].color != self.color:
                return True
            # En passant capture
            if last_move:
                prev_start, prev_end = last_move
                moved_piece = board[prev_end[0]][prev_end[1]]
                # Check that the enemy pawn just moved two squares and is adjacent.
                if (isinstance(moved_piece, Pawn) and 
                    moved_piece.color != self.color and 
                    abs(prev_start[0] - prev_end[0]) == 2 and 
                    prev_end[0] == r1 and prev_end[1] == c2):
                    return True

        return False

    def move(self, start, end):
        self.has_moved = True


class Rook(Piece):
    def __init__(self, color):
        super().__init__(color)
        self.has_moved = False

    def __str__(self):
        return 'R' if self.color == 'white' else 'r'

    def is_valid_move(self, start, end, board, last_move=None):
        r1, c1 = start
        r2, c2 = end

        # Must move in a straight line.
        if r1 != r2 and c1 != c2:
            return False

        # Check path clearance.
        if r1 == r2:
            step = 1 if c2 > c1 else -1
            for c in range(c1 + step, c2, step):
                if board[r1][c] is not None:
                    return False
        else:
            step = 1 if r2 > r1 else -1
            for r in range(r1 + step, r2, step):
                if board[r][c1] is not None:
                    return False

        # Cannot capture your own piece.
        if board[r2][c2] is not None and board[r2][c2].color == self.color:
            return False

        return True

    def move(self, start, end):
        self.has_moved = True


class Bishop(Piece):
    def __init__(self, color):
        super().__init__(color)
    
    def __str__(self):
        return 'B' if self.color == 'white' else 'b'
    
    def is_valid_move(self, start, end, board, last_move=None):
        r1, c1 = start
        r2, c2 = end

        if abs(r2 - r1) != abs(c2 - c1):
            return False

        row_step = 1 if r2 > r1 else -1
        col_step = 1 if c2 > c1 else -1

        r, c = r1 + row_step, c1 + col_step
        while r != r2 and c != c2:
            if board[r][c] is not None:
                return False
            r += row_step
            c += col_step

        # Cannot capture your own piece.
        if board[r2][c2] is not None and board[r2][c2].color == self.color:
            return False

        return True


class Knight(Piece):
    def __init__(self, color):
        super().__init__(color)
    
    def __str__(self):
        return 'N' if self.color == 'white' else 'n'
    
    def is_valid_move(self, start, end, board, last_move=None):
        r1, c1 = start
        r2, c2 = end

        # Cannot capture your own piece.
        if board[r2][c2] is not None and board[r2][c2].color == self.color:
            return False

        if (abs(r2 - r1) == 2 and abs(c2 - c1) == 1) or (abs(r2 - r1) == 1 and abs(c2 - c1) == 2):
            return True

        return False


class Queen(Piece):
    def __init__(self, color):
        super().__init__(color)

    def __str__(self):
        return 'Q' if self.color == 'white' else 'q'

    def is_valid_move(self, start, end, board, last_move=None):
        r1, c1 = start
        r2, c2 = end

        # Cannot capture your own piece.
        if board[r2][c2] is not None and board[r2][c2].color == self.color:
            return False

        # Diagonal move.
        if abs(r2 - r1) == abs(c2 - c1):
            row_step = 1 if r2 > r1 else -1
            col_step = 1 if c2 > c1 else -1
            r, c = r1 + row_step, c1 + col_step
            while r != r2 and c != c2:
                if board[r][c] is not None:
                    return False
                r += row_step
                c += col_step
            return True

        # Horizontal move.
        if r1 == r2:
            step = 1 if c2 > c1 else -1
            for c in range(c1 + step, c2, step):
                if board[r1][c] is not None:
                    return False
            return True

        # Vertical move.
        if c1 == c2:
            step = 1 if r2 > r1 else -1
            for r in range(r1 + step, r2, step):
                if board[r][c1] is not None:
                    return False
            return True

        return False


class King(Piece):
    def __init__(self, color):
        super().__init__(color)
        self.has_moved = False  # Added flag for castling

    def __str__(self):
        return 'K' if self.color == 'white' else 'k'

    def is_valid_move(self, start, end, board, last_move=None):
        r1, c1 = start
        r2, c2 = end

        # King moves one square in any direction.
        if abs(r2 - r1) <= 1 and abs(c2 - c1) <= 1:
            # Cannot capture your own piece.
            if board[r2][c2] is not None and board[r2][c2].color == self.color:
                return False
            # Check that the destination square is not under attack.
            if self.is_under_attack(end, board):
                return False
            return True

        # Castling.
        if not self.has_moved and (r2, c2) in [(7, 2), (7, 6), (0, 2), (0, 6)]:
            rook_col = 7 if c2 == 6 else 0  # Kingside (to column 6) or Queenside (to column 2)
            rook = board[r2][rook_col]

            if isinstance(rook, Rook) and not rook.has_moved:
                # Ensure path is clear
                if c2 == 6 and board[r2][5] is None and board[r2][6] is None:  # Kingside
                    # Additional safety checks (not in, through, or ending in check) are recommended.
                    return True
                if c2 == 2 and board[r2][1] is None and board[r2][2] is None and board[r2][3] is None:  # Queenside
                    return True

        return False

    def is_under_attack(self, square, board):
        # Check if any opponent piece can move to the given square.
        for r in range(8):
            for c in range(8):
                piece = board[r][c]
                if piece is not None and piece.color != self.color:
                    # When checking for attacks, we do not pass last_move.
                    if piece.is_valid_move((r, c), square, board):
                        return True
        return False

    def move(self, start, end):
        self.has_moved = True


class Game:
    def __init__(self):
        self.board = self.create_board()
        self.turn = 'white'  # White moves first.
        self.game_over = False
        self.last_move = None  # Stores the last move for en passant.
        self.white_king_pos = None
        self.black_king_pos = None
        self.setup_pieces()

    def create_board(self):
        # Create an 8x8 board initialized with None.
        return [[None for _ in range(8)] for _ in range(8)]

    def setup_pieces(self):
        # With convert_position mapping, row 0 is rank 8 and row 7 is rank 1.
        # White pieces belong on ranks 1 and 2 (rows 7 and 6) and black pieces on ranks 7 and 8 (rows 1 and 0).
        # White pieces:
        self.board[7] = [
            Rook('white'), Knight('white'), Bishop('white'), Queen('white'),
            King('white'), Bishop('white'), Knight('white'), Rook('white')
        ]
        self.board[6] = [Pawn('white') for _ in range(8)]
        self.white_king_pos = (7, 4)  # White king starts at e1.

        # Black pieces:
        self.board[0] = [
            Rook('black'), Knight('black'), Bishop('black'), Queen('black'),
            King('black'), Bishop('black'), Knight('black'), Rook('black')
        ]
        self.board[1] = [Pawn('black') for _ in range(8)]
        self.black_king_pos = (0, 4)  # Black king starts at e8.

        # Ensure rows 2 through 5 are empty.
        for row in range(2, 6):
            self.board[row] = [None for _ in range(8)]

    def display_board(self):
        # Display the board with ranks 8 to 1.
        for row in self.board:
            row_str = []
            for piece in row:
                row_str.append(str(piece) if piece is not None else '.')
            print(" ".join(row_str))
        print()  # Blank line for spacing.

    def convert_position(self, pos_str):
        """
        Converts a chess position (e.g., 'a2') to board indices.
        Row 0 corresponds to rank 8 and row 7 to rank 1.
        """
        pos_str = pos_str.strip().lower()
        if pos_str == "quit":
            return "quit"
        if len(pos_str) != 2:
            return None
        col, row_char = pos_str[0], pos_str[1]
        if col not in "abcdefgh" or not row_char.isdigit():
            return None
        row_num = int(row_char)
        if row_num < 1 or row_num > 8:
            return None
        row_index = 8 - row_num  # Rank 8 becomes row 0.
        col_index = ord(col) - ord('a')
        return (row_index, col_index)

    def is_valid_position(self, pos):
        if pos is None or pos == "quit":
            return False
        r, c = pos
        return 0 <= r < 8 and 0 <= c < 8

    def get_piece_at(self, pos):
        r, c = pos
        if self.is_valid_position(pos):
            return self.board[r][c]
        return None

    def is_check(self, color):
        # Check if the king of the given color is under attack.
        king_pos = self.white_king_pos if color == 'white' else self.black_king_pos
        opponent_color = 'black' if color == 'white' else 'white'
        for r in range(8):
            for c in range(8):
                piece = self.board[r][c]
                if piece is not None and piece.color == opponent_color:
                    if piece.is_valid_move((r, c), king_pos, self.board, self.last_move):
                        return True
        return False

    def is_checkmate(self, color):
        # First, if the king is not in check, it's not checkmate.
        if not self.is_check(color):
            return False

        # Try every move for every piece of the given color.
        for r in range(8):
            for c in range(8):
                piece = self.board[r][c]
                if piece is not None and piece.color == color:
                    start = (r, c)
                    for r2 in range(8):
                        for c2 in range(8):
                            end = (r2, c2)
                            # Check if the piece can legally move.
                            if piece.is_valid_move(start, end, self.board, self.last_move):
                                # Backup the board state.
                                backup_start = self.board[r][c]
                                backup_end = self.board[r2][c2]
                                original_white_king = self.white_king_pos
                                original_black_king = self.black_king_pos

                                # Make the move.
                                self.board[r2][c2] = piece
                                self.board[r][c] = None
                                if isinstance(piece, King):
                                    if piece.color == 'white':
                                        self.white_king_pos = (r2, c2)
                                    else:
                                        self.black_king_pos = (r2, c2)
                                # Check if the king is still in check.
                                in_check = self.is_check(color)
                                # Revert the move.
                                self.board[r][c] = backup_start
                                self.board[r2][c2] = backup_end
                                self.white_king_pos = original_white_king
                                self.black_king_pos = original_black_king
                                if not in_check:
                                    return False
        return True

    def update_king_position(self, start, end, piece):
        # If a king moves, update its stored position.
        if isinstance(piece, King):
            if piece.color == 'white':
                self.white_king_pos = end
            else:
                self.black_king_pos = end

    def play_turn(self):
        print(f"{self.turn.capitalize()}'s turn")
        # Get starting position.
        start_str = input("Enter the starting position (e.g., 'a2') or 'quit' to exit: ").strip().lower()
        if start_str == "quit":
            self.game_over = True
            return

        start_pos = self.convert_position(start_str)
        if start_pos == "quit":
            self.game_over = True
            return

        # Get ending position.
        end_str = input("Enter the ending position (e.g., 'a3') or 'quit' to exit: ").strip().lower()
        if end_str == "quit":
            self.game_over = True
            return

        end_pos = self.convert_position(end_str)
        if end_pos == "quit":
            self.game_over = True
            return

        if not self.is_valid_position(start_pos) or not self.is_valid_position(end_pos):
            print("Invalid position(s). Please try again.\n")
            return

        piece = self.get_piece_at(start_pos)
        if piece is None:
            print("No piece at the starting position. Try again.\n")
            return

        if piece.color != self.turn:
            print("You can only move your own pieces. Try again.\n")
            return

        if not piece.is_valid_move(start_pos, end_pos, self.board, self.last_move):
            print("Invalid move for that piece. Try again.\n")
            return

        # Backup the current state in case we need to revert.
        backup_start = self.board[start_pos[0]][start_pos[1]]
        backup_end = self.board[end_pos[0]][end_pos[1]]
        # For castling, backup the rook.
        castling_rook_backup = None
        rook_start = None
        rook_end = None

        # Execute the king's or other piece's move.
        self.board[end_pos[0]][end_pos[1]] = piece
        self.board[start_pos[0]][start_pos[1]] = None

        # Handle castling: if the piece is a King and it moves two squares horizontally,
        # then move the associated rook.
        if isinstance(piece, King) and abs(end_pos[1] - start_pos[1]) == 2:
            if end_pos[1] == 6:  # Kingside
                rook_start = (end_pos[0], 7)
                rook_end = (end_pos[0], 5)
            elif end_pos[1] == 2:  # Queenside
                rook_start = (end_pos[0], 0)
                rook_end = (end_pos[0], 3)

            castling_rook_backup = self.board[rook_start[0]][rook_start[1]]
            self.board[rook_end[0]][rook_end[1]] = self.board[rook_start[0]][rook_start[1]]
            self.board[rook_start[0]][rook_start[1]] = None

        # Handle pawn's en passant capture.
        if isinstance(piece, Pawn) and start_pos[1] != end_pos[1] and backup_end is None:
            captured_row = start_pos[0]
            captured_col = end_pos[1]
            self.board[captured_row][captured_col] = None

        # Update piece-specific state.
        if hasattr(piece, 'move'):
            piece.move(start_pos, end_pos)
        if castling_rook_backup is not None and rook_start is not None:
            rook = self.board[rook_end[0]][rook_end[1]]
            if hasattr(rook, 'move'):
                rook.move(rook_start, rook_end)

        # Update king position if needed.
        self.update_king_position(start_pos, end_pos, piece)

        # Check that the move does not leave the current player's king in check.
        if self.is_check(self.turn):
            print("Move would leave your king in check! Reverting move.\n")
            self.board[start_pos[0]][start_pos[1]] = backup_start
            self.board[end_pos[0]][end_pos[1]] = backup_end
            if castling_rook_backup is not None and rook_start is not None and rook_end is not None:
                self.board[rook_start[0]][rook_start[1]] = castling_rook_backup
                self.board[rook_end[0]][rook_end[1]] = None
            return

        self.last_move = (start_pos, end_pos)
        # Switch turns.
        self.turn = 'black' if self.turn == 'white' else 'white'

        # After switching turns, check if the new player is checkmated.
        if self.is_checkmate(self.turn):
            self.display_board()
            print("Checkmate!")
            winner = 'white' if self.turn == 'black' else 'black'
            print(f"{winner.capitalize()} wins!")
            choice = input("Enter 'quit' to exit or 'restart' to start a new game: ").strip().lower()
            if choice == "restart":
                self.__init__()  # Reinitialize the game.
            else:
                self.game_over = True

    def play(self):
        while not self.game_over:
            self.display_board()
            self.play_turn()


# if __name__ == "__main__":
#     game = Game()
#     game.play()


# Wrapping the Game class in a Flask API
# chess.py

# Assume your existing Game, Pawn, King, Rook, etc. classes are defined above.
# We now define an updated ChessGame class that wraps Game for the Flask API.

class ChessGame:
    def __init__(self):
        self.game = Game()  # Initialize the underlying game.
    
    def get_board(self):
        """
        Returns a 2D list representing the board state.
        Each element is either '.' (for an empty square) or the string representation of a piece.
        """
        board_repr = []
        for row in self.game.board:
            row_repr = []
            for piece in row:
                if piece is None:
                    row_repr.append('.')
                else:
                    row_repr.append(str(piece))
            board_repr.append(row_repr)
        return board_repr

    def make_move(self, start, end):
        """
        Attempts to make a move from 'start' to 'end'.
        'start' and 'end' are tuples (row, col).
        Returns True if the move was successful; otherwise, False.
        Also, after a valid move, if the opponent is in checkmate the game is flagged as over.
        """
        piece = self.game.get_piece_at(start)
        if piece is None or piece.color != self.game.turn:
            return False

        # Validate move using piece logic (this should include normal moves, en passant, and castling checks).
        if not piece.is_valid_move(start, end, self.game.board, self.game.last_move):
            return False

        # Backup state for potential reversion.
        backup_start = self.game.board[start[0]][start[1]]
        backup_end   = self.game.board[end[0]][end[1]]
        backup_captured = None  # For en passant capture.
        backup_rook = None      # For castling.
        rook_start = None
        rook_end   = None

        # Execute the move: move the piece.
        self.game.board[end[0]][end[1]] = piece
        self.game.board[start[0]][start[1]] = None

        # Handle en passant capture.
        # If a pawn moves diagonally into an empty square, remove the opponent pawn that moved two squares last move.
        if isinstance(piece, Pawn) and (start[1] != end[1]) and backup_end is None:
            # In our design, the captured pawn is located in the same row as the moving pawn's start.
            captured_row = start[0]
            captured_col = end[1]
            backup_captured = self.game.board[captured_row][captured_col]
            self.game.board[captured_row][captured_col] = None

        # Handle castling.
        # If a king moves two squares horizontally, also move the corresponding rook.
        if isinstance(piece, King) and abs(end[1] - start[1]) == 2:
            if end[1] == 6:  # kingside castling
                rook_start = (end[0], 7)
                rook_end   = (end[0], 5)
            elif end[1] == 2:  # queenside castling
                rook_start = (end[0], 0)
                rook_end   = (end[0], 3)
            backup_rook = self.game.board[rook_start[0]][rook_start[1]]
            self.game.board[rook_end[0]][rook_end[1]] = backup_rook
            self.game.board[rook_start[0]][rook_start[1]] = None
            if hasattr(backup_rook, 'move'):
                backup_rook.move(rook_start, rook_end)

        # Update piece-specific state.
        if hasattr(piece, 'move'):
            piece.move(start, end)

        # Update king's position if necessary.
        self.game.update_king_position(start, end, piece)

        # If the move leaves the current player's king in check, revert the move.
        if self.game.is_check(self.game.turn):
            self.game.board[start[0]][start[1]] = backup_start
            self.game.board[end[0]][end[1]] = backup_end
            if backup_rook is not None and rook_start is not None and rook_end is not None:
                self.game.board[rook_start[0]][rook_start[1]] = backup_rook
                self.game.board[rook_end[0]][rook_end[1]] = None
            if backup_captured is not None:
                self.game.board[captured_row][captured_col] = backup_captured
            return False

        # Update last move and switch turns.
        self.game.last_move = (start, end)
        self.game.turn = 'black' if self.game.turn == 'white' else 'white'

        # After a valid move, check if the opposing player is in checkmate.
        if self.is_checkmate(self.game.turn):
            self.game.game_over = True  # Flag the game as over.
        return True

    def is_checkmate(self, color):
        """
        Returns True if the player of the given color is in checkmate.
        This method simulates every possible move for the given color.
        """
        if not self.game.is_check(color):
            return False

        # For each piece of the given color, try every move.
        for r in range(8):
            for c in range(8):
                piece = self.game.board[r][c]
                if piece is not None and piece.color == color:
                    start = (r, c)
                    for r2 in range(8):
                        for c2 in range(8):
                            end = (r2, c2)
                            if piece.is_valid_move(start, end, self.game.board, self.game.last_move):
                                # Backup state.
                                backup_start = self.game.board[r][c]
                                backup_end = self.game.board[r2][c2]
                                orig_white_king = self.game.white_king_pos
                                orig_black_king = self.game.black_king_pos

                                # Make the move temporarily.
                                self.game.board[r2][c2] = piece
                                self.game.board[r][c] = None
                                if isinstance(piece, King):
                                    if color == 'white':
                                        self.game.white_king_pos = (r2, c2)
                                    else:
                                        self.game.black_king_pos = (r2, c2)
                                in_check = self.game.is_check(color)
                                # Revert move.
                                self.game.board[r][c] = backup_start
                                self.game.board[r2][c2] = backup_end
                                self.game.white_king_pos = orig_white_king
                                self.game.black_king_pos = orig_black_king
                                if not in_check:
                                    return False
        return True

    def restart_game(self):
        """
        Restarts the game by reinitializing the underlying Game class.
        """
        self.game = Game()

    def quit_game(self):
        """
        Quits the game by flagging it as over.
        (Your Flask API can interpret this flag to stop accepting moves.)
        """
        self.game.game_over = True
