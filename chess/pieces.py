from piece import Piece
from piece_factory import PieceFactory
from constants import BLACK, WHITE
from chess.moves import ChessMove, ChessMoveSet


class ChessFactory(PieceFactory):
    "Concrete piece factory for setting up a chess game"

    def create_piece(self, board, space):
        x = space.row
        y = space.col
        if x < 3 and abs(x - y) % 2 == 0:
            return Checker(BLACK, board, space)
        if board.size - x < 4 and abs(x - y) % 2 == 0:
            return Checker(WHITE, board, space)
        return None

class Pawn(Piece):
    "Concrete piece class for a basic checker or 'peasant'"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._cap_directions = ["ne", "nw"]
        if self._side == WHITE:
            self._symbol = u"⚆"
            self._directions = ["n"]
        if self._side == BLACK:
            self._symbol = u"⚈"
            self._directions = ["s"]
            self._cap_directions = ["se", "sw"]

    def enumerate_moves(self):
        moves = ChessMoveSet()
        #2-step moves for pawns
        if (self._side == WHITE and self._current_space.row == 6) or (self._side == BLACK and self._current_space.row == 1):
            direction = self._directions[0]
            step = self._board.get_dir(self._current_space, direction)
            if step and step.is_free():
                step = self._board.get_dir(step, direction)
            if step and step.is_free():
                m = ChessMove(self._current_space, step)
                moves.append(m)
        # basic moves
        for direction in self._directions:
            one_step = self._board.get_dir(self._current_space, direction)
            if one_step and one_step.is_free():
                m = CheckersMove(self._current_space, one_step)
                moves.append(m)
                if (self._side == WHITE and one_step.row == 0) or \
                        (self._side == BLACK and one_step.row == self._board.size - 1):
                    m.add_promotion()
        
        for direction in self._cap_directions:
            pass

        return moves

    # def _enumerate_jumps(self, moves, current_space, captured, midjump=False):
    #     """Recursive helper function for finding jump moves

    #     Args:
    #         moves (CheckersMoveSet): set to which moves are added when found
    #         current_space (Space): space from which jump moves are currently being sought
    #         captured (list): pieces captured thus far
    #         midjump (bool, optional): flag used to avoid adding moves when no jumps have been made. Defaults to False.
    #     """
    #     done_jumping = True
    #     # recursive cases making up to 4 additional branching calls
    #     for direction in self._directions:
    #         one_step = self._board.get_dir(current_space, direction)

    #         if one_step and not one_step.is_free() and one_step.piece.side != self._side and one_step not in captured:
    #             two_steps = self._board.get_dir(one_step, direction)
    #             if two_steps and two_steps.is_free() or two_steps == self._current_space:
    #                 # use + creates a shallow copy of captured so that each branch has a different list. the spaces themselves are the same objects
    #                 self._enumerate_jumps(
    #                     moves, two_steps, captured + [one_step], midjump=True)
    #                 done_jumping = False
    #     # base case. found no more jumps. time to create the move
    #     if midjump and done_jumping:
    #         m = CheckersMove(self._current_space, current_space, captured)
    #         if ((self._side == WHITE and current_space.row == 0) or
    #                 (self._side == BLACK and current_space.row == self._board.size - 1)):
    #             m.add_promotion()
    #         moves.append(m)

    def promote(self):
        "Overrides promote to return a KingChecker in the same space for the same side"
        return Queen(self._side, self._board, self._current_space)


# class KingChecker(Checker):
#     "Same as a basic checker except that it can move in all 4 directions, has a different symbol, and cannot be promoted further"

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self._directions = ["ne", "nw", "se", "sw"]
#         if self._side == WHITE:
#             self._symbol = u"⚇"
#         if self._side == BLACK:
#             self._symbol = u"⚉"

#     def promote(self):
#         "Override promote to return self since a king cannot be promoted further"
#         return self
