import chess
import random

# Piece position evaluation tables
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

pawn_mid = [0,   0,   0,   0,   0,   0,   0,   0,
    30,  30,  30,  40,  40,  30,  30,  30,
    20,  20,  20,  30,  30,  30,  20,  20,
    10,  10,  15,  25,  25,  15,  10,  10,
    5,   5,   5,  20,  20,   5,   5,   5,
    5,   0,   0,   5,   5,   0,   0,   5,
    5,   5,   5, -10, -10,   5,   5,   5,
    0,   0,   0,   0,   0,   0,   0,   0]

random.seed(42)


class ChessEngine:
    def __init__(self, depth=5):
        """
        Initialize the chess engine.
        
        Args:
            depth (int): The depth to search in the game tree
        """
        self.depth = depth
        self.transposition_table = {}

        self.zobrist_table = {
            (piece_type, color, square): random.getrandbits(64)
            for piece_type in range(1, 7)  # PAWN to KING
            for color in [chess.WHITE, chess.BLACK]
            for square in chess.SQUARES
        }

        self.zobrist_side = random.getrandbits(64)
        self.zobrist_castling = {
            flag: random.getrandbits(64)
            for flag in range(16)  # 4 castling rights = 2^4 = 16 combos
        }
        self.zobrist_ep = {
            square: random.getrandbits(64)
            for square in range(64)
        }

    def compute_zobrist_hash(self, board):
        """
        Return a 64‑bit Zobrist hash for *board*.

        • python‑chess ≥ 1.8:  board.transposition_key()  (incremental, fast)  
        • older versions:      hash(board._transposition_key())  (still OK)
        """
        try:
            return board.transposition_key()          # correct spelling
        except AttributeError:
            # Legacy fallback – one XOR away from the same value.
            return hash(board._transposition_key())   # :contentReference[oaicite:0]{index=0}



    
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
            chess.PAWN: 100,
            chess.KNIGHT: 320,
            chess.BISHOP: 330,
            chess.ROOK: 500,
            chess.QUEEN: 900,
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
        
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece:
                value = piece_values[piece.piece_type]
                # Use piece tables to evaluate position
                table = piece_tables[piece.piece_type]
                index = square if piece.color == chess.WHITE else chess.square_mirror(square)
                score += table[index]
                if piece.color == chess.BLACK:
                    score += value
                else:
                    score -= value
        return score

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

        key = self.compute_zobrist_hash(board)
        if key in self.transposition_table:
            entry = self.transposition_table[key]
            if entry["depth"] >= depth:
                return entry["value"]

        

        if depth == 0 or board.is_game_over():
            score = self.evaluate_position(board)
            self.transposition_table[key] = {"depth": depth, "value": score}
            return score
            
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
            self.transposition_table[key] = {"depth": depth, "value": max_eval}
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
            self.transposition_table[key] = {"depth": depth, "value": min_eval}
            return min_eval
    # def quiesce(self, board, alpha, beta):
    #     currentPosition = self.evaluate_position(board);

    #     if (currentPosition >= beta):
    #         return beta
    #     if (alpha < currentPosition):
    #         alpha = currentPosition

    #     for move in board.legal_moves:
    #         if (board.is_capture)

    def order_moves(self, board):
        captures = []
        non_captures = []
        for move in board.legal_moves:
            if board.is_capture(move):
                captures.append(move)
            else:
                non_captures.append(move)
        return captures + non_captures

    def find_best_move(self, board):
        """
        Find the best move using minimax with alpha-beta pruning.
        
        Args:
            board (chess.Board): The current board position
            
        Returns:
            chess.Move: The best move found
        """
        self.transposition_table.clear()
        best_move = None
        best_value = -float('inf')
        alpha = -float('inf')
        beta = float('inf')
        moves = self.order_moves(board)

        
        for move in moves:
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
    engine = ChessEngine(depth=5)
    

    #0 represents white, 1 represents black
    currentPlayer = 0;
    while not board.is_game_over():
        if currentPlayer == 0:
            print("Current board position:")
            print(board)
            # Human move loops until a valid move is entered
            while True:
                human_move_str = input("Enter your move (e.g., 'e2e4'): ")
                try:
                    # Convert the string to a Move object
                    human_move_obj = chess.Move.from_uci(human_move_str)
                    
                    if human_move_obj in board.legal_moves:
                        board.push(human_move_obj)
                        break
                    else:
                        print("Invalid move. Try again.")
                        continue
                except ValueError:
                    # If the string cannot be parsed as a UCI move, prompt again
                    print("Invalid move format. Try again.")
                    continue

        else:
            # Computer move
            best_move = engine.find_best_move(board)
            board.push(best_move)

        currentPlayer = 1 - currentPlayer

    if board.is_checkmate():
        print("Checkmate! Game over.")
    elif board.is_stalemate():
        print("Stalemate! Game over.")
    else:
        print("Game over. It's a draw.")
    
    print("Current board position:")
    print(board)
    
    # Select the best move
    best_move = engine.find_best_move(board)
    
    print(f"Best move: {best_move}")
    board.push(best_move)
    
    print("Board after best move:")
    print(board) 