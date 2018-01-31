TERRAINS = ['wheat', 'water', 'forest', 'cave', 'wasteland', 'sheep', 'castle']
MAXWIDTH = 5
CASTLE_COORDS = (4, 4)
CASTLE_ADJ_COORDS = [(4, 3), (4, 5), (3, 4), (5, 4)]

COORD_MAP = {}

for i in range(9):
    for j in range(9):
        # Number gridpoints with integers
        COORD_MAP.update({(j, i): i * 9 + j})

REV_COORD_MAP = {v: k for k,v in COORD_MAP.items()}


class Side(object):

    def __init__(self, kings, terrain):
        assert isinstance(kings, int), 'Kings must be an integer.'
        assert terrain in TERRAINS, 'Unrecognized terrain: ' + terrain
        self.kings = kings
        self.terrain = terrain

    def __eq__(self, other):
        assert isinstance(other, Side), 'Invalid comparison.'
        equal = True
        equal &= self.kings == other.kings
        equal &= self.terrain == other.terrain
        return equal

    def __ne__(self, other):
        assert isinstance(other, Side), 'Invalid comparison.'
        if not self.__eq__(other):
            return True
        return False

    def __repr__(self):
        return self.terrain + ', k=' + str(self.kings)

    def __hash__(self):
        return hash((self.kings, self.terrain))


class Domino(object):

    def __init__(self, one_side, other_side, number):
        self.one_side = one_side
        self.other_side = other_side
        self.number = number

    def __hash__(self):
        return hash((self.one_side, self.other_side))

    def __repr__(self):
        return 'A: ' + self.one_side.terrain + ', k=' + str(self.one_side.kings) + \
             '\nB: ' + self.other_side.terrain + ', k=' + str(self.other_side.kings)

    def __getitem__(self, item):
        assert item in (0, 1), 'Must choose 0 or 1 when accessing sides of a domino.'
        if item == 0:
            return self.one_side
        return self.other_side
    
    def __eq__(self, other):
        """
        Will consider like Dominos equal even if their numbers are different.
        """
        assert isinstance(other, Domino)
        equal = True
        if self.one_side == other.one_side:
            if self.other_side == other.other_side:
                return True
        if self.one_side == other.other_side:
            if self.other_side == other.one_side:
                return True
        return False

    def __ne__(self, other):
        if self.__eq__(other):
            return False
        return True

    def get_other_side(self, side):
        if side == self.one_side:
            return self.other_side
        elif side == self.other_side:
            return self.one_side
        else:
            assert False, 'You provided a side not on this Domino.'


