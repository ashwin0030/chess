import random
from constants import LOSS, WIN, BLACK, WHITE
from copy import deepcopy

class Player:
    "Abstract player class"

    def __init__(self, side=None) -> None:
        self.side = side

    def take_turn(self):
        raise NotImplementedError()

    @staticmethod
    def create_player(player_type):
        "Factory method for creating players"
        if player_type == "human":
            return HumanPlayer()
        elif player_type == "random":
            return RandomCompPlayer()
        elif player_type == "greedy":
            return GreedyCompPlayer()
        elif len(player_type) >= len("minimax2") and player_type[0:7] == "minimax":
            try:
                depth = int(player_type[7])
                return MiniMax(depth)
            except:
                return None
        else:
            return None


class HumanPlayer(Player):
    "Concrete player class that prompts for moves via the command line"

    def take_turn(self, game_state):
        b = game_state.board
        while True:
            chosen_piece = input("Select a piece to move\n")
            chosen_piece = b.get_space(chosen_piece).piece
            if chosen_piece is None:
                print("no piece at that location")
                continue
            if chosen_piece.side != self.side:
                print("that is not your piece")
                continue
            options = chosen_piece.enumerate_moves()
            if len(options) == 0 or options[0] not in game_state.all_possible_moves():

                print("that piece cannot move")
                continue

            self._prompt_for_move(options).execute(game_state)
            return

    def _prompt_for_move(self, options):
        while True:
            for idx, op in enumerate(options):
                print(f"{idx}: {op}")
            chosen_move = input(
                "Select a move by entering the corresponding index\n")
            try:
                chosen_move = options[int(chosen_move)]
                return chosen_move
            except ValueError:
                print("not a valid option")


class RandomCompPlayer(Player):
    "Concrete player class that picks random moves"

    def take_turn(self, game_state):
        options = game_state.all_possible_moves()
        m = random.choice(options)
        print(m)
        m.execute(game_state)


class GreedyCompPlayer(Player):
    "Concrete player class that chooses moves that capture the most pieces while breaking ties randomly"

    def take_turn(self, game_state):
        options = game_state.all_possible_moves()
        max_captured = 0
        potential_moves = []
        for m in options:
            if m.capture_value() > max_captured:
                potential_moves = [m]
                max_captured = m.capture_value()
            elif m.capture_value() == max_captured:
                potential_moves.append(m)

        selected_move = random.choice(potential_moves)
        print(selected_move)
        selected_move.execute(game_state)

class MiniMax(Player):
    "Fixed-depth minimax search AI"
    def __init__(self, depth, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._depth = depth
    def take_turn(self, game_state):
        best = self.doSearch(game_state, self._depth)
        move = best[1]
        print(move)
        move.execute(game_state)
    def doSearch(self, game_state, depth):
        if game_state.check_loss():
            if game_state._current_side == self.side:
                return [LOSS, None]
            return [WIN, None]
        elif game_state.check_draw():
            return [0, None]
        elif depth == 0:
            return [game_state.evaluate(self.side), None]

        if game_state._current_side == self.side:
            v = [LOSS, None]
            options = game_state.all_possible_moves()
            for i in range(len(options)):
                gs = deepcopy(game_state)
                move = (gs.all_possible_moves())[i]
                move.execute(gs)
                result = self.doSearch(gs, depth - 1)
                if result[0] > v[0]:
                    v[0] = result[0]
                    v[1] = options[i]
            return v
            
        else:
            v = [WIN, None]
            options = game_state.all_possible_moves()
            for i in range(len(options)):
                gs = deepcopy(game_state)
                move = (gs.all_possible_moves())[i]
                move.execute(gs)
                result = self.doSearch(gs, depth - 1)
                if result[0] < v[0]:
                    v[0] = result[0]
                    v[1] = options[i]
            return v
        return [LOSS, None]
