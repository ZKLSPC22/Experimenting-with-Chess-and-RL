from flask import Flask, render_template, request, jsonify
from chess import RemoteGame  # 确保路径正确
from chess_bots import *

app = Flask(__name__)
game = RemoteGame()  # 实例化国际象棋游戏
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
        if bot_enabled == 'random':
            move = random_bot.get_bot_move(game)
        elif bot_enabled == 'bot1':
            move = bot1.get_bot_move(game)
        elif bot_enabled == 'bot2':
            move = bot2.get_bot_move(game)
        if move:
            start, end = move
            print(f"Bot move: {start} -> {end}")
            game.make_move(start, end)
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
    if game.make_move(start, end):
        response = {
            'status': 'success',
            'board': game.get_board(),
            'turn_color': game.turn
        }
        if game.game_over:
            if game.is_checkmate(game.turn):
                winner = 'white' if game.turn == 'black' else 'black'
                response['game_over'] = True
                response['message'] = f'Checkmate! {winner.capitalize()} wins!'
            elif game.is_stalemate(game.turn):
                response['game_over'] = True
                response['message'] = 'Stalemate!'
        return jsonify(response)
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
    game.restart_game()
    maybe_bot_move()
    return jsonify({
        'status': 'success',
        'message': 'Game restarted!',
        'board': game.get_board(),          # Add board here if needed
        'bottom_color': game.bottom_color,
        'turn_color': game.turn
    })

@app.route('/quit', methods=['POST'])
def quit():
    game.quit_game()
    return jsonify({'status': 'success', 'message': 'Game quit!'})

if __name__ == '__main__':
    app.run(debug=True)