class Board(object):
    def __init__(self):
        self.B = {}  # collection of sides, keyed by (i, j) tuple of integers
        self.iMax = None
        self.iMin = None
        self.jMax = None
        self.jMin = None
        self.Edges = []
        self.Graph = {}
        self.connected_components = []
        self.castle_adj_coords = []
        self.castle_coords = ()
        self.place_castle()

    def place_castle(self, castle_coords=(4, 4)):
        self.castle_coords = castle_coords
        self.B[castle_coords] = Side(kings=0, terrain='castle')
        for iBump, jBump in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            self.castle_adj_coords += [(castle_coords[0] + iBump, castle_coords[1] + jBump)]

    def __getitem__(self, ij):
        return self.B[ij]

    def undo_move(self, move):
        #  TODO: Need to remove edge list or junk edge list entirely
        #  TODO: This function entirely untested. Use at your own risk!
        self.B.pop(move.i, move.j)
        self.B.pop(move.i2, move.j2)
        self.update_max_min()
        positions = [move.i, move.j, move.i2, move.j2]
        for p in positions:
            if p in self.Graph.keys():
                self.Graph.pop(p)
        for k in self.Graph.keys():
            vals = set()
            for v in self.Graph[k]:
                if v not in positions:
                    vals.add(v)
            self.Graph[k] = vals

    def assign_domino(self, move):
        if self.check_move_validity(move):
            self.B[move.i, move.j] = move.side_a
            self.B[move.i2, move.j2] = move.side_b
            self.record_external_edge_formation(move)
            self.update_max_min(move)
            if move.side_a.terrain == move.side_b.terrain:
                # Record internal edge if both sides of domino have same terrain
                edge = (COORD_MAP[move.i, move.j], COORD_MAP[move.i2, move.j2])
                self.Edges += [edge]
                self.update_graph(move, edge)
            else:
                self.update_graph(move)
            return True
        else:
            return False

    def update_graph(self, move, edge=None):
        m1 = COORD_MAP[move.i, move.j]
        m2 = COORD_MAP[move.i2, move.j2]

        if edge is not None:
            e1 = edge[0]
            e2 = edge[1]

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
        else:
            if m1 not in self.Graph.keys():
                self.Graph.update({m1: set()})
            if m2 not in self.Graph.keys():
                self.Graph.update({m2: set()})

    def update_max_min(self, move=None):
        if move is not None:
            if self.iMax is None:
                self.iMax = max(move.i, move.i2)
            else:
                self.iMax = max(self.iMax, move.i, move.i2)

            if self.jMax is None:
                self.jMax = max(move.j, move.j2)
            else:
                self.jMax = max(self.jMax, move.j, move.j2)

            if self.iMin is None:
                self.iMin = min(move.i, move.i2)
            else:
                self.iMin = min(self.iMin, move.i, move.i2)

            if self.jMin is None:
                self.jMin = min(move.j, move.j2)
            else:
                self.jMin = min(self.jMin, move.j, move.j2)
        else:
            # Figure out from existing board
            i_s = [x[0] for x in self.B.keys()]
            j_s = [x[1] for x in self.B.keys()]

            self.iMax = max(i_s)
            self.jMax = max(j_s)

            self.iMin = min(i_s)
            self.jMin = min(j_s)

    def check_max_min(self, move):
        # Make sure the move doesn't expand board too wide/long.

        if self.iMax is None:
            iMax = max(move.i, move.i2)
        else:
            iMax = max(self.iMax, move.i, move.i2)

        if self.jMax is None:
            jMax = max(move.j, move.j2)
        else:
            jMax = max(self.jMax, move.j, move.j2)

        if self.iMin is None:
            iMin = min(move.i, move.i2)
        else:
            iMin = min(self.iMin, move.i, move.i2)

        if self.jMin is None:
            jMin = min(move.j, move.j2)
        else:
            jMin = min(self.jMin, move.j, move.j2)

        if iMax - iMin >= MAXWIDTH:
            return False

        if jMax - jMin >= MAXWIDTH:
            return False

        return True

    def check_castle_adjacency(self, move):
        if (move.i, move.j) in self.castle_adj_coords:
            return True
        if (move.i2, move.j2) in self.castle_adj_coords:
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
        if move.i < 0 or move.i2 < 0:
            return False
        if move.j < 0 or move.j2 < 0:
            return False
        if move.i > 8 or move.i2 > 8:
            return False
        if move.j > 8 or move.j2 > 8:
            return False
        if (move.Di == 0) and (move.Dj == 0):
            return False
        if max(move.Di, move.Dj) > 1:
            return False
        if min(move.Di, move.Dj) < -1:
            return False
        if (move.i, move.j) in self.B.keys():
            return False
        if (move.i2, move.j2) in self.B.keys():
            return False
        if (move.i, move.j) == (4, 4):
            return False
        if (move.i2, move.j2) == (4, 4):
            return False

        if self.check_max_min(move):
            if self.check_castle_adjacency(move):
                return True
            if self.check_external_edge_formation(move):
                return True
        return False

    def find_connected_components(self):
        connected_components = []
        for key in self.Graph.keys():
            for group in connected_components:
                if key in group:
                    break
            else:
                connected_components += [self.dfs(self.Graph, key)]
        self.connected_components = connected_components

    def dfs(self, graph, start, visited=None):
        # Depth-first search for finding connected components to start node
        if visited is None:
            visited = set()
        visited.add(start)

        for nxt in graph[start] - visited:
            visited.add(nxt)
            self.dfs(graph, nxt, visited)
        return visited

    def score_kings(self):
        self.find_connected_components()
        total_score = 0
        for comp in self.connected_components:
            k = 0
            for c in comp:
                side = self.B[REV_COORD_MAP[c]]
                k += side.kings
            component_score = k * len(comp)
            total_score += component_score
        return total_score

    def get_feasible_move_set(self, domino):
        """
        Returns all moves that are valid, given self and domino
        """
        assert isinstance(domino, Domino), 'Please pass a king domino domino object.'

        feasible_set = set()
        for coords, side in self.B.items():
            i_existing = coords[0]
            j_existing = coords[1]
            for iBump, jBump in [(1, 0), (-1, 0), (0, 1), (0, -1)]:  # Test all adjacencies to each side

                i = i_existing + iBump
                j = j_existing + jBump
                for Di, Dj in [(1, 0), (-1, 0), (0, 1), (0, -1)]:  # Test all rotations
                    candidate_move = Move(domino, 0, i, j, Di, Dj)
                    if self.check_move_validity(candidate_move):
                        feasible_set.add(candidate_move)
        return feasible_set


