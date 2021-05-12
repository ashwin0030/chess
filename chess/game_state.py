from game_state import GameState
from chess.moves import ChessMoveSet
from constants import BLACK, WHITE


class ChessGameState(GameState):
    def all_possible_moves(self, side=None):
        if not side:
            side = self._current_side
        pieces = self._board.pieces_iterator(side)
        # uses CheckersMoveSet to enforce restriction on basic moves when at least once piece has a jump
        options = ChessMoveSet()
        for piece in pieces:
            options.extend(piece.enumerate_moves())

        return options



    def check_loss(self, side=None):
        #Do some sort of logic to check if player cant escape check
        if not side:
            side = self._current_side
        # no more pieces
        # pieces = list()
        for piece in self._board.pieces_iterator(side):
            if piece._val == 100:
                return False
        return True
