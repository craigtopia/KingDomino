import pandas as pd
import random
import kingDomino as kD
from domino_library import DOMINO_LIB

if __name__ == '__main__':
    myBoard = kD.Board()

    # Place some moves first
    N = 0
    # random.seed(0)
    dom_set = set(DOMINO_LIB)
    doms = random.sample(DOMINO_LIB, len(DOMINO_LIB))
    for dom in doms[:N]:
        feasible_set = myBoard.get_feasible_move_set(dom)
        mv = random.sample(feasible_set, 1)[0]
        myBoard.assign_domino(mv)

    moves_left = True
    doms_left = set(doms[N:])
    while moves_left:

        total_feasible_set = set()
        for dom in doms_left:
            total_feasible_set = total_feasible_set.union(myBoard.get_feasible_move_set(dom))
        if len(total_feasible_set) == 0:
            moves_left = False
        else:
            tree = kD.MonteCarloKingDominoThinker(myBoard, doms_left, think_time=100)
            out = tree.think_about_set_of_moves(total_feasible_set)
            max_score = -1
            best_move = None

            for mv, score in out.items():
                if score > max_score:
                    best_move = mv
                    max_score = score
            myBoard.assign_domino(best_move)
            doms_left.remove(best_move.domino)

            print(best_move, max_score)
            myBoard.show()
            print(myBoard.score_kings())
