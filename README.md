# mongoChess
A chess engine built from scratch in python using pygame

## How it works
To try it out you could clone the repo and with the included requirements you can get the project run by running ``python3 ChessMain.py``

At the moment I have built a mechanism for locking pieces from moving if they have no legal moves to make, and as of right now only the pawn and the rook have a logic that calculate this. Untill then you can only move these.

An basic "Undo" mechanism is in place by pressing the ``z`` button, which will undo your last move untill the original setup of the board is made
## TODO:

1. ~~Add the Bishop movement logic~~
2. ~~Add Knight movement logic~~
3. ~~Add Queen movement logic~~
4. ~~Add King movement logic~~
5. Add Check/Checkmate/Stalemate logic
6. Some kind of AI to challenge you
7. General cleanup with smoother animations, menu and displaying movement history

##Probably not going to implement:
1. Multiplayer

