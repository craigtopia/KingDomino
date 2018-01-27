
import networkx as nx
TERRAINS = ['wheat', 'water', 'forest', 'cave', 'wasteland', 'farm']
MAXWIDTH = 5
CASTLE_COORDS = (4, 4)
CASTLE_ADJ_COORDS = [(4, 3), (4, 5), (3, 4), (5, 4)]

COORD_MAP = {}
for i in range(9):
    for j in range(9):
        # Number gridpoints with integers
        COORD_MAP.update({(j, i): i * 9 + j})


class Side(object):

    def __init__(self, kings, terrain):
        assert isinstance(kings, int), 'Kings must be an integer.'
        assert terrain in TERRAINS, 'Unrecognized terrain.'
        self.kings = kings
        self.terrain = terrain

    def __eq__(self, other):
        assert isinstance(other, Side), 'Invalid comparison.'
        if self.kings == other.kings:
            if self.terrain == other.terrain:
                return True
        return False

    def __ne__(self, other):
        assert isinstance(other, Side), 'Invalid comparison.'
        if not self.__eq__(other):
            return True
        return False

    def __repr__(self):
        return self.terrain + ', k=' + str(self.kings)


class Domino(object):

    def __init__(self, side_a, side_b, number):
        self.side_a = side_a
        self.side_b = side_b
        self.number = number

    def __repr__(self):
        return 'A: ' + self.side_a.terrain + ', k=' + str(self.side_a.kings) + \
             '\nB: ' + self.side_b.terrain + ', k=' + str(self.side_b.kings)

    def other_side(self, side):
        if side == self.side_a:
            return self.side_b
        elif side == self.side_b:
            return self.side_a
        else:
            assert False, 'You provided a side not on this Domino.'


