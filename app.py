from flask import Flask, render_template, request, jsonify
from chess import RemoteGame  # Ensure the path is correct
from chess_bots import *
import random

app = Flask(__name__)
game = RemoteGame()  # Instantiate the chess game
bot = bot1.get_bot_move

def maybe_bot_move():
    print("maybe_bot_move")
    print(f"ai color is {game.ai_color}")
    print(f"game.bot_enabled: {game.bot_enabled}, game.game_over: {not game.game_over}, game.turn: {game.turn == game.ai_color}, game.ai_color: {game.ai_color}")
    if game.bot_enabled and not game.game_over and game.turn == game.ai_color:
        move = None
        # Get bot_enabled safely without relying on request data
        bot_enabled = 'bot1'  # Default to bot1 if not from POST
        if request.method == 'POST':
            data = request.get_json()
            bot_enabled = data.get('bot_enabled', 'bot1')
            
        # Choose which bot to use
        current_bot = None
        if bot_enabled == 'random':
            current_bot = random_bot
        elif bot_enabled == 'bot1':
            current_bot = bot1
        elif bot_enabled == 'bot2':
            current_bot = bot2
            
        if current_bot:
            move = current_bot.get_bot_move(game)
            
        if move:
            start, end = move
            print(f"Bot move: {start} -> {end}")
            result = game.make_move(start, end)
            
            # Handle the bot's pawn promotion
            if result == "promotion_needed":
                piece_type = current_bot.handle_promotion()
                print(f"Bot promotes pawn to: {piece_type}")  # Add log
                game.promote_pawn(end, piece_type)
                # Switch turn
                game.turn = 'black' if game.turn == 'white' else 'white'
            
            game.display_board()

@app.route('/')
def home():
    print("home====================")
    maybe_bot_move()
    return render_template('chess.html',
                           bottom_color=game.bottom_color,
                           turn_color=game.turn,
                           ai_color=game.ai_color)

@app.route('/board')
def get_board():
    print("get_board====================")
    maybe_bot_move()
    print(f'board: {game.get_board()} turn_color: {game.turn}, bottom_color: {game.bottom_color}')
    return jsonify({'board': game.get_board(), 
                    'turn_color': game.turn, 
                    'bottom_color': game.bottom_color})

@app.route('/bot-mode', methods=['POST'])
def bot_mode():
    print("bot_mode====================")
    data = request.get_json()
    if data and 'bot_enabled' in data:
        game.bot_enabled = True
        maybe_bot_move()
        # Return updated board info after bot move (if any)
        return jsonify({
            'success': True,
            'board': game.get_board(),
            'turn_color': game.turn,
            'bottom_color': game.bottom_color
        })
    return jsonify(success=False), 400

@app.route('/move', methods=['POST'])
def make_move():
    print("make_move====================")
    data = request.json
    start = tuple(data.get('start'))
    end = tuple(data.get('end'))
    result = game.make_move(start, end)
    
    if result == "promotion_needed":
        return jsonify({
            'status': 'success',
            'promotion_needed': True,
            'board': game.get_board(),
            'turn_color': game.turn
        })
    elif result == "checkmate":
        winner = 'white' if game.turn == 'black' else 'black'
        return jsonify({
            'status': 'success',
            'game_over': True,
            'message': f'Checkmate! {winner.capitalize()} wins!',
            'board': game.get_board(),
            'turn_color': game.turn
        })
    elif result == "stalemate":
        return jsonify({
            'status': 'success',
            'game_over': True,
            'message': 'Stalemate!',
            'board': game.get_board(),
            'turn_color': game.turn
        })
    elif result:
        return jsonify({
            'status': 'success',
            'board': game.get_board(),
            'turn_color': game.turn
        })
    return jsonify({'status': 'invalid move'})

@app.route('/get_possible_moves', methods=['POST'])
def get_possible_moves():
    print("get_possible_moves====================")
    try:
        data = request.json
        start = tuple(data.get('start'))
        moves = game.check_valid_moves(start, game.board)
        return jsonify({'moves': moves})
    except Exception as e:
        app.logger.error("Error in /get_possible_moves: %s", e)
        return jsonify({'error': str(e)}), 500
@app.route('/restart', methods=['POST'])
def restart():
    print("restart====================")
    try:
        # Completely reset the game state
        game.restart_game()
        game.bot_enabled = False  # Reset bot status
        game.game_over = False    # Reset game over status
        
        # Reset bot options
        global bot
        bot = bot1.get_bot_move  # Reset to default bot
        
        # Get the new game state
        current_board = game.get_board()
        current_bottom_color = game.bottom_color
        current_turn = game.turn
        
        print(f"Game restarted with bottom_color: {current_bottom_color}, turn: {current_turn}")
        
        return jsonify({
            'status': 'success',
            'message': 'Game restarted!',
            'board': current_board,
            'bottom_color': current_bottom_color,
            'turn_color': current_turn,
            'bot_enabled': False  # Add bot status to response
        })
    except Exception as e:
        print(f"Error restarting game: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to restart game'
        }), 500

@app.route('/promote', methods=['POST'])
def promote():
    print("promote====================")
    data = request.json
    start = tuple(data.get('start'))
    end = tuple(data.get('end'))
    piece_type = data.get('piece_type')
    
    # Execute promotion
    result = game.handle_promotion(end, piece_type)
    if result == True or result == "bot_turn":
        response = {
            'status': 'success',
            'board': game.get_board(),
            'turn_color': game.turn
        }
        # If it's the AI's turn, trigger AI move
        if result == "bot_turn":
            maybe_bot_move()
            response['board'] = game.get_board()
            response['turn_color'] = game.turn
        return jsonify(response)
    elif result == "checkmate":
        winner = 'white' if game.turn == 'black' else 'black'
        return jsonify({
            'status': 'success',
            'game_over': True,
            'message': f'Checkmate! {winner.capitalize()} wins!',
            'board': game.get_board(),
            'turn_color': game.turn
        })
    elif result == "stalemate":
        return jsonify({
            'status': 'success',
            'game_over': True,
            'message': 'Stalemate!',
            'board': game.get_board(),
            'turn_color': game.turn
        })
    return jsonify({'status': 'invalid promotion'})

@app.route('/quit', methods=['POST'])
def quit():
    game.quit_game()
    return jsonify({'status': 'success', 'message': 'Game quit!'})

if __name__ == '__main__':
    app.run(debug=True)
