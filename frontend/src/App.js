import React, { useState, useEffect } from 'react';
import { Chessboard } from 'react-chessboard';
import axios from 'axios';
import './App.css';

function App() {
  const [boardPosition, setBoardPosition] = useState({});
  const [gameState, setGameState] = useState({
    turn: 'white',
    check: false,
    gameOver: false,
    checkmate: false,
    stalemate: false
  });
  const [selectedSquare, setSelectedSquare] = useState(null);
  const [legalMoves, setLegalMoves] = useState([]);
  const [lastMove, setLastMove] = useState(null);

  // Fetch the board state from the backend
  const fetchBoardState = async () => {
    try {
      const response = await axios.get('/api/board');
      setBoardPosition(response.data);
      setGameState({
        turn: response.data.turn,
        check: response.data.check,
        gameOver: response.data.game_over,
        checkmate: response.data.checkmate,
        stalemate: response.data.stalemate
      });
    } catch (error) {
      console.error('Error fetching board state:', error);
    }
  };

  // Fetch legal moves
  const fetchLegalMoves = async () => {
    try {
      const response = await axios.get('/api/legal-moves');
      setLegalMoves(response.data.moves);
    } catch (error) {
      console.error('Error fetching legal moves:', error);
    }
  };

  // Make a move
  const makeMove = async (from, to) => {
    try {
      const moveUci = `${from}${to}`;
      const response = await axios.post('/api/move', { move: moveUci });
      
      if (response.data.success) {
        setBoardPosition(response.data.board);
        setGameState({
          turn: response.data.board.turn,
          check: response.data.board.check,
          gameOver: response.data.board.game_over,
          checkmate: response.data.board.checkmate,
          stalemate: response.data.board.stalemate
        });
        setLastMove({ from, to });
        setSelectedSquare(null);
        fetchLegalMoves();
      }
    } catch (error) {
      console.error('Error making move:', error);
    }
  };

  // Get a move from the engine
  const getEngineMove = async () => {
    try {
      const response = await axios.get('/api/engine-move');
      
      if (response.data.success) {
        setBoardPosition(response.data.board);
        setGameState({
          turn: response.data.board.turn,
          check: response.data.board.check,
          gameOver: response.data.board.game_over,
          checkmate: response.data.board.checkmate,
          stalemate: response.data.board.stalemate
        });
        
        // Parse the move to highlight it
        const move = response.data.move;
        setLastMove({
          from: move.substring(0, 2),
          to: move.substring(2, 4)
        });
        
        fetchLegalMoves();
      }
    } catch (error) {
      console.error('Error getting engine move:', error);
    }
  };

  // Reset the game
  const resetGame = async () => {
    try {
      const response = await axios.post('/api/reset');
      
      if (response.data.success) {
        setBoardPosition(response.data.board);
        setGameState({
          turn: response.data.board.turn,
          check: response.data.board.check,
          gameOver: response.data.board.game_over,
          checkmate: response.data.board.checkmate,
          stalemate: response.data.board.stalemate
        });
        setSelectedSquare(null);
        setLastMove(null);
        fetchLegalMoves();
      }
    } catch (error) {
      console.error('Error resetting game:', error);
    }
  };

  // Handle square click
  const handleSquareClick = (square) => {
    // If a piece is already selected, try to make a move
    if (selectedSquare) {
      if (selectedSquare !== square) {
        const moveUci = `${selectedSquare}${square}`;
        if (legalMoves.includes(moveUci)) {
          makeMove(selectedSquare, square);
        } else {
          setSelectedSquare(square);
        }
      } else {
        setSelectedSquare(null);
      }
    } else {
      // Select the square if there's a piece on it
      if (boardPosition[square]) {
        setSelectedSquare(square);
      }
    }
  };

  // Initialize the board
  useEffect(() => {
    fetchBoardState();
    fetchLegalMoves();
  }, []);

  // Convert the board position to FEN-like format for react-chessboard
  // This is a simplification - we're just setting custom pieces
  const customPieces = () => {
    const pieces = {};
    Object.keys(boardPosition).forEach(square => {
      if (typeof boardPosition[square] === 'string' && 
          boardPosition[square].includes('_')) {
        
        const [color, type] = boardPosition[square].split('_');
        if (square.length === 2 && 
            ['a','b','c','d','e','f','g','h'].includes(square[0]) && 
            ['1','2','3','4','5','6','7','8'].includes(square[1])) {
          
          const pieceCode = color === 'w' ? type.toUpperCase() : type;
          pieces[square] = pieceCode;
        }
      }
    });
    return pieces;
  };
  
  // Function to determine square styles
  const squareStyles = () => {
    const styles = {};
    
    // Highlight selected square
    if (selectedSquare) {
      styles[selectedSquare] = { backgroundColor: 'rgba(255, 255, 0, 0.4)' };
      
      // Highlight legal moves from the selected square
      legalMoves.forEach(move => {
        if (move.startsWith(selectedSquare)) {
          const targetSquare = move.substring(2, 4);
          styles[targetSquare] = { backgroundColor: 'rgba(0, 255, 0, 0.4)' };
        }
      });
    }
    
    // Highlight last move
    if (lastMove) {
      styles[lastMove.from] = { 
        ...styles[lastMove.from],
        backgroundColor: styles[lastMove.from] 
          ? 'rgba(255, 165, 0, 0.6)' 
          : 'rgba(255, 165, 0, 0.4)'
      };
      styles[lastMove.to] = { 
        ...styles[lastMove.to],
        backgroundColor: styles[lastMove.to] 
          ? 'rgba(255, 165, 0, 0.6)' 
          : 'rgba(255, 165, 0, 0.4)'
      };
    }
    
    return styles;
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Chess Game with Python Engine</h1>
      </header>
      
      <div className="game-container">
        <div className="chessboard-container">
          <Chessboard 
            id="board"
            position={customPieces()}
            onSquareClick={handleSquareClick}
            customSquareStyles={squareStyles()}
            areArrowsAllowed={true}
            boardOrientation="white"
          />
        </div>
        
        <div className="game-info">
          <div className="status">
            <p>Turn: {gameState.turn}</p>
            {gameState.check && <p className="check-status">Check!</p>}
            {gameState.checkmate && <p className="checkmate-status">Checkmate!</p>}
            {gameState.stalemate && <p className="stalemate-status">Stalemate!</p>}
            {gameState.gameOver && <p className="game-over-status">Game Over</p>}
          </div>
          
          <div className="controls">
            <button onClick={getEngineMove} disabled={gameState.gameOver}>
              Get Engine Move
            </button>
            <button onClick={resetGame}>
              Reset Game
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App; 