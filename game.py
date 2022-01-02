import random
import copy
from domino_library import DOMINO_LIB


class Game(object):
    """
    4-player:
        * All 48 dominoes
        * one king each player
        * 4 dominoes on menu

    3-player:
        * 36 dominoes
        * one king each player
        * 3 dominoes on menu

    2-player:
        * 24 dominoes
        * two kings each player
        * 4 dominoes on menu

    Setup:
        1. Generate Menu
      **2. Select dominoes
        3. Generate new Menu (two will display at once: selected Menu (old) / unselected Menu (new))

    Turn:
        For each domino in Old Menu:
            1. Place or discard domino
            2. Check if there's a New Menu
                Yes: - Select domino from New Menu
                No: pass (game almost over)
        Check if there's a New Menu:
            Yes: Re-assign New Menu --> Old Menu. Generate New Menu. Start new turn.
            No: Game over!
    """

    def __init__(self, n_players, variant='standard'):
        assert n_players in (2, 3, 4), 'n_players must be 2, 3, or 4'
        assert any([variant == x for x in ['standard']]), 'Sorry, variant %s is not supported.' % variant
        self.n_players = n_players
        self.variant = variant

        self.library_size = 0
        self.kings_per_player = 0
        self.n_dominoes_on_menu = 0

        self.old_menu = []  # List of dominoes
        self.new_menu = []  # List of dominoes
        self.dominoes_in_box = []  # List of dominoes

        self.set_parameters()

    def set_parameters(self):
        if self.n_players == 4:
            self.library_size = 48
            self.kings_per_player = 1
            self.n_dominoes_on_menu = 4

        elif self.n_players == 3:
            self.library_size = 36
            self.kings_per_player = 1
            self.n_dominoes_on_menu = 3

        elif self.n_players == 2:
            self.library_size = 24
            self.kings_per_player = 2
            self.n_dominoes_on_menu = 4

    def _set_up_dominoes_in_box(self):
        """
        Generates a randomly ordered list of self.library_size dominoes
        """
        random.shuffle(DOMINO_LIB)
        self.dominoes_in_box = DOMINO_LIB[:self.library_size]

    def draw_new_menu(self):
        """
        Grab dominoes from box
        """
        self.old_menu = copy.copy(self.new_menu)
        self.new_menu = self.dominoes_in_box[:self.n_dominoes_on_menu]
        self.new_menu.sort()

        self.dominoes_in_box = self.dominoes_in_box[self.n_dominoes_on_menu:]



    def setup(self):
        """
        This would erase/ruin an ongoing game, so only run once at the beginning!
        """
        self._set_up_dominoes_in_box()
