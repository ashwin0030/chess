from constants import BLACK, BOARD_SIZE, WHITE
from board import Board
from playersGUI import Player, HumanPlayer
from copy import deepcopy
import sys
import tkinter
import tkinter.font as font
from tkinter import ttk 
import time

from checkers.pieces import CheckerFactory
from checkers.game_state import CheckersGameState
from chess.pieces import ChessFactory
from chess.game_state import ChessGameState



class GameHistory():
    def __init__(self):
        # stack of old game states that can be reached with undo
        self._undo_stack = []

        # temporary stack of game states built as undo is called
        self._redo_stack = []

    def push(self, gs):
        """Saves a new game state and invalidates any potential redos

        Args:
            gs GameState): current game state to add to undo stack
        """
        self._undo_stack.append(gs)
        self._redo_stack = []

    def undo(self, gs):
        """
        Args:
            gs (GameState): current game state to add to redo stack. 

        Returns:
            GameState: previous game state from undo stack
        """

        if len(self._undo_stack) == 0:
            return None
        x = self._undo_stack.pop()
        self._redo_stack.append(gs)
        return x

    def redo(self, gs):
        """
        Args:
            gs (GameState): current game state to add to undo stack

        Returns:
            GameState: game state most recently added to redo stack by an undo
        """

        if len(self._redo_stack) == 0:
            return None
        self._undo_stack.append(gs)
        return self._redo_stack.pop()


