from piece import Piece
from piece_factory import PieceFactory
from constants import BLACK, WHITE
from chess.moves import ChessMove, ChessMoveSet


class ChessFactory(PieceFactory):
    "Concrete piece factory for setting up a chess game"

    def create_piece(self, board, space):
        x = space.row
        y = space.col
        if x == 0 and (y == 0 or y == board.size - 1):
            return Rook(BLACK, board, space)
        elif x == 0 and (y == 1 or y == board.size - 2):
            return Knight(BLACK, board, space)
        elif x == 0 and (y == 2 or y == board.size - 3):
            return Bishop(BLACK, board, space)
        elif x == 0 and y == 3:
            return Queen(BLACK, board, space)
        elif x == 0:
            return King(BLACK, board, space)
        elif x == 1:
            return Pawn(BLACK, board, space)

        if x == board.size-1 and (y == 0 or y == board.size - 1):
            return Rook(WHITE, board, space)
        elif x == board.size-1 and (y == 1 or y == board.size - 2):
            return Knight(WHITE, board, space)
        elif x == board.size-1 and (y == 2 or y == board.size - 3):
            return Bishop(WHITE, board, space)
        elif x == board.size-1 and y == 3:
            return Queen(WHITE, board, space)
        elif x == board.size-1:
            return King(WHITE, board, space)
        elif x == board.size-2:
            return Pawn(WHITE, board, space)
        
        return None

class ChessPiece(Piece):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self._side == WHITE:
            self._symbol = u"⚆"
            self._directions = []
        if self._side == BLACK:
            self._symbol = u"⚈"
            self._directions = []
    def enumerate_moves(self):
        moves = ChessMoveSet()
        done_jumping = True
        for direction in self._directions:
            one_step = self._board.get_dir(self._current_space, direction)
            while one_step and one_step.is_free():
                m = ChessMove(self._current_space, one_step, [])
                moves.append(m)
                one_step = self._board.get_dir(one_step, direction)
            if one_step and not one_step.is_free():
                if one_step.piece.side != self._side:
                    m = ChessMove(self._current_space, one_step, [one_step])
                    moves.append(m)
                    continue
                else:
                    continue
        return moves

class Bishop(ChessPiece):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._val = 3
        self._directions = ["ne", "nw", "se", "sw"]
        if self._side == WHITE:
            self._symbol = u"♗"    
        if self._side == BLACK:
            self._symbol = u"♝"


class Rook(ChessPiece):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._val = 5
        self._directions = ["n", "s", "e", "w"]
        if self._side == WHITE:
            self._symbol = u"♖"    
        if self._side == BLACK:
            self._symbol = u"♜"

class Queen(ChessPiece):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._val = 9
        self._directions = ["n", "s", "e", "w", "ne", "nw", "se", "sw"]
        if self._side == WHITE:
            self._symbol = u"♕"    
        if self._side == BLACK:
            self._symbol = u"♛"

class Knight(Piece):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._val = 3
        if self._side == WHITE:
            self._symbol = u"♘"    
        if self._side == BLACK:
            self._symbol = u"♞"
    def enumerate_moves(self):
        moves = ChessMoveSet()
        dir1 = ["n", "e", "s", "w"]
        dir2 = ["e", "s", "w", "n"]
        dir3 = ["w", "n", "e", "s"]

        for i, direction in enumerate(dir1):
            one_step = self._board.get_dir(self._current_space, direction)
            if not one_step:
                continue
            two_step = self._board.get_dir(one_step, direction)
            if not two_step:
                continue
            turn1 = self._board.get_dir(two_step, dir2[i])
            turn2 = self._board.get_dir(two_step, dir3[i])
            for turn in [turn1, turn2]:
                if turn and not turn.is_free():
                    if turn.piece.side != self._side:
                        m = ChessMove(self._current_space, turn, [turn])
                        moves.append(m)
                    else:
                        continue
                elif turn and turn.is_free():
                    m = ChessMove(self._current_space, turn)
                    moves.append(m)
        
        return moves

class King(Piece):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._directions = ["n", "s", "e", "w", "ne", "nw", "se", "sw"]
        self._val = 100
        if self._side == WHITE:
            self._symbol = u"♔"    
        if self._side == BLACK:
            self._symbol = u"♚"
    def enumerate_moves(self):
        moves = ChessMoveSet()
        for direction in self._directions:
            one_step = self._board.get_dir(self._current_space, direction)
            if one_step and one_step.is_free():
                m = ChessMove(self._current_space, one_step)
                moves.append(m)
            elif one_step and not one_step.is_free():
                m = ChessMove(self._current_space, one_step, [one_step])
                moves.append(m)
        return moves
        


class Pawn(Piece):
    "Concrete piece class for a basic checker or 'peasant'"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._val = 1
        self._cap_directions = ["ne", "nw"]
        if self._side == WHITE:
            self._symbol = u"♙"
            self._directions = ["n"]
        if self._side == BLACK:
            self._symbol = u"♟︎"
            self._directions = ["s"]
            self._cap_directions = ["se", "sw"]

    def enumerate_moves(self):
        moves = ChessMoveSet()

        if (self._side == WHITE and self._current_space.row == self._board.size - 2) or \
                (self._side == BLACK and self._current_space.row == 1):
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
                m = ChessMove(self._current_space, one_step)
                moves.append(m)
                if (self._side == WHITE and one_step.row == 0) or \
                        (self._side == BLACK and one_step.row == self._board.size - 1):
                    m.add_promotion()
        
        for direction in self._cap_directions:
            one_step = self._board.get_dir(self._current_space, direction)
            if one_step and not one_step.is_free() and one_step.piece.side != self._side:
                m = ChessMove(self._current_space, one_step, [one_step])
                moves.append(m)
                if (self._side == WHITE and one_step.row == 0) or \
                        (self._side == BLACK and one_step.row == self._board.size - 1):
                    m.add_promotion()

        return moves

    def promote(self):
        "Overrides promote to return a Queen in the same space for the same side"
        return Queen(self._side, self._board, self._current_space)