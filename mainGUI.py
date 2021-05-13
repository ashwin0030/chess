from constants import BLACK, BOARD_SIZE, WHITE
from board import Board
from playersGUI import Player, HumanPlayer
from copy import deepcopy
import sys
import tkinter
import tkinter.font as font
import random as rand
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
        self.window = tkinter.Tk()
        self.window.title("Chess GUI")
        # self.window.report_callback_exception = handle_exception

        self.title_frame = ttk.Frame(self.window)
        self.title_frame.grid(row=0, column=1, columnspan=2)

        self.board_frame = ttk.Frame(self.window)
        self.board_frame.grid(row=1, column=1, columnspan=2)

        self.button_frame = ttk.Frame(self.window)
        self.button_frame.grid(row=1, column=4, columnspan=1, sticky="e")

        self.message_frame = ttk.Frame(self.window)
        self.message_frame.grid(row=2, column=1, columnspan=2, sticky="e")

        self.random_frame = ttk.Frame(self.window)
        self.random_frame.grid(row=3, column=1, columnspan=1, sticky="e")

        
        b = Board(int(BOARD_SIZE), ChessFactory())
        if checkers:
            b = Board(int(BOARD_SIZE), CheckerFactory())
        b.set_up()
        self._game_state = ChessGameState(b, WHITE, None)
        if checkers:
            self._game_state = CheckersGameState(b, WHITE, None)


        self.light_colors = ["#FFC5B8", "#FFE9B8", "#E2FFB8", "#B8FFD9", "#B8F6FF", "#B8DAFF", "#C0B8FF", "#E6B8FF", "#FFB8FF", "#FFB8D4", "#6AFFDA", "#FF6A6A"]
        self.light_color = "#56fca2"
        random_button = ttk.Button(self.random_frame, text="Randomize Color Scheme")
        random_button['command'] = lambda random=True: self.refresh_colors(random)
        random_button.pack()

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
            self._last_state = None
            self._next_state = None
            self._next_called = True


            ttk.Button(self.button_frame, text="Undo", command=self.undo_board).pack()
            ttk.Button(self.button_frame, text="Redo", command=self.redo_board).pack()
            ttk.Button(self.button_frame, text="Next", command=self.next_board).pack()

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
        ttk.Label(self.title_frame, text = str(self._game_state).split("\n")[-1]).pack()

        if self.history_enabled:
            self._history.push(self.prev_state)

        if not self.history_enabled and str(type(player1)) != "<class 'playersGUI.HumanPlayer'>" and str(type(player2)) != "<class 'playersGUI.HumanPlayer'>":
            self.bot_turn()
        elif str(type(self._cur_player)) != "<class 'playersGUI.HumanPlayer'>":
            self._cur_player.take_turn(self._game_state)
            self.refresh_colors()
            self._cur_player = self._players[self._game_state.current_side]

        self.window.mainloop()


    def undo_board(self):
        self._last_state = self._history.undo(self._game_state)
        if self._last_state:
            self._game_state = self._last_state

        self.refresh_colors()
        self._cur_player = self._players[self._game_state.current_side]
        self._next_called = False

    def redo_board(self):
        self._next_state = self._history.redo(self._game_state)
        if self._next_state:
            self._game_state = self._next_state
        self.refresh_colors()
        self._cur_player = self._players[self._game_state.current_side]
        self._next_called = False

    def next_board(self):
        self.prev_state = deepcopy(self._game_state)

        self._cur_player = self._players[self._game_state.current_side]
        self._next_called = True

        if self.history_enabled:
            self._history.push(self.prev_state)

            if str(type(self._cur_player)) != "<class 'playersGUI.HumanPlayer'>":
                self._cur_player.take_turn(self._game_state)
                self.refresh_colors()
                self._cur_player = self._players[self._game_state.current_side]
                self._next_called = True

    def bot_turn(self):
        if self._game_state.check_loss():
            self.end_game()
            return 

        self._cur_player.take_turn(self._game_state)
        self.refresh_colors()

        self.window.after(1000, self.bot_turn)

    def refresh_colors(self, random=False):
        if self._game_state.check_loss():
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

                if random:
                    self.light_color = rand.choice(self.light_colors)

                mRDark.configure("mRDark.TButton", background=self.light_color, width=2, height=2, font=("Arial", 25))
                mRLight.configure("mRLight.TButton",background="white", width=2, height=2, font=("Arial", 25))
                mRDark.theme_use('alt')
                mRLight.theme_use('alt')
                
                self._boardGUI[x][y].configure(text=text, style=s)
                self._boardGUI[x][y]['command'] = lambda x=x, y=y: self.button_click(x, y)

        self.title_frame.destroy()
        self.title_frame = ttk.Frame(self.window)
        self.title_frame.grid(row=0, column=1, columnspan=2)
        ttk.Label(self.title_frame, text = str(self._game_state).split("\n")[-1]).pack()

    def update_player(self, player):
        # print("updating player")
        self._cur_player = player

    def button_click(self, x, y):
        self._game_state._button_selected = (x, y)
        # print(self._game_state._button_selected)
        # print(str(self._cur_player.side))

        player_human = str(type(self._cur_player)) == "<class 'playersGUI.HumanPlayer'>"
        if (self._history and self._next_called and player_human) or (not self._history and player_human): 
            self._cur_player.check_space(self._game_state, self._game_state._button_selected, self, self._boardGUI)
            
    def end_game(self):
        self.board_frame.destroy()
        self.board_frame = ttk.Frame(self.window)
        self.board_frame.grid(row=1, column=1, columnspan=2)
        self.title_frame.destroy()
        self.button_frame.destroy()
        self.random_frame.destroy()

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
        self.message_frame.grid(row=2, column=1, columnspan=2, sticky="e")

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

        if (str(type(self._cur_player)) != "<class 'playersGUI.HumanPlayer'>") and (not self.history_enabled):
            self._cur_player.take_turn(self._game_state)
            self.refresh_colors()
            self._cur_player = self._players[self._game_state.current_side]

        self._next_called = False

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
