from flask import Flask, render_template, request, jsonify
from chess import RemoteGame  # 确保路径正确

app = Flask(__name__)
game = RemoteGame()  # 实例化国际象棋游戏

@app.route('/')
def home():
    return render_template('chess.html',
                           bottom_color=game.bottom_color,
                           turn_color=game.turn)

@app.route('/board')
def get_board():
    return jsonify({'board': game.get_board(), 
                    'turn_color': game.turn, 
                    'bottom_color': game.bottom_color})

@app.route('/bot-mode', methods=['POST'])
def bot_mode():
    data = request.get_json()
    if data and 'bot_enabled' in data:
        game.bot_enabled = bool(data['bot_enabled'])
        return jsonify(success=True)
    return jsonify(success=False), 400

@app.route('/move', methods=['POST'])
def make_move():
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
    game.restart_game()
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
