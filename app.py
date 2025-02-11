from flask import Flask, render_template, request, jsonify
from chess import ChessGame  # Import the ChessGame wrapper from your chess.py file

app = Flask(__name__)
game = ChessGame()  # Instantiate the chess game

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/board')
def get_board():
    return jsonify({'board': game.get_board()})

@app.route('/move', methods=['POST'])
def make_move():
    data = request.json
    start = data.get('start')
    end = data.get('end')
    # Convert start and end to tuples.
    if game.make_move(tuple(start), tuple(end)):
        response = {
            'status': 'success',
            'board': game.get_board()
        }
        # If the game is over (i.e. checkmate has been detected):
        if game.game.game_over:
            # The winner is the opposite of the current turn because the turn was already switched.
            winner = 'white' if game.game.turn == 'black' else 'black'
            response['game_over'] = True
            response['message'] = f'Checkmate! {winner.capitalize()} wins!'
        return jsonify(response)
    return jsonify({'status': 'invalid move'})

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
