from flask import Flask, render_template, request, jsonify
from chess import RemoteGame  # 确保路径正确

app = Flask(__name__)
game = RemoteGame()  # 实例化国际象棋游戏

@app.route('/')
def home():
    return render_template('chess.html')

@app.route('/board')
def get_board():
    return jsonify({'board': game.get_board()})

@app.route('/move', methods=['POST'])
def make_move():
    data = request.json
    start = tuple(data.get('start'))
    end = tuple(data.get('end'))
    if game.make_move(start, end):
        response = {
            'status': 'success',
            'board': game.get_board()
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
    data = request.json
    start = tuple(data.get('start'))
    current_color = game.turn  # 获取当前玩家的回合颜色
    moves = game.check_valid_moves(start, game.board)  # 只传递 3 个参数
    return jsonify({'moves': moves})

@app.route('/restart', methods=['POST'])
def restart():
    game.restart_game()
    return jsonify({'status': 'success', 'message': 'Game restarted!'})

@app.route('/quit', methods=['POST'])
def quit():
    game.quit_game()
    return jsonify({'status': 'success', 'message': 'Game quit!'})

if __name__ == '__main__':
    app.run(debug=True)
