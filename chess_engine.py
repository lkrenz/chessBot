import chess
import chess.polyglot 
import random
import time

# Piece square tables
king_mid = [0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, -5, -5, -5, 0, 0,
            0, 0, 10, -5, -5, -5, 10, 0]

queen_mid = [-20, -10, -10, -5, -5, -10, -10, -20,
             -10, 0, 0, 0, 0, 0, 0, -10,
             -10, 0, 5, 5, 5, 5, 0, -10,
             -5, 0, 5, 5, 5, 5, 0, -5,
             -5, 0, 5, 5, 5, 5, 0, -5,
             -10, 5, 5, 5, 5, 5, 0, -10,
             -10, 0, 5, 0, 0, 0, 0, -10,
             -20, -10, -10, 0, 0, -10, -10, -20]

rook_mid = [10, 10, 10, 10, 10, 10, 10, 10,
            10, 10, 10, 10, 10, 10, 10, 10,
            0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 10, 10, 0, 0, 0,
            0, 0, 0, 10, 10, 5, 0, 0]

bishop_mid = [0, 0, 0, 0, 0, 0, 0, 0,
              0, 0, 0, 0, 0, 0, 0, 0,
              0, 0, 0, 0, 0, 0, 0, 0,
              0, 10, 0, 0, 0, 0, 10, 0,
              5, 0, 10, 0, 0, 10, 0, 5,
              0, 10, 0, 10, 10, 0, 10, 0,
              0, 10, 0, 10, 10, 0, 10, 0,
              0, 0, -10, 0, 0, -10, 0, 0]

knight_mid = [-5, -5, -5, -5, -5, -5, -5, -5,
              -5, 0, 0, 10, 10, 0, 0, -5,
              -5, 5, 10, 10, 10, 10, 5, -5,
              -5, 5, 10, 15, 15, 10, 5, -5,
              -5, 5, 10, 15, 15, 10, 5, -5,
              -5, 5, 10, 10, 10, 10, 5, -5,
              -5, 0, 0, 5, 5, 0, 0, -5,
              -5, -10, -5, -5, -5, -5, -10, -5]

pawn_mid = [0, 0, 0, 0, 0, 0, 0, 0,
            30, 30, 30, 40, 40, 30, 30, 30,
            20, 20, 20, 30, 30, 30, 20, 20,
            10, 10, 15, 25, 25, 15, 10, 10,
            5, 5, 5, 20, 20, 5, 5, 5,
            5, 0, 0, 5, 5, 0, 0, 5,
            5, 5, 5, -10, -10, 5, 5, 5,
            0, 0, 0, 0, 0, 0, 0, 0]

# Set random seed for testing purposes
random.seed(42)


