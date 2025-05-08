import chess
import chess.polyglot 
import random

# --- Piece‑square tables (kept in snake_case because they are constants) ---
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


random.seed(42)


class ChessEngine:
    """Simple minimax chess engine with incremental evaluation and camelCase naming."""

    mvvLvaScore = [[0]*7 for _ in range(7)]
    for victim in range(1, 7):
        for attacker in range(1, 7):
            mvvLvaScore[victim][attacker] = 10_000 * victim - attacker

    # --- static tables ---
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

    def __init__(self, depth=5, bookPath="Perfect2023.bin"):
        self.depth = depth
        self.transpositionTable: dict[int, dict] = {}

        # Random numbers only needed if you fall back to custom hashing
        self.zobristTable = {
            (piece_type, color, square): random.getrandbits(64)
            for piece_type in range(1, 7)
            for color in [chess.WHITE, chess.BLACK]
            for square in chess.SQUARES
        }
        self.zobristSide = random.getrandbits(64)

        try:
            self.book = chess.polyglot.open_reader(bookPath) 
        except FileNotFoundError:
            self.book = None

    def bookMove(self, board):
        if not self.book:
            return None
        try:
            return self.book.weighted_choice(board).move
        except IndexError:           # out‑of‑book
            return None
        
  


    # ------------------------------------------------------------------
    # Hashing
    # ------------------------------------------------------------------
    def computeZobristHash(self, board: chess.Board) -> int:
        """Return a 64‑bit hash for *board* using python‑chess' incremental key."""
        try:
            return board.transposition_key()  # fast path (python‑chess ≥ 1.8)
        except AttributeError:
            # Fallback for old versions
            return hash(board._transposition_key())

    # ------------------------------------------------------------------
    # Incremental evaluation helpers
    # ------------------------------------------------------------------
    def fullEvaluate(self, board: chess.Board) -> int:
        """Full evaluation of *board* (material + piece‑square tables)."""
        score = 0
        for sq in chess.SQUARES:
            piece = board.piece_at(sq)
            if not piece:
                continue
            factor = 1 if piece.color == chess.BLACK else -1  # engine score: positive = Black
            idx = sq if piece.color == chess.WHITE else chess.square_mirror(sq)
            score += factor * (
                self.pieceValues[piece.piece_type] + self.pieceTables[piece.piece_type][idx]
            )
        return score

        # ------------------------------------------------------------------
    # Incremental delta evaluation (safe for en‑passant & castling)
    # ------------------------------------------------------------------
    def deltaEval(self, board: chess.Board, move: chess.Move, currentScore: int) -> int:
        """Return the new evaluation after hypothetically playing *move*.
           *board* is still in the pre‑move state when this is called."""
        piece = board.piece_at(move.from_square)
        colorFactor = 1 if piece.color == chess.BLACK else -1  # + for Black, – for White

        # --- 1. remove the piece from its origin square ------------------------
        fromIdx = move.from_square if piece.color == chess.WHITE \
                  else chess.square_mirror(move.from_square)
        currentScore -= colorFactor * (
            self.pieceValues[piece.piece_type] + self.pieceTables[piece.piece_type][fromIdx]
        )

        # --- 2. add the piece (or its promotion) on the destination square -----
        promoType = move.promotion or piece.piece_type
        toIdx = move.to_square if piece.color == chess.WHITE \
                else chess.square_mirror(move.to_square)
        currentScore += colorFactor * (
            self.pieceValues[promoType] + self.pieceTables[promoType][toIdx]
        )

                # --- 3. handle captures (normal & en‑passant) --------------------------
        if board.is_capture(move):
            victimSq = move.to_square
            if board.is_en_passant(move):                       # pawn is behind target
                victimSq += 8 if piece.color == chess.WHITE else -8

            capturedType = board.piece_type_at(victimSq)
            if capturedType is not None:
                vicIdx = victimSq if piece.color == chess.BLACK \
                         else chess.square_mirror(victimSq)

                # Remove the victim’s old contribution
                #   Before: score += (–colorFactor) * value
                #   After : score += 0
                #   Δ      = –(–colorFactor) * value = +colorFactor * value
                currentScore += colorFactor * (
                    self.pieceValues[capturedType] +
                    self.pieceTables[capturedType][vicIdx]
                )

        # --- 4. shift the rook in castling -------------------------------------
        if board.is_castling(move):
            rookFrom, rookTo = (
                (move.to_square + 1, move.to_square - 1)   # king‑side
                if chess.square_file(move.to_square) == 6  # to‑square file g
                else (move.to_square - 2, move.to_square + 1)  # queen‑side
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


    # ------------------------------------------------------------------
    # Move ordering helper
    # ------------------------------------------------------------------
    def orderMoves(self, board, ttMove=None):
        captures, quiets = [], []
        for mv in board.legal_moves:
            if mv == ttMove:                 # PV move first
                return [mv] + list(board.legal_moves)
            (captures if board.is_capture(mv) else quiets).append(mv)

        # Sort only the (small) capture list by MVV‑LVA
        captures.sort(key=lambda m: self.mvvLvaScore[
            board.piece_type_at(m.to_square) or chess.PAWN]
            [board.piece_at(m.from_square).piece_type], reverse=True)

        return captures + quiets


    
        # ------------------------------------------------------------------
    # Move‑scoring helper  (TT first  ➜  MVV‑LVA  ➜  rest) 
    # ------------------------------------------------------------------
    def scoreMove(self, board, move, ttMove):
        if move == ttMove:                       # principal‑variation move
            return 1_000_000

        if board.is_capture(move):
            # --- find the real victim square (handles en‑passant) -----
            victimSq = move.to_square
            if board.is_en_passant(move):
                piece = board.piece_at(move.from_square)
                victimSq += 8 if piece.color == chess.WHITE else -8

            victim   = board.piece_type_at(victimSq) or chess.PAWN  # safety belt
            attacker = board.piece_at(move.from_square).piece_type
            return 500_000 + self.mvvLvaScore[victim][attacker]

        return 0   # quiet move


    # ------------------------------------------------------------------
    # Minimax with alpha‑beta pruning + incremental eval
    # ------------------------------------------------------------------
        # -------- Minimax with alpha‑beta --------
    def minimax(self, board, depth, score, alpha, beta, maximizing, ply=0):
        key = self.computeZobristHash(board)

        ttEntry = self.transpositionTable.get(key)
        if ttEntry and ttEntry["depth"] >= depth:
            return ttEntry["value"]
        ttMove = ttEntry.get("move") if ttEntry else None   # safe even if key missing


        if depth == 0 or board.is_game_over():
            self.transpositionTable[key] = {"depth": depth, "value": score}
            return score

        bestMove = None                          # NEW ➌ track best move
        if maximizing:
            best = -float("inf")
            for mv in self.orderMoves(board, ttMove):      # NEW ➋ pass ttMove
                nextScore = self.deltaEval(board, mv, score)
                board.push(mv)
                val = self.minimax(board, depth-1, nextScore, alpha, beta, False, ply+1)
                board.pop()
                if val > best:
                    best, bestMove = val, mv
                alpha = max(alpha, best)
                if beta <= alpha:
                    break
        else:
            best = float("inf")
            for mv in self.orderMoves(board, ttMove):      # NEW ➋
                nextScore = self.deltaEval(board, mv, score)
                board.push(mv)
                val = self.minimax(board, depth-1, nextScore, alpha, beta, True, ply+1)
                board.pop()
                if val < best:
                    best, bestMove = val, mv
                beta = min(beta, best)
                if beta <= alpha:
                    break

        # store PV move for future probes
        self.transpositionTable[key] = {"depth": depth, "value": best, "move": bestMove}
        return best


    # ------------------------------------------------------------------
    # Root search
    # ------------------------------------------------------------------
    def findBestMove(self, board: chess.Board) -> chess.Move:
        bm = self.bookMove(board)
        if bm:                       # ① book hit → instant reply
            return bm
        # self.transpositionTable.clear()
        rootScore = self.fullEvaluate(board)
        bestMove, bestVal = None, -float("inf")
        alpha, beta = -float("inf"), float("inf")

        for mv in self.orderMoves(board):
            scoreAfter = self.deltaEval(board, mv, rootScore)
            board.push(mv)
            val = self.minimax(board, self.depth - 1, scoreAfter, alpha, beta, False)
            board.pop()
            if val > bestVal:
                bestVal, bestMove = val, mv
            alpha = max(alpha, bestVal)
        return bestMove


# ----------------------- Example usage -------------------------------
if __name__ == "__main__":
    gameBoard = chess.Board()
    engine = ChessEngine(depth=5)

    sideToMove = 0  # 0 = human (white), 1 = engine (black)

    while not gameBoard.is_game_over():
        print(gameBoard)
        if sideToMove == 0:
            userInp = input("Enter your move (e.g. e2e4): ")
            try:
                uciMove = chess.Move.from_uci(userInp.strip())
                if uciMove in gameBoard.legal_moves:
                    gameBoard.push(uciMove)
                    sideToMove = 1
                else:
                    print("Illegal move. Try again.")
            except ValueError:
                print("Bad UCI string. Try again.")
        else:
            best = engine.findBestMove(gameBoard)
            print(f"Engine plays {best}")
            gameBoard.push(best)
            sideToMove = 0

    print(gameBoard.result())
