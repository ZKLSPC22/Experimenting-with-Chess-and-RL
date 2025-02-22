import copy


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
            if (
                not self.has_moved 
                and r2 == r1 + 2 * direction 
                and board[r1 + direction][c1] is None 
                and board[r2][c2] is None
            ):
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
                if (
                    isinstance(moved_piece, Pawn)
                    and moved_piece.color != self.color
                    and abs(prev_start[0] - prev_end[0]) == 2
                    and prev_end[0] == r1 
                    and prev_end[1] == c2
                ):
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

        if (
            (abs(r2 - r1) == 2 and abs(c2 - c1) == 1) 
            or (abs(r2 - r1) == 1 and abs(c2 - c1) == 2)
        ):
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
                if (
                    c2 == 6 
                    and board[r2][5] is None 
                    and board[r2][6] is None 
                    and not self.is_under_attack(end, board)
                ):  # Kingside
                    return True
                if (
                    c2 == 2 
                    and board[r2][1] is None 
                    and board[r2][2] is None 
                    and board[r2][3] is None
                    and not self.is_under_attack(end, board)
                ):  # Queenside
                    return True
                if self.is_under_attack(end, board):
                    return False

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
        self.backup_board = copy.deepcopy(self.board)
        self.turn = 'white'  # White moves first.
        self.game_over = False
        self.last_move = None  # Stores the last move for en passant.
        self.white_king_pos = None
        self.black_king_pos = None
        self.setup_pieces()

    def check_valid_moves(self, start, board):
        piece = board[start[0]][start[1]]
        if not isinstance(piece, Piece):
            return []
        
        valid_moves = []
        for i in range(8):
            for j in range(8):
                end = (i, j)
                print(f"checking move from {start} to {end}")
                last_move = self.last_move
                if piece.is_valid_move(start, end, board, last_move):
                    # 检查移动后是否会使国王处于被将军状态
                    temp_board = copy.deepcopy(board)
                    temp_board[end[0]][end[1]] = piece
                    temp_board[start[0]][start[1]] = None
                    if not self.is_check(piece.color, temp_board):
                        valid_moves.append(end)
        
        return valid_moves

    def all_valid_moves(self, color, board):
        color = color.replace(" ", "").lower
        if color not in ["white", "black"]:
            raise ValueError("Color must be 'black' or 'white'.")
        
        valid_moves = []
        for i in range(8):
            for j in range(8):
                start = (i,j)
                piece = board[start[0]][start[1]]
                if not isinstance(piece,Piece) or piece.color != color:
                    continue
                valid_moves.extend(self.check_valid_moves(start, board))
        
        return valid_moves


    def create_board(self):
        # Create an 8x8 board initialized with None.
        return [[None for _ in range(8)] for _ in range(8)]

    def get_board(self):
        board_state = []
        for row in self.board:
            board_row = []
            for piece in row:
                if piece is None:
                    board_row.append('.')
                else:
                    board_row.append(piece.__str__())
            board_state.append(board_row)
        return board_state

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

    # Check position not out of range
    def pos_in_range(self, pos):
        if pos is None or pos == "quit":
            return False
        r, c = pos
        return 0 <= r < 8 and 0 <= c < 8

    # Get piece at given position
    def get_piece_at(self, pos, board):
        r, c = pos
        if self.pos_in_range(pos):
            return board[r][c]
        return None

    # Handle pawn's en passant capture.
    def en_passant(self, start, end):
        print("processing En Passant")
        piece = self.backup_board[end[0]][end[1]]
        captured_row = start[0]
        captured_col = end[1]
        if (
            isinstance(piece, Pawn)
            and start[1] != end[1]
            and self.board[end[0]][end[1]] is None
            and isinstance(self.backup_board[captured_row][captured_col], Pawn)
        ):
            captured_row = start[0]
            captured_col = end[1]
            self.backup_board[captured_row][captured_col] = None
            print(f"en passant, taken {captured_row, captured_col}")
    
    # Handle castling: if the piece is a King and it moves two squares horizontally,
    # then move the associated rook.
    def castle(self, start, end):
        piece = self.backup_board[end[0]][end[1]]
        if isinstance(piece, King) and abs(end[1] - start[1]) == 2 and start[0] == end[0]:
            if end[1] == 6:  # Kingside
                rook_start = (end[0], 7)
                rook_end = (end[0], 5)
            elif end[1] == 2:  # Queenside
                rook_start = (end[0], 0)
                rook_end = (end[0], 3)

            self.backup_board[rook_end[0]][rook_end[1]] = self.backup_board[rook_start[0]][rook_start[1]]
            self.backup_board[rook_start[0]][rook_start[1]] = None

    def is_check(self, color, board):
        # Check if the king of the given color is under attack.
        king_pos = self.white_king_pos if color == 'white' else self.black_king_pos
        opponent_color = 'black' if color == 'white' else 'white'
        for r in range(8):
            for c in range(8):
                piece = board[r][c]
                if piece is not None and piece.color == opponent_color:
                    if piece.is_valid_move((r, c), king_pos, board, self.last_move):
                        return True
        return False
    
    def no_piece_can_move(self, color, board):
        for r in range(8):
            for c in range(8):
                piece = board[r][c]
                if piece is not None and piece.color == color:
                    start = (r, c)
                    for r2 in range(8):
                        for c2 in range(8):
                            end = (r2, c2)
                            # Check if the piece can legally move.
                            if piece.is_valid_move(start, end, board, self.last_move):
                                # Backup the board state.
                                backup_start = board[r][c]
                                backup_end = board[r2][c2]
                                original_white_king = self.white_king_pos
                                original_black_king = self.black_king_pos

                                # Make the move.
                                board[r2][c2] = piece
                                board[r][c] = None
                                if isinstance(piece, King):
                                    if piece.color == 'white':
                                        self.white_king_pos = (r2, c2)
                                    else:
                                        self.black_king_pos = (r2, c2)
                                # Check if the king is still in check.
                                in_check = self.is_check(color, board)
                                # Revert the move.
                                board[r][c] = backup_start
                                board[r2][c2] = backup_end
                                self.white_king_pos = original_white_king
                                self.black_king_pos = original_black_king
                                if not in_check:
                                    return False
        return True

    def is_checkmate(self, color):
        # First, if the king is not in check, it's not checkmate.
        if not self.is_check(color, self.board):
            return False

        return self.no_piece_can_move(color, self.board)
    
    def is_stalemate(self, color):
        if self.is_check(color, self.board):
            return False

        return self.no_piece_can_move(color, self.board)


    def update_king_position(self, start, end, piece):
        # If a king moves, update its stored position.
        if isinstance(piece, King):
            if piece.color == 'white':
                self.white_king_pos = end
            else:
                self.black_king_pos = end