class Move(object):

    def __init__(self, domino, first_side, i, j, Di, Dj):
        # side_a goes in spot (i, j)
        # side_b goes in spot (i + Di, j + Dj)
        self.domino = domino
        self.side_a = domino[first_side]
        self.side_b = domino[0 if first_side else 1]
        self.i = i
        self.j = j
        self.Di = Di
        self.Dj = Dj
        self.i2 = i + Di
        self.j2 = j + Dj
    
    def __eq__(self, other):
        assert isinstance(other, Move), 'Invalid comparison.'
        equal = True
        equal &= self.domino == other.domino
        equal &= self.i == other.i
        equal &= self.j == other.j
        equal &= self.Di == other.Di
        equal &= self.Dj == other.Dj
        equal &= self.i2 == other.i2
        equal &= self.j2 == other.j2
        return equal
    
    def __ne__(self, other):
        if self.__eq__(other):
            return False
        return True

    def __hash__(self):
        return hash((self.side_a, self.side_b, self.i, self.j, self.Di, self.Dj))

    def __repr__(self):
        return '(i , j ): (%d, %d) - %s \t(i2, j2): (%d, %d) - %s\n' % (self.i, self.j, self.side_a.terrain,
                                                                         self.i2, self.j2, self.side_b.terrain)


if __name__ == '__main__':
    """
    /home/craigtopia/PycharmProjects/KingDomino/venv/bin/python /home/craigtopia/PycharmProjects/KingDomino/kingDomino.py
    M1 valid:  True
    cast adj:  False
    ext edge:  True
    int edge:  False
    M2 valid:  True
    M3 valid:  True
    dict_keys([(5, 4), (6, 4), (5, 5), (6, 5), (7, 6), (6, 6)])
    [(50, 41), (51, 42), (60, 51)]
    {50: {41}, 41: {50}, 51: {42, 60}, 42: {51}, 60: {51}, 61: set()}
    [{41, 50}, {42, 51, 60}, {61}]
    9
    
    Process finished with exit code 0

    """
    myField = Side(0, 'wheat')
    myWater = Side(1, 'water')
    myDom = Domino(myField, myWater, 1)

    myMove = Move(myDom, 0, 5, 4, 1, 0)
    myMove2 = Move(myDom, 0, 5, 5, 1, 0)
    myMove3 = Move(myDom, 0, 7, 6, -1, 0)
    myBoard = Board()

    print('M1 valid: ', myBoard.check_move_validity(myMove))
    myBoard.assign_domino(myMove)
    print('cast adj: ', myBoard.check_castle_adjacency(myMove2))
    print('ext edge: ', myBoard.check_external_edge_formation(myMove2))
    print('int edge: ', myBoard.check_internal_edge(myMove2))

    print('M2 valid: ', myBoard.check_move_validity(myMove2))
    myBoard.assign_domino(myMove2)

    print('M3 valid: ', myBoard.check_move_validity(myMove3))
    myBoard.assign_domino(myMove3)

    print(myBoard.B.keys())

    print(myBoard.Edges)
    print(myBoard.Graph)
    myBoard.find_connected_components()
    print(myBoard.connected_components)
    print(myBoard.score_kings())

