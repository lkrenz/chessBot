import chess
import random

class ChessEngine:
    def __init__(self, depth=2):
        """
        Initialize the chess engine.
        
        Args:
            depth (int): The depth to search in the game tree
        """
        self.depth = depth
    
    def select_move(self, board, is_white=True):
        """
        Select the best move for the given board position.
        
        Args:
            board (chess.Board): The current board position
            is_white (bool): Whether the engine is playing as white
            
        Returns:
            chess.Move: The selected move
        """
        # Simple random move selection
        legal_moves = list(board.legal_moves)
        if not legal_moves:
            return None
            
        # For now, just return a random move
        return random.choice(legal_moves)
    
    def evaluate_position(self, board):
        """
        Evaluate the current board position.
        
        Args:
            board (chess.Board): The current board position
            
        Returns:
            float: A score for the position (positive is good for white)
        """
        # Simple material counting evaluation
        if board.is_checkmate():
            # If checkmate, return a large value
            return -10000 if board.turn else 10000
        
        # Count material
        score = 0
        piece_values = {
            chess.PAWN: 1,
            chess.KNIGHT: 3,
            chess.BISHOP: 3,
            chess.ROOK: 5,
            chess.QUEEN: 9,
            chess.KING: 0  # King isn't counted in material
        }

        piece_tables = {
            chess.PAWN: pawn_mid,
            chess.KNIGHT: knight_mid,
            chess.BISHOP: bishop_mid,
            chess.ROOK: rook_mid,
            chess.QUEEN: queen_mid,
            chess.KING: king_mid
        }

        king_mid = [0, 0,  0,  0,   0,  0,  0, 0,
            0, 0,  0,  0,   0,  0,  0, 0,
            0, 0,  0,  0,   0,  0,  0, 0,
            0, 0,  0,  0,   0,  0,  0, 0,
            0, 0,  0,  0,   0,  0,  0, 0,
            0, 0,  0,  0,   0,  0,  0, 0,
            0, 0,  0, -5,  -5, -5,  0, 0,
            0, 0, 10, -5,  -5, -5, 10, 0]

queen_mid = [-20, -10, -10, -5, -5, -10, -10, -20,
        -10,   0,   0,  0,  0,   0,   0, -10,
        -10,   0,   5,  5,  5,   5,   0, -10,
        -5,   0,   5,  5,  5,   5,   0,  -5,
        -5,   0,   5,  5,  5,   5,   0,  -5,
        -10,   5,   5,  5,  5,   5,   0, -10,
        -10,   0,   5,  0,  0,   0,   0, -10,
        -20, -10, -10,  0,  0, -10, -10, -20]

rook_mid = [10,  10,  10,  10,  10,  10,  10,  10,
    10,  10,  10,  10,  10,  10,  10,  10,
        0,   0,   0,   0,   0,   0,   0,   0,
        0,   0,   0,   0,   0,   0,   0,   0,
        0,   0,   0,   0,   0,   0,   0,   0,
        0,   0,   0,   0,   0,   0,   0,   0,
        0,   0,   0,  10,  10,   0,   0,   0,
        0,   0,   0,  10,  10,   5,   0,   0]

bishop_mid = [0,   0,   0,   0,   0,   0,   0,   0,
        0,   0,   0,   0,   0,   0,   0,   0,
        0,   0,   0,   0,   0,   0,   0,   0,
        0,  10,   0,   0,   0,   0,  10,   0,
        5,   0,  10,   0,   0,  10,   0,   5,
        0,  10,   0,  10,  10,   0,  10,   0,
        0,  10,   0,  10,  10,   0,  10,   0,
        0,   0, -10,   0,   0, -10,   0,   0]

knight_mid = [-5,  -5, -5, -5, -5, -5,  -5, -5,
        -5,   0,  0, 10, 10,  0,   0, -5,
        -5,   5, 10, 10, 10, 10,   5, -5,
        -5,   5, 10, 15, 15, 10,   5, -5,
        -5,   5, 10, 15, 15, 10,   5, -5,
        -5,   5, 10, 10, 10, 10,   5, -5,
        -5,   0,  0,  5,  5,  0,   0, -5,
        -5, -10, -5, -5, -5, -5, -10, -5]

pawn_mid = [ 0,   0,   0,   0,   0,   0,   0,   0,
    30,  30,  30,  40,  40,  30,  30,  30,
    20,  20,  20,  30,  30,  30,  20,  20,
    10,  10,  15,  25,  25,  15,  10,  10,
        5,   5,   5,  20,  20,   5,   5,   5,
        5,   0,   0,   5,   5,   0,   0,   5,
        5,   5,   5, -10, -10,   5,   5,   5,
        0,   0,   0,   0,   0,   0,   0,   0]

        
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece:
                value = piece_values[piece.piece_type]
                if piece.color == chess.WHITE:
                    score += value
                else:
                    score -= value
                    
        return score

    def getPieceVal
    
    def minimax(self, board, depth, alpha=-float('inf'), beta=float('inf'), is_maximizing=True):
        """
        Minimax algorithm with alpha-beta pruning.
        
        Args:
            board (chess.Board): The current board position
            depth (int): Current depth in the search tree
            alpha (float): Alpha value for pruning
            beta (float): Beta value for pruning
            is_maximizing (bool): Whether this is a maximizing node
            
        Returns:
            float: The evaluation score for the best move
        """
        if depth == 0 or board.is_game_over():
            return self.evaluate_position(board)
            
        if is_maximizing:
            max_eval = -float('inf')
            for move in board.legal_moves:
                board.push(move)
                eval = self.minimax(board, depth - 1, alpha, beta, False)
                board.pop()
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return max_eval
        else:
            min_eval = float('inf')
            for move in board.legal_moves:
                board.push(move)
                eval = self.minimax(board, depth - 1, alpha, beta, True)
                board.pop()
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval
    
    def find_best_move(self, board):
        """
        Find the best move using minimax with alpha-beta pruning.
        
        Args:
            board (chess.Board): The current board position
            
        Returns:
            chess.Move: The best move found
        """
        best_move = None
        best_value = -float('inf')
        alpha = -float('inf')
        beta = float('inf')
        
        for move in board.legal_moves:
            board.push(move)
            board_value = self.minimax(board, self.depth - 1, alpha, beta, False)
            board.pop()
            
            if board_value > best_value:
                best_value = board_value
                best_move = move
                
            alpha = max(alpha, best_value)
            
        return best_move

# Example usage
if __name__ == "__main__":
    # Create a new board
    board = chess.Board()
    
    # Initialize the engine
    engine = ChessEngine(depth=3)
    
    # Make some random moves to get a non-starting position
    for _ in range(5):
        moves = list(board.legal_moves)
        board.push(random.choice(moves))
    
    print("Current board position:")
    print(board)
    
    # Select the best move
    best_move = engine.find_best_move(board)
    
    print(f"Best move: {best_move}")
    board.push(best_move)
    
    print("Board after best move:")
    print(board) 