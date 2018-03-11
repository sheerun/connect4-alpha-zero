import enum
import numpy as np

from logging import getLogger

logger = getLogger(__name__)

# noinspection PyArgumentList
Winner = enum.Enum("Winner", "black white draw")

# noinspection PyArgumentList
Player = enum.Enum("Player", "black white")


class Connect4Env:
    def __init__(self):
        self.board = None
        self.turn = 0
        self.done = False
        self.winner = None  # type: Winner
        self.resigned = False

    def reset(self):
        self.board = []
        for i in range(4):
            self.board.append([])
            for j in range(16):
                self.board[i].append(' ')
        self.turn = 0
        self.done = False
        self.winner = None
        self.resigned = False
        return self

    def update(self, board):
        self.board = np.copy(board)
        self.turn = self.turn_n()
        self.done = False
        self.winner = None
        self.resigned = False
        return self

    def turn_n(self):
        turn = 0
        for i in range(4):
            for j in range(16):
                if self.board[i][j] != ' ':
                    turn += 1

        return turn

    def player_turn(self):
        if self.turn % 2 == 0:
            return Player.white
        else:
            return Player.black

    # action = 0-15
    # board: level, [height*width]
    def step(self, action):
        if action is None:
            self._resigned()
            return self.board, {}

        for i in range(4):
            if self.board[i][action] == ' ':
                self.board[i][action] = ('X' if self.player_turn() == Player.white else 'O')
                break

        self.turn += 1

        self.check_for_fours()

        if self.turn > 64:
            self.done = True
            if self.winner is None:
                self.winner = Winner.draw

        return self.board, {}

    def legal_moves(self):
        legal = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        for j in range(16):
            for i in range(4):
                if self.board[i][j] == ' ':
                    legal[j] = 1
                    break

        return legal

    def check_for_fours(self):
        for a in range(4):
            for b in range(4):
                if self.four_check(a, b, 0, 0, 0, 1):
                    self.done = True
                    return
                if self.four_check(a, 0, b, 0, 1, 0):
                    self.done = True
                    return
                if self.four_check(0, a, b, 1, 0, 0):
                    self.done = True
                    return

        # first corner
        if self.four_check(0, 0, 0, 0, 1, 1):
            self.done = True
            return
        if self.four_check(0, 0, 0, 1, 1, 0):
            self.done = True
            return
        if self.four_check(0, 0, 0, 1, 0, 1):
            self.done = True
            return
        if self.four_check(0, 0, 0, 1, 1, 1):
            self.done = True
            return

        # second corner
        if self.four_check(0, 3, 0, 0, -1, 1):
            self.done = True
            return
        if self.four_check(0, 3, 0, 1, -1, 0):
            self.done = True
            return
        if self.four_check(0, 3, 0, 1, 0, 1):
            self.done = True
            return
        if self.four_check(0, 3, 0, 1, -1, 1):
            self.done = True
            return

        # third corner
        if self.four_check(0, 3, 3, 0, -1, -1):
            self.done = True
            return
        if self.four_check(0, 3, 3, 1, -1, 0):
            self.done = True
            return
        if self.four_check(0, 3, 3, 1, 0, -1):
            self.done = True
            return
        if self.four_check(0, 3, 3, 1, -1, -1):
            self.done = True
            return

        # fourth corner
        if self.four_check(0, 0, 3, 0, 1, -1):
            self.done = True
            return
        if self.four_check(0, 0, 3, 1, 1, 0):
            self.done = True
            return
        if self.four_check(0, 0, 3, 1, 0, -1):
            self.done = True
            return
        if self.four_check(0, 0, 3, 1, 1, -1):
            self.done = True
            return


    def four_check(self, i0, x, y, di, dx, dy):
        if ' ' == self.board[i0][x + y*4].lower():
            return False

        four_in_a_row = False
        consecutive_count = 0

        for d in range(4):
            i = i0 + d*di
            j = x+d*dx + y*4+d*dy*4
            if self.board[i][j].lower() == self.board[i0][x + y*4].lower():
                consecutive_count += 1
            else:
                break

        if consecutive_count >= 4:
            four_in_a_row = True
            if 'x' == self.board[i0][x + y*4].lower():
                self.winner = Winner.white
            else:
                self.winner = Winner.black

        return four_in_a_row

    def _resigned(self):
        if self.player_turn() == Player.white:
            self.winner = Winner.white
        else:
            self.winner = Winner.black
        self.done = True
        self.resigned = True

    def black_and_white_plane(self):
        board_white = np.copy(self.board)
        board_black = np.copy(self.board)
        for i in range(4):
            for j in range(16):
                if self.board[i][j] == ' ':
                    board_white[i][j] = 0
                    board_black[i][j] = 0
                elif self.board[i][j] == 'X':
                    board_white[i][j] = 1
                    board_black[i][j] = 0
                else:
                    board_white[i][j] = 0
                    board_black[i][j] = 1

        return np.array(board_white), np.array(board_black)

    def render(self):
        print("\nRound: " + str(self.turn))


        for y in range(3, -1, -1):
            print("\n| ", end="")
            for i in range(4):
                for x in range(4):
                    print(str(self.board[i][y*4+x]), end=" ")
                print("| ", end="")

        print("\n", end="")

        if self.done:
            print("Game Over!")
            if self.winner == Winner.white:
                print("X is the winner")
            elif self.winner == Winner.black:
                print("O is the winner")
            else:
                print("Game was a draw")

    @property
    def observation(self):
        return ''
