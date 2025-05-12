# Chess engine and web app

This program creates a chess wep app iteration in which the user can play against a chess bot.

## Running the code

### To run the code, begin by installing the required dependencies:

pip install -r requirements.txt

### Then, activate the back and front ends:

python server.py

python -m http.server 3000

### Finally, go to a web browser and navigate to http://127.0.0.1:3000

## Overview

The basis for this engine is a recursive algorithm that makes use of minimax and alpha-beta prunning to find the optimal move.
The engine uses many different techniques to try and speed up the recursion, allowing it to go as deeply as possible. Each search
is capped at a few seconds (this can be changed) but usually makes it 7-8 layers ahead. In the early game, the engine will use book
moves for as long as possible to ensure an effective opening. From there, the engine uses a iterative scoring changes between boards,
transposition tables running on zobrist hashing, move ordering using MvvLva (Most valuable victim, Least valuable attacker) move odering
and alpha beta pruning to make the engine more efficient. I estmiate the bot's elo at around 1700 as it can consistently beat the 1600
chess bots on chess.com, but loses to the 2000.



