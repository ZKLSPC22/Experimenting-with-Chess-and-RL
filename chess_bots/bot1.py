import random

def get_bot_move(game):
    if game.turn == game.ai_color:
        moves = game.all_valid_moves(game.ai_color,game.board)
        move = random.choice(moves)
        if not moves:
            return None
        return move
    return None

def handle_promotion():
    """Handle the bot's pawn promotion"""
    return random.choice(['Q', 'R', 'B', 'N'])  # Randomly choose a promotion piece
