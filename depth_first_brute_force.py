import kingDomino as kD
import copy
from domino_library import DOMINO_LIB

MAX_SCORE = 0


def sera(Dominos, board, visited=None):
    global MAX_SCORE

    if visited is None:
        visited = set()

    for d in Dominos - visited:
        M = board.get_feasible_move_set(d)
        if len(M) != 0:
            visited.add(d)
            for mv in M:
                bc = copy.deepcopy(board)
                bc.assign_domino(mv)
                sera(Dominos, bc, visited)
            visited.remove(d)
    score = board.score_kings()

    if score > MAX_SCORE:
        MAX_SCORE = score
        print(score, board.B)
    return


myBoard = kD.Board()
myBoard.max_score = 0

sera(set(DOMINO_LIB), myBoard)

# Next, try implement a greedy algorithm. It will choose the highest value-add among all moves.