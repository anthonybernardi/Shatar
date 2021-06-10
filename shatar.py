from pieces import Pawn, King, Rook, Bishop, Tiger, Knight, square_is_threatened, find_king, piece_threatens_square
from copy import deepcopy

NUM_COLS = 8
# With these constant values for players, flipping ownership is just a sign change
WHITE = 1
NOBODY = 0
BLACK = -1

TIE = 2  # NOT the value of a tie, which is 0 - just an arbitrary enum for end-of-game

WIN_VAL = 100
WHITE_TO_PLAY = True
DEMO_SEARCH_DEPTH = 5

DIRECTIONS = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

DEFAULT_BOARD = [[Rook(), Knight(), Bishop(), Tiger(), King(), Bishop(), Knight(), Rook()],
                 [Pawn(), Pawn(), Pawn(), None, Pawn(), Pawn(), Pawn(), Pawn()],
                 [None, None, None, None, None, None, None, None],
                 [None, None, None, Pawn(), None, None, None, None],
                 [None, None, None, Pawn(white=False), None, None, None, None],
                 [None, None, None, None, None, None, None, None],
                 [Pawn(white=False), Pawn(white=False), Pawn(white=False), None, Pawn(white=False),
                  Pawn(white=False), Pawn(white=False), Pawn(white=False), ],
                 [Rook(white=False), Knight(white=False), Bishop(white=False), Tiger(white=False), King(white=False),
                  Bishop(white=False), Knight(white=False), Rook(white=False)]]


def fen_to_board(fen):
    board = []

    fen_rows = fen.split('/')
    fen_rows.reverse()

    for fen_row in fen_rows:
        row = []
        for i in range(len(fen_row)):
            curr = fen_row[i]
            if curr.isnumeric():
                for j in range(int(curr)):
                    row.append(None)
            else:
                row.append(str_to_piece(curr))
        board.append(row)

    return board


def str_to_piece(piece):
    if piece == 'n':
        return Knight(white=False)
    elif piece == 'N':
        return Knight()
    elif piece == 'q':
        return Tiger(white=False)
    elif piece == 'Q':
        return Tiger()
    elif piece == 'k':
        return King(white=False)
    elif piece == 'K':
        return King()
    elif piece == 'b':
        return Bishop(white=False)
    elif piece == 'B':
        return Bishop()
    elif piece == 'p':
        return Pawn(white=False)
    elif piece == 'P':
        return Pawn()
    elif piece == 'r':
        return Rook(white=False)
    elif piece == 'R':
        return Rook()