class LocalGame(Game):
    # Converts user input into coordinates
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
    
    # Gets starting position from user input, quit if told.
    def get_start_pos(self):
        start_str = input("Enter the starting position (e.g., 'a2') or 'quit' to exit: ").strip().lower()
        if start_str == "quit":
            self.game_over = True
            return
        start_pos = self.convert_position(start_str)
        return start_pos

    # Get ending position from user input, quit if told.
    def get_end_pos(self):
        end_str = input("Enter the ending position (e.g., 'a3') or 'quit' to exit: ").strip().lower()
        if end_str == "quit":
            self.game_over = True
            return
        end_pos = self.convert_position(end_str)
        return end_pos
    
    def play_turn(self):
        start_pos = self.get_start_pos()
        end_pos = self.get_end_pos()
        
        if not self.pos_in_range(start_pos) or not self.pos_in_range(end_pos):
            print("Invalid position(s). Please try again.\n")
            return
        
        if not isinstance(self.board[start_pos[0]][start_pos[1]], Piece):
            print(f"You can't start from an empty square.")
            return

        piece = self.get_piece_at(start_pos, self.board)
        if piece is None:
            print("No piece at the starting position. Try again.\n")
            return

        if piece.color != self.turn:
            print("You can only move your own pieces. Try again.\n")
            return

        if not piece.is_valid_move(start_pos, end_pos, self.board, self.last_move):
            if isinstance(piece, King):
                print("Move would leave your king in check!")
                print("King moves into check") # Debug
                return
            print("Invalid move for that piece. Try again.\n")
            return

        # Backup the current state in case we need to revert.
        self.backup_board = copy.deepcopy(self.board)

        # Execute the move on the backup board.
        self.backup_board[end_pos[0]][end_pos[1]] = piece
        self.backup_board[start_pos[0]][start_pos[1]] = None

        self.en_passant(start_pos, end_pos)
        self.castle(start_pos, end_pos)

        # Update piece-specific state.
        if hasattr(piece, 'move'):
            piece.move(start_pos, end_pos)

        # Update king position if needed.
        self.update_king_position(start_pos, end_pos, piece)

        # Check that the move does not leave the current player's king in check.
        if self.is_check(self.turn, self.backup_board):
            print("Move would leave your king in check!")
            self.backup_board = copy.deepcopy(self.board)
            print("Move leaves king in check") # Debug
            return
        
        # Stores last move for en passant
        self.last_move = (start_pos, end_pos)
        # Make move by updating the entire board
        self.board = copy.deepcopy(self.backup_board)
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
        
        if self.is_stalemate(self.turn):
            self.display_board()
            print("Stalemate!")
            choice = input("Enter 'quit' to exit or 'restart' to start a new game: ").strip().lower()
            if choice == "restart":
                self.__init__()  # Reinitialize the game.
            else:
                self.game_over = True

    def play(self):
        while not self.game_over:
            self.display_board()
            self.play_turn()

    def local_game(self):
        while not self.game_over:
            self.display_board()


