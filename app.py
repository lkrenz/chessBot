from flask import Flask, jsonify, request
from flask_cors import CORS
import chess
from chess_engine import ChessEngine

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Global variables to maintain state
board = chess.Board()
engine = ChessEngine(depth=2)  # Lower depth for faster response

def board_to_dict():
    """Convert the chess board to a dictionary representation."""
    result = {}
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            # Get square name (e.g., 'a1', 'e4')
            square_name = chess.square_name(square)
            # Create piece info: color_piecetype (e.g., 'w_p' for white pawn)
            color = 'w' if piece.color == chess.WHITE else 'b'
            piece_type = piece.symbol().lower()
            result[square_name] = f"{color}_{piece_type}"
    
    # Add game state information
    result["turn"] = "white" if board.turn == chess.WHITE else "black"
    result["check"] = board.is_check()
    result["game_over"] = board.is_game_over()
    result["checkmate"] = board.is_checkmate()
    result["stalemate"] = board.is_stalemate()
    
    return result

@app.route('/api/board', methods=['GET'])
def get_board():
    """Get the current board state."""
    return jsonify(board_to_dict())

@app.route('/api/move', methods=['POST'])
def make_move():
    """Make a move on the board."""
    data = request.get_json()
    move_uci = data.get('move')
    
    try:
        move = chess.Move.from_uci(move_uci)
        if move in board.legal_moves:
            board.push(move)
            return jsonify({
                "success": True,
                "board": board_to_dict(),
                "move": move_uci
            })
        else:
            return jsonify({
                "success": False,
                "error": "Illegal move"
            }), 400
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 400

@app.route('/api/engine-move', methods=['GET'])
def get_engine_move():
    """Get a move from the chess engine."""
    if board.is_game_over():
        return jsonify({
            "success": False,
            "error": "Game is over"
        }), 400
    
    best_move = engine.find_best_move(board)
    if best_move:
        board.push(best_move)
        return jsonify({
            "success": True,
            "board": board_to_dict(),
            "move": best_move.uci()
        })
    else:
        return jsonify({
            "success": False,
            "error": "No move available"
        }), 400

@app.route('/api/reset', methods=['POST'])
def reset_game():
    """Reset the game to the initial position."""
    global board
    board = chess.Board()
    return jsonify({
        "success": True,
        "board": board_to_dict()
    })

@app.route('/api/legal-moves', methods=['GET'])
def get_legal_moves():
    """Get all legal moves for the current position."""
    moves = [move.uci() for move in board.legal_moves]
    return jsonify({
        "moves": moves
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000) 