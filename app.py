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
    start = data.get('start')  # Expected to be something like [6, 4]
    end = data.get('end')      # Expected to be something like [4, 4]
    if game.make_move(tuple(start), tuple(end)):
        return jsonify({'status': 'success', 'board': game.get_board()})
    return jsonify({'status': 'invalid move'})

if __name__ == '__main__':
    app.run(debug=True)