class ChessEngine:

    # presets values for piece exchanges
    mvvLvaScore = [[0]*7 for _ in range(7)]
    for victim in range(1, 7):
        for attacker in range(1, 7):
            mvvLvaScore[victim][attacker] = 10_000 * victim - attacker

    # Preset values for pieces
    pieceValues = {
        chess.PAWN: 100,
        chess.KNIGHT: 320,
        chess.BISHOP: 330,
        chess.ROOK: 500,
        chess.QUEEN: 900,
        chess.KING: 0,
    }

    pieceTables = {
        chess.PAWN: pawn_mid,
        chess.KNIGHT: knight_mid,
        chess.BISHOP: bishop_mid,
        chess.ROOK: rook_mid,
        chess.QUEEN: queen_mid,
        chess.KING: king_mid,
    }

    # Innitializes a new chessBot
    def __init__(self, depth=5, bookPath="Perfect2023.bin"):
        self.depth = depth
        self.transpositionTable: dict[int, dict] = {}

        # Instantiates zobrist hashing
        self.zobristTable = {
            (piece_type, color, square): random.getrandbits(64)
            for piece_type in range(1, 7)
            for color in [chess.WHITE, chess.BLACK]
            for square in chess.SQUARES
        }
        self.zobristSide = random.getrandbits(64)

        # Opens book
        try:
            self.book = chess.polyglot.open_reader(bookPath) 
        except FileNotFoundError:
            self.book = None

    # Method to return book move
    def bookMove(self, board):
        if not self.book:
            return None
        try:
            return self.book.weighted_choice(board).move
        except IndexError:           
            return None
        
    # Hashes current board using a zobrist hash
    def computeZobristHash(self, board: chess.Board):
        try:
            return board.transposition_key()
        except AttributeError:
            return hash(board._transposition_key())

    # Innitial evaluation function used for base board
    def fullEvaluate(self, board: chess.Board):
        score = 0
        for sq in chess.SQUARES:
            piece = board.piece_at(sq)
            if not piece:
                continue

            # Engine plays black uses negative for white piece evaluation
            factor = 1 if piece.color == chess.BLACK else -1
            idx = sq if piece.color == chess.WHITE else chess.square_mirror(sq)
            score += factor * (
                self.pieceValues[piece.piece_type] + self.pieceTables[piece.piece_type][idx]
            )
        return score

    # Evaluates new boards by calculating the difference before and after a move
    def deltaEval(self, board: chess.Board, move: chess.Move, currentScore: int):
        
        # Finds original piece
        piece = board.piece_at(move.from_square)
        colorFactor = 1 if piece.color == chess.BLACK else -1  # + for Black, – for White

        # Makes the move
        fromIdx = move.from_square if piece.color == chess.WHITE \
                  else chess.square_mirror(move.from_square)

        # Removes score representing old position
        currentScore -= colorFactor * (
            self.pieceValues[piece.piece_type] + self.pieceTables[piece.piece_type][fromIdx]
        )

        # Moves piece to new square
        promoType = move.promotion or piece.piece_type
        toIdx = move.to_square if piece.color == chess.WHITE \
                else chess.square_mirror(move.to_square)
        currentScore += colorFactor * (
            self.pieceValues[promoType] + self.pieceTables[promoType][toIdx]
        )

        # Handles capture conditions
        if board.is_capture(move):
            victimSq = move.to_square
            if board.is_en_passant(move):                       
                victimSq += 8 if piece.color == chess.WHITE else -8

            capturedType = board.piece_type_at(victimSq)
            if capturedType is not None:
                vicIdx = victimSq if piece.color == chess.BLACK \
                         else chess.square_mirror(victimSq)

                # Handles removal of victim piece
                currentScore += colorFactor * (
                    self.pieceValues[capturedType] +
                    self.pieceTables[capturedType][vicIdx]
                )

        # Handles castling case
        if board.is_castling(move):
            rookFrom, rookTo = (
                (move.to_square + 1, move.to_square - 1)   
                if chess.square_file(move.to_square) == 6  
                else (move.to_square - 2, move.to_square + 1)  
            )
            for sqFrom, sqTo in [(rookFrom, rookTo)]:
                idxFrom = sqFrom if piece.color == chess.WHITE else chess.square_mirror(sqFrom)
                idxTo   = sqTo   if piece.color == chess.WHITE else chess.square_mirror(sqTo)
                currentScore -= colorFactor * (
                    self.pieceValues[chess.ROOK] + self.pieceTables[chess.ROOK][idxFrom]
                )
                currentScore += colorFactor * (
                    self.pieceValues[chess.ROOK] + self.pieceTables[chess.ROOK][idxTo]
                )

        return currentScore


    # Orders moves to improve alpha-beta prunning
    def orderMoves(self, board, ttMove=None):

        # Prioritizes capture moves
        captures, quiets = [], []

        # Starts Mvvlva move ordering
        for mv in board.legal_moves:
            if mv == ttMove:                 
                return [mv] + list(board.legal_moves)
            (captures if board.is_capture(mv) else quiets).append(mv)

        # Sorts capture list by MvvLva
        captures.sort(key=lambda m: self.mvvLvaScore[
            board.piece_type_at(m.to_square) or chess.PAWN]
            [board.piece_at(m.from_square).piece_type], reverse=True)

        return captures + quiets


    
    # Uses MvvLva to score moves
    def scoreMove(self, board, move, ttMove):

        # Returns the transposition table move
        if move == ttMove:            
            return 1_000_000


        # Handles capture case
        if board.is_capture(move):
            victimSq = move.to_square
            if board.is_en_passant(move):
                piece = board.piece_at(move.from_square)
                victimSq += 8 if piece.color == chess.WHITE else -8

            victim   = board.piece_type_at(victimSq) or chess.PAWN
            attacker = board.piece_at(move.from_square).piece_type
            return 500_000 + self.mvvLvaScore[victim][attacker]

        return 0


    # Uses a minimax algorithm with alpha beta pruning to find best move
    def minimax(self, board, depth, score, alpha, beta, maximizing, ply=0):

        # Gets current hash
        key = self.computeZobristHash(board)

        # Checks for transposition move
        ttEntry = self.transpositionTable.get(key)
        if ttEntry and ttEntry["depth"] >= depth:
            return ttEntry["value"]
        ttMove = ttEntry.get("move") if ttEntry else None


        # Handles leaves in the tree
        if board.is_game_over():                       
            if board.is_checkmate():
                # Each side prioritizes not getting checkmated and trying to checkmate
                val = (1000000 - ply) if not maximizing else (-1000000 + ply)
            else:
                # Stalemate is neutral
                val = 0
            self.transpositionTable[key] = {"depth": depth, "value": val}
            return val

        # Reaches maximum depth
        if depth == 0:                                
            self.transpositionTable[key] = {"depth": depth, "value": score}
            return score


        # Main body of minimax
        bestMove = None                          
        if maximizing:
            best = -float("inf")
            for mv in self.orderMoves(board, ttMove):      

                # Incremental hash used to find next board value
                nextScore = self.deltaEval(board, mv, score)
                board.push(mv)

                # Recurses to try next board
                val = self.minimax(board, depth-1, nextScore, alpha, beta, False, ply+1)

                # Removes last move
                board.pop()
                if val > best:
                    best, bestMove = val, mv

                # Checks to see if pruning is possible
                alpha = max(alpha, best)
                if beta <= alpha:
                    break
        else:
            # Similar idea to max, but tries to minimize the possible score
            # to represent the oponent mimizing computer score
            best = float("inf")
            for mv in self.orderMoves(board, ttMove):      
                nextScore = self.deltaEval(board, mv, score)
                board.push(mv)
                val = self.minimax(board, depth-1, nextScore, alpha, beta, True, ply+1)
                board.pop()
                if val < best:
                    best, bestMove = val, mv
                beta = min(beta, best)
                if beta <= alpha:
                    break

        # Store calculated move in transposition table
        self.transpositionTable[key] = {"depth": depth, "value": best, "move": bestMove}
        return best


    # Uses minimax to find the best move in a current position
    def findBestMove(self, board: chess.Board, maxTime: float = 2.0):

        # Checks for book move
        bm = self.bookMove(board)
        if bm:
            return bm

        # Constants
        start    = time.perf_counter()
        rootEval = self.fullEvaluate(board)
        depth    = 1
        bestMove = None                      

        # Iterates deeper until time limit is exceeded by last layer
        while True:
            if time.perf_counter() - start >= maxTime:
                break                       

            self.transpositionTable.clear()  

            # Values for alpha beta pruning
            bestVal  = -float("inf")
            alpha, beta = -float("inf"), float("inf")

            # Starts the recursive process
            for mv in self.orderMoves(board):           
                scoreAfter = self.deltaEval(board, mv, rootEval)
                board.push(mv)
                val = self.minimax(board, depth - 1, scoreAfter,
                                alpha, beta, False)
                board.pop()

                if val > bestVal:                       
                    bestVal, bestMove = val, mv
                alpha = max(alpha, bestVal)

            depth += 1                                  
        print(depth)
        
        return bestMove