class ShatarModel(object):
    """ Class that runs a model of Shatar. Contains the board and all rules for the board.

    Attributes:
        board (2d array): represents the board of pieces. None if no piece on a square
        to_play (boolean): True if white_to_play, False otherwise
        shak_sequence_white (boolean): True if there is currently a check sequence for white that contains a check by a Rook, Knight, or Tiger (Queen)
    """

    def __init__(self, board=DEFAULT_BOARD, last_moved_from=(6, 3), last_moved_to=(4, 3), to_play=WHITE_TO_PLAY):
        self.board = board
        self.to_play = to_play
        self.last_moved_from = last_moved_from
        self.last_moved_to = last_moved_to
        self.shak_sequence_white = False
        self.shak_sequence_black = False
        self.moves_since_last_capture = 0
        self.total_moves = 0

    def move(self, from_row, from_col, to_row, to_col):
        """ Move on the board from the given square to the other given square.
            Throws exceptions if it's bad for any reason

        :param from_row:
        :param from_col:
        :param to_row:
        :param to_col:
        :return:
        """
        piece = self.board[from_row][from_col]

        if piece is None:
            raise ValueError("Piece to move does not exist!")

        if not (piece.white == self.to_play):
            raise ValueError("This piece is the wrong color to move!")

        if not piece.is_legal_move(self.board, from_row, from_col, to_row, to_col):
            raise ValueError(
                "Piece: " + str(piece) + " cannot make this move! " + f'{from_row}, {from_col}, {to_row}, {to_col}')

        if from_row == to_row and from_col == to_col:
            raise ValueError("Can't move to the same square")

        if self.board[to_row][to_col] is not None:
            self.moves_since_last_capture = 0
        else:
            self.moves_since_last_capture += 1

        self.board[to_row][to_col] = self.board[from_row][from_col]
        self.board[from_row][from_col] = None

        if (str(piece) == 'P' and to_row == 7) or (str(piece) == 'p' and to_row == 0):
            self.board[to_row][to_col] = Tiger(white=piece.white)

        self.update_checking_sequence()
        self.total_moves += 1
        self.last_moved_from = from_row, from_col
        self.last_moved_to = to_row, to_col
        self.to_play = not self.to_play

    def update_checking_sequence(self):
        # if the opposite color of what just played is now in check:
        checking_piece = self.get_piece_causing_check(not self.to_play)
        if checking_piece is not None:
            shak = isinstance(checking_piece, Rook) or isinstance(checking_piece, Tiger) or \
                   isinstance(checking_piece, Knight)
            # update the shak sequence to be include this possible shak
            if self.to_play:
                self.shak_sequence_white = self.shak_sequence_white or shak
            else:
                self.shak_sequence_black = self.shak_sequence_black or shak
        # if this isn't a check, the check sequence must be over so just make it false
        else:
            if self.to_play:
                self.shak_sequence_white = False
            else:
                self.shak_sequence_black = False
        # at the end of this, black could be in checkmate and white could have a True shak sequence and it would be gg

    def get_piece_at(self, row, col):
        """ Get the piece at the given row and column on this board

        :param row: (int) given row
        :param col: (int) given column
        :return: the piece at this square or None
        """
        return self.board[row][col]

    def is_in_check(self, white):
        """ Returns true if the given color is in check

        :param white: (boolean) True if checking if white is in check, false if black
        :return: True if the given color is in check
        """
        return self.get_piece_causing_check(white) is not None

    def get_piece_causing_check(self, white):
        """ Returns the piece putting the given color in check, otherwise None

        :param white: (boolean) True if checking if white is in check, false if black
        :return: A piece or None
        """

        king_row, king_col = find_king(self.board, white)

        return piece_threatens_square(self.board, king_row, king_col, not white)

    def __str__(self):
        b = ''
        for i in range(len(self.board)):
            for j in range(len(self.board[0])):
                square = self.board[7 - i][j]
                if square is None:
                    b += '-\t'
                else:
                    b += str(square) + '\t'
            b += '\n'
        return b

    def get_board(self):
        """ Return the current state of the board

        :return: (2d list) current Shatar board
        """
        new_board = []
        for i in range(len(self.board)):
            row = []
            for j in range(len(self.board[0])):
                piece = self.board[i][j]
                if piece is None:
                    row.append(None)
                else:
                    row.append(deepcopy(piece))
            new_board.append(row)

        return new_board

    def is_game_over(self):
        """ Determines if the game is over

        :return: 1 if white wins, 0 if draw, -1 if black wins, 2 if game is not over
        """
        # TODO - three fold repetition!!!
        # if a player only has a king, it's a DRAW
        if self.only_has_king(self.to_play):
            return 0

        # if to_play has no legal moves
        if len(self.generate_legal_moves()) == 0:
            # get the shak for the opposite player
            shak = self.shak_sequence_black
            if not self.to_play:
                shak = self.shak_sequence_white

            piece = self.get_piece_causing_check(self.to_play)
            # if knight is giving this check or there is no shak sequence it is a draw
            # or if the piece is none that would mean stalemate which we'll say is a draw
            if piece is None or isinstance(piece, Knight) or not shak:
                return 0
            else:
                # if white to play, that means black has won so return -1
                if self.to_play:
                    return -1
                # opposite
                else:
                    return 1

        # if no captures in 50 moves: draw
        if self.moves_since_last_capture >= 100:
            return 0

        # there actually are legal moves and it's not a draw so the game is not over
        return 2

    def generate_legal_moves(self):
        """ Generates all the legal moves for the to_play player in the current board's position

        :return: (list) of moves that are tuples in the format: (from_row, from_col, to_row, to_col)
        """
        moves = []
        for i in range(len(self.board)):
            for j in range(len(self.board[0])):
                piece = self.board[i][j]
                if piece is not None and piece.white == self.to_play:
                    piece_moves = piece.generate_legal_moves(self.board, i, j)
                    for move in piece_moves:
                        moves.append(move)
        return moves

    def only_has_king(self, white):
        """ Return True if the given color only has a King left on the board. """
        count = 0
        for i in range(len(self.board)):
            for j in range(len(self.board[0])):
                piece = self.board[i][j]
                if piece is None:
                    continue
                if piece.white == white and not isinstance(piece, King):
                    return False
                elif piece.white == white:
                    count += 1
        return count == 1


TOUGH_BOARD = [[King(), None, None, None, None, None, None, None],
               [Tiger(), None, None, None, None, None, None, None],
               [None, None, None, None, None, None, None, None],
               [None, None, None, None, None, None, Pawn(white=False), None],
               [None, None, None, None, None, None, None, None],
               [None, Pawn(), None, None, None, None, None, None],
               [Pawn(white=False), None, None, None, None, None, None, None],
               [King(white=False), None, None, None, None, None, None, None]]

# model = ShatarModel(board=TOUGH_BOARD)
# print(model.is_game_over())
# model.move(1, 0, 6, 0)
# r = model.is_game_over()
# print(model.generate_legal_moves())
# print(r)
# x = fen_to_board("rnbq2nr/pp1ppppp/4b3/2k5/3P1p2/8/PPP1PPPP/RNBQKBNR")
# fen = "rnbq2nr/pp1ppppp/4b3/2k5/3P1p2/8/PPP1PPPP/RNBQKBNR"
# print(x)