class Board(object):
    def __init__(self):
        self.B = {}
        self.iMax = None
        self.iMin = None
        self.jMax = None
        self.jMin = None
        self.Edges = []
        self.Graph = {}

    def __getitem__(self, ij):
        return self.B[ij]

    def assign_domino(self, move):
        assert (move.Di != 0) or (move.Dj != 0), 'Cannot put two sides on same square.'
        assert max(move.Di, move.Dj) <= 1, 'Must be adjacent.'
        assert min(move.Di, move.Dj) >=-1, 'Must be adjacent.'
        self.B[move.i, move.j] = move.side_a
        self.B[move.i + move.Di, move.j + move.Dj] = move.side_b
        self.record_external_edge_formation(move)
        if move.side_a.terrain == move.side_b.terrain:
            # Record internal edge if both sides of domino have same terrain
            edge = (COORD_MAP[move.i, move.j], COORD_MAP[move.i2, move.j2])
            self.Edges += [edge]
            self.update_graph(move, edge)

    def update_graph(self, move, edge):
        e1 = edge[0]
        e2 = edge[1]
        m1 = COORD_MAP[move.i, move.j]
        m2 = COORD_MAP[move.i2, move.j2]

        assert m1 in edge or m2 in edge, 'This move was invalid because it did not form an edge.'

        if e1 not in self.Graph.keys():
            self.Graph.update({e1: {e2}})
        else:
            self.Graph[e1].add(e2)

        if e2 not in self.Graph.keys():
            self.Graph.update({e2: {e1}})
        else:
            self.Graph[e2].add(e1)

        if m1 not in edge:
            if m1 not in self.Graph.keys():
                self.Graph.update({m1: set()})

        if m2 not in edge:
            if m2 not in self.Graph.keys():
                self.Graph.update({m2: set()})

    def check_max_min(self, move):
        # Make sure the move doesn't expand board too wide/long.
        i2 = move.i + move.Di
        j2 = move.j + move.Dj

        if self.iMax is None:
            iMax = max(move.i, i2)
        else:
            iMax = max(self.iMax, move.i, i2)

        if self.jMax is None:
            jMax = max(move.j, j2)
        else:
            jMax = max(self.jMax, move.j, j2)

        if self.iMin is None:
            iMin = min(move.i, i2)
        else:
            iMin = max(self.iMin, move.i, i2)

        if self.jMin is None:
            jMin = min(move.j, j2)
        else:
            jMin = min(self.jMin, move.j, j2)

        if iMax - iMin >= MAXWIDTH:
            return False
        if jMax - jMin >= MAXWIDTH:
            return False

        return True

    @staticmethod
    def check_castle_adjacency(move):
        if (move.i, move.j) in CASTLE_ADJ_COORDS:
            return True
        if (move.i2, move.j2) in CASTLE_ADJ_COORDS:
            return True
        return False

    def check_external_edge_formation(self, move):
        # Just have to check the 3 adjacencies to given move, (4th is same domino)
        for step in [(1, 0), (0, 1), (-1, 0), (0, -1)]:
            if (move.Di, move.Dj) != step:
                step_i = move.i + step[0]
                step_j = move.j + step[1]
                if (step_i, step_j) in self.B.keys():
                    existing_terrain = self.B[step_i, step_j].terrain
                    if existing_terrain == move.side_a.terrain:
                        return True

        for step in [(1, 0), (0, 1), (-1, 0), (0, -1)]:
            if (-move.Di, -move.Dj) != step:
                step_i = move.i2 + step[0]
                step_j = move.j2 + step[1]
                if (step_i, step_j) in self.B.keys():
                    existing_terrain = self.B[step_i, step_j].terrain
                    if existing_terrain == move.side_b.terrain:
                        return True
        return False

    def record_external_edge_formation(self, move):
        for step in [(1, 0), (0, 1), (-1, 0), (0, -1)]:
            if (move.Di, move.Dj) != step:
                step_i = move.i + step[0]
                step_j = move.j + step[1]
                if (step_i, step_j) in self.B.keys():
                    existing_terrain = self.B[step_i, step_j].terrain
                    if existing_terrain == move.side_a.terrain:
                        edge = (COORD_MAP[move.i, move.j], COORD_MAP[step_i, step_j])
                        self.Edges += [edge]
                        self.update_graph(move, edge)

        for step in [(1, 0), (0, 1), (-1, 0), (0, -1)]:
            if (-move.Di, -move.Dj) != step:
                step_i = move.i2 + step[0]
                step_j = move.j2 + step[1]
                if (step_i, step_j) in self.B.keys():
                    existing_terrain = self.B[step_i, step_j].terrain
                    if existing_terrain == move.side_b.terrain:
                        edge = (COORD_MAP[move.i2, move.j2], COORD_MAP[step_i, step_j])
                        self.Edges += [edge]
                        self.update_graph(move, edge)

    @staticmethod
    def check_internal_edge(move):
        if move.side_a.terrain == move.side_b.terrain:
            return True
        return False

    def check_move_validity(self, move):
        castle_adjacency = self.check_castle_adjacency(move)
        ext_edge_formation = self.check_external_edge_formation(move)
        within_width_limit = self.check_max_min(move)

        if within_width_limit:
            if castle_adjacency:
                return True
            if ext_edge_formation:
                return True
        return False


class Move(object):
    def __init__(self, domino, side_a, i, j, Di, Dj):
        self.domino = domino
        self.side_a = side_a
        self.side_b = domino.other_side(side_a)
        self.i = i
        self.j = j
        self.Di = Di
        self.Dj = Dj
        self.i2 = i + Di
        self.j2 = j + Dj


myField = Side(0, 'wheat')
myWater = Side(0, 'water')
myDom = Domino(myField, myWater, 1)

myMove = Move(myDom, myDom.side_a, 3, 4, -1, 0)
myMove2 = Move(myDom, myDom.side_a, 3, 5, -1, 0)
myBoard = Board()

print('M1 valid: ', myBoard.check_move_validity(myMove))
myBoard.assign_domino(myMove)
print('cast adj: ', myBoard.check_castle_adjacency(myMove2))
print('ext edge: ', myBoard.check_external_edge_formation(myMove2))
print('int edge: ', myBoard.check_internal_edge(myMove2))

print('M2 valid: ', myBoard.check_move_validity(myMove2))
myBoard.assign_domino(myMove2)
print(myBoard.B.keys())

print(myBoard.Edges)
print(myBoard.Graph)