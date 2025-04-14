# Chess Game with Python Engine & React UI

This project combines a Python chess engine with a React frontend to create an interactive chess game.

## Project Structure

- `chess_engine.py`: Core chess engine with minimax algorithm and alpha-beta pruning
- `app.py`: Flask API server that exposes the chess engine functionality
- `frontend/`: React application for the user interface

## Setup Instructions

### Backend (Python)

1. Install the required Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Start the Flask API server:
   ```bash
   python app.py
   ```
   The server will run on http://localhost:5000

### Frontend (React)

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install the required npm packages:
   ```bash
   npm install
   ```

3. Start the React development server:
   ```bash
   npm start
   ```
   The frontend will run on http://localhost:3000

## How to Play

1. Open http://localhost:3000 in your web browser
2. The chess board will appear with the initial position
3. Click on a piece to select it
4. Click on a highlighted square to move the selected piece
5. Use the "Get Engine Move" button to let the computer make a move
6. Use the "Reset Game" button to start a new game

## Features

- Interactive chess board with piece movement
- Legal move highlighting
- Last move highlighting
- Game state display (check, checkmate, stalemate)
- Computer opponent using minimax algorithm

## Technologies Used

- Backend: Python, Flask, python-chess
- Frontend: React, react-chessboard
- Algorithms: Minimax with alpha-beta pruning