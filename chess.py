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
        self.has_moved = False

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
            rook_col = 7 if c2 == 6 else 0  # Kingside (6) -> rook at 7, Queenside (2) -> rook at 0
            rook = board[r2][rook_col]

            if isinstance(rook, Rook) and not rook.has_moved:
                # Ensure path is clear
                if c2 == 6 and board[r2][5] is None and board[r2][6] is None:  # Kingside
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
        if len(pos_str) != 2:
            return None
        col, row_char = pos_str[0].lower(), pos_str[1]
        if col not in "abcdefgh" or not row_char.isdigit():
            return None
        row_num = int(row_char)
        if row_num < 1 or row_num > 8:
            return None
        row_index = 8 - row_num  # Rank 8 becomes row 0.
        col_index = ord(col) - ord('a')
        return (row_index, col_index)

    def is_valid_position(self, pos):
        if pos is None:
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

    def update_king_position(self, start, end, piece):
        # If a king moves, update its stored position.
        if isinstance(piece, King):
            if piece.color == 'white':
                self.white_king_pos = end
            else:
                self.black_king_pos = end

    def play_turn(self):
        print(f"{self.turn.capitalize()}'s turn")
        start_str = input("Enter the starting position (e.g., 'a2'): ")
        end_str = input("Enter the ending position (e.g., 'a3'): ")

        start_pos = self.convert_position(start_str)
        end_pos = self.convert_position(end_str)

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

        # Execute the move.
        self.board[end_pos[0]][end_pos[1]] = piece
        self.board[start_pos[0]][start_pos[1]] = None

        # Handle pawn's en passant capture.
        if isinstance(piece, Pawn) and start_pos[1] != end_pos[1] and backup_end is None:
            # Remove the enemy pawn that moved two squares in the previous move.
            captured_row = start_pos[0]
            captured_col = end_pos[1]
            self.board[captured_row][captured_col] = None

        # Update piece-specific state (e.g. has_moved flag).
        if hasattr(piece, 'move'):
            piece.move(start_pos, end_pos)

        # Update king position if needed.
        self.update_king_position(start_pos, end_pos, piece)

        # Check that the move does not leave the current player's king in check.
        if self.is_check(self.turn):
            print("Move would leave your king in check! Reverting move.\n")
            self.board[start_pos[0]][start_pos[1]] = backup_start
            self.board[end_pos[0]][end_pos[1]] = backup_end
            # If en passant capture occurred, reverting that would require additional state handling.
            return

        self.last_move = (start_pos, end_pos)
        # Switch turns.
        self.turn = 'black' if self.turn == 'white' else 'white'

    def play(self):
        while not self.game_over:
            self.display_board()
            self.play_turn()


if __name__ == "__main__":
    game = Game()
    game.play()