class RemoteGame(Game):
    def __init__(self):
        super().__init__()

    def make_move(self, start, end):
        """
        Attempts to make a move from 'start' to 'end'.
        'start' and 'end' are tuples (row, col).
        Returns True if the move was successful; otherwise, False.
        Also, after a valid move, if the opponent is in checkmate the game is flagged as over.
        """
        piece = self.get_piece_at(start, self.board)
        if piece is None or piece.color != self.turn:
            print(f"Invalid move: {start} to {end} by {self.turn}")
            return False

        # Validate move using piece logic (this should include normal moves, en passant, and castling checks).
        if not piece.is_valid_move(start, end, self.board, self.last_move):
            print(f"Invalid move: {start} to {end} by {self.turn}")
            return False

        # Backup the current state in case we need to revert.
        self.backup_board = copy.deepcopy(self.board)

        # Execute the move on the backup board.
        self.backup_board[end[0]][end[1]] = piece
        self.backup_board[start[0]][start[1]] = None

        self.en_passant(start, end)
        self.castle(start, end)

        # Update piece-specific state.
        if hasattr(piece, 'move'):
            piece.move(start, end)

        # Update king's position if necessary.
        self.update_king_position(start, end, piece)

        # If the move leaves the current player's king in check, revert the move.
        if self.is_check(self.turn, self.backup_board):
            print(f"{self.turn} is in check")
            self.backup_board = copy.deepcopy(self.board)
            return False
        print("no check")

        # Stores last move for en passant
        self.last_move = (start, end)
        # Make move by updating the entire board
        self.board = copy.deepcopy(self.backup_board)
        # Switch turns.
        self.turn = 'black' if self.turn == 'white' else 'white'

        # After a valid move, check if the opposing player is in checkmate.
        if self.is_checkmate(self.turn):
            self.game_over = True

        # Check if opposite player is in
        if self.is_stalemate(self.turn):
            self.game_over = True
    
        print(f"Move successful: {start} to {end} by {self.turn}")
        return True

    def restart_game(self):
        """
        Restarts the game by reinitializing the underlying Game class.
        """
        self.__init__()

    def quit_game(self):
        """
        Quits the game by flagging it as over.
        (Your Flask API can interpret this flag to stop accepting moves.)
        """
        self.game_over = True


if __name__ == "__main__":
     game = LocalGame()
     game.play()