class Menu:
    def __init__(self, player1=HumanPlayer(),
                 player2=HumanPlayer(),
                 history_enabled=False):
        print("does this happen2")
        self.window = tkinter.Tk()
        self.window.title("Chess GUI")
        # self.window.report_callback_exception = handle_exception

        self.board_frame = ttk.Frame(self.window)
        self.board_frame.grid(row=1, column=1, columnspan=2)

        self.button_frame = ttk.Frame(self.window)
        self.button_frame.grid(row=1, column=4, columnspan=1, sticky="e")

        self.message_frame = ttk.Frame(self.window)
        self.message_frame.grid(row=2, column=1, columnspan=1, sticky="e")

        
        b = Board(int(BOARD_SIZE), ChessFactory())
        if checkers:
            b = Board(int(BOARD_SIZE), CheckerFactory())
        b.set_up()
        self._game_state = ChessGameState(b, WHITE, None)
        if checkers:
            self._game_state = CheckersGameState(b, WHITE, None)

        # set up players
        self._players = {
            WHITE: player1,
            BLACK: player2
        }
        player1.side = WHITE
        player2.side = BLACK

        # set up history
        if history_enabled:
            self._history = GameHistory()
        self.history_enabled = history_enabled

        self._boardGUI = []
        myFont = font.Font(size=20)

        mRDark = ttk.Style()
        mRLight = ttk.Style()

        for x in range(self._game_state._board._size):
            self._boardGUI.append([])
            for y in range(self._game_state._board._size):
                if abs(x - y) % 2 == 0:
                    s = 'mRLight.TButton'
                else:
                    s = 'mRDark.TButton'

                if self._game_state._board._board[x][y]._piece:
                    text = (self._game_state._board._board[x][y]).draw()
                else:
                    text = ""

                # ttk.Style().configure('green/black.TButton', foreground='green', background='black',)

                mRDark.configure("mRDark.TButton", background="#56fca2", width=2, height=2, font=("Arial", 25))
                mRLight.configure("mRLight.TButton",background="white", width=2, height=2, font=("Arial", 25))
                mRDark.theme_use('alt')
                mRLight.theme_use('alt')
                
                self._boardGUI[x].append(ttk.Button(self.board_frame, text=text, style=s))
                # board[x][y]['font'] = myFont

                self._boardGUI[x][y].grid(row=x,column=y)
                self._boardGUI[x][y]['command'] = lambda x=x, y=y: self.button_click(x, y)

        self.prev_state = deepcopy(self._game_state)

        self._cur_player = self._players[self._game_state.current_side]

        if self.history_enabled:
            self._history.push(prev_state)

        if str(type(player1)) != "<class 'playersGUI.HumanPlayer'>" and str(type(player2)) != "<class 'playersGUI.HumanPlayer'>":
            self.bot_turn()
        elif str(type(self._cur_player)) != "<class 'playersGUI.HumanPlayer'>":
            self._cur_player.take_turn(self._game_state)
            self.refresh_colors()
            self._cur_player = self._players[self._game_state.current_side]

        self.window.mainloop()


    def bot_turn(self):
        if self._game_state.check_loss():
            self.end_game()
            return 

        self._cur_player.take_turn(self._game_state)
        self.refresh_colors()

        self.window.after(1000, self.bot_turn)

    def refresh_colors(self):
        if self._game_state.check_loss():
            # print("loss?")
            self.end_game()

        mRDark = ttk.Style()
        mRLight = ttk.Style()

        for x in range(self._game_state._board._size):
            self._boardGUI.append([])
            for y in range(self._game_state._board._size):
                if abs(x - y) % 2 == 0:
                    s = 'mRLight.TButton'
                else:
                    s = 'mRDark.TButton'

                if self._game_state._board._board[x][y]._piece:
                    text = (self._game_state._board._board[x][y]).draw()
                else:
                    text = ""

                mRDark.configure("mRDark.TButton", background="#56fca2", width=2, height=2, font=("Arial", 25))
                mRLight.configure("mRLight.TButton",background="white", width=2, height=2, font=("Arial", 25))
                mRDark.theme_use('alt')
                mRLight.theme_use('alt')
                
                self._boardGUI[x][y].configure(text=text, style=s)
                self._boardGUI[x][y]['command'] = lambda x=x, y=y: self.button_click(x, y)

    def update_player(self, player):
        # print("updating player")
        self._cur_player = player

    def button_click(self, x, y):
        self._game_state._button_selected = (x, y)
        # print(self._game_state._button_selected)
        # print(str(type(self._cur_player)))

        if str(type(self._cur_player)) == "<class 'playersGUI.HumanPlayer'>":
            self._cur_player.check_space(self._game_state, self._game_state._button_selected, self, self._boardGUI)



    def end_game(self):
        self.board_frame.destroy()
        self.board_frame = ttk.Frame(self.window)
        self.board_frame.grid(row=1, column=1, columnspan=2)

        mRDark = ttk.Style()
        mRLight = ttk.Style()

        self._boardGUI = []

        for x in range(self._game_state._board._size):
            self._boardGUI.append([])
            for y in range(self._game_state._board._size):
                if abs(x - y) % 2 == 0:
                    s = 'mRLight.TButton'
                else:
                    s = 'mRDark.TButton'

                if self._game_state._board._board[x][y]._piece:
                    text = (self._game_state._board._board[x][y]).draw()
                else:
                    text = ""

                mRDark.configure("mRDark.TButton", background="#56fca2", width=2, height=2, font=("Arial", 25))
                mRLight.configure("mRLight.TButton",background="white", width=2, height=2, font=("Arial", 25))
                mRDark.theme_use('alt')
                mRLight.theme_use('alt')
                
                self._boardGUI[x].append(ttk.Button(self.board_frame, text=text, style=s))

                self._boardGUI[x][y].grid(row=x,column=y)
                self._boardGUI[x][y]['command'] = None

        self.message_frame.destroy()

        self.message_frame = ttk.Frame(self.window)
        self.message_frame.grid(row=2, column=1, columnspan=1, sticky="e")

        if self._game_state.current_side == WHITE:
            ttk.Label(self.message_frame, text = "BLACK HAS WON!").pack()
        else:
            ttk.Label(self.message_frame, text = "WHITE HAS WON!").pack()
        
        return

    def execute_move(self, move):
        move.execute(self._game_state)
        self.refresh_colors()

        self._cur_player = self._players[self._game_state.current_side]

        if self._game_state.check_loss():
            self.end_game()

        if str(type(self._cur_player)) != "<class 'playersGUI.HumanPlayer'>":
            self._cur_player.take_turn(self._game_state)
            self.refresh_colors()
            self._cur_player = self._players[self._game_state.current_side]

if __name__ == "__main__":

    # take in arguments and setup defaults if necessary
    #print("Starting")
    checkers = False
    if len(sys.argv) > 1:
        if sys.argv[1] == "checkers":
            checkers = True

    if len(sys.argv) > 2:
        player1 = Player.create_player(sys.argv[2])
        if not player1:
            sys.exit()
    else:
        player1 = Player.create_player("human")
    if len(sys.argv) > 3:
        player2 = Player.create_player(sys.argv[3])
        if not player2:
            sys.exit()
    else:
        player2 = Player.create_player("human")

    history = len(sys.argv) > 4 and sys.argv[4] == "on"

    # create driver and start game
    # game = GameDriver(player1, player2, history, checkers)
    # game.start_game()

    m = Menu(player1, player2, history)
