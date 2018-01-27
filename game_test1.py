import kingDomino as kD
from domino_library import DOMINO_LIB
import random

myBoard = kD.Board()
myDomino = DOMINO_LIB[31]

myMove = kD.Move(myDomino, first_side=0, i=5, j=4, Di=1, Dj=0)
myBoard.assign_domino(myMove)
print(myDomino)

print(myBoard.score_kings())