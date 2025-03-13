import random

def get_bot_move(game):
    if game.turn == game.ai_color:
        moves = game.all_valid_moves(game.ai_color,game.board)
        move = random.choice(moves)
        if not moves:
            return None
        return move
    return None