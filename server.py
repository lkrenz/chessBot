from flask import Flask, request, jsonify
from flask_cors import CORS
from chess_engine import ChessEngine
import chess

app = Flask(__name__)

CORS(app)


engine = ChessEngine(depth=5)

@app.route('/best_move', methods=['POST'])
def best_move():
    data = request.get_json()
    fen = data['fen']

    board = chess.Board(fen)
    best_move = engine.findBestMove(board)

    return jsonify({'bestMove': best_move.uci()})


if __name__ == '__main__':
    app.run(debug=True)
