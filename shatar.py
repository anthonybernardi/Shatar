from pieces import Pawn, King, Rook, Bishop, Tiger, Knight, square_is_threatened, find_king

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


class ShatarModel(object):
    """ Class that runs a model of Shatar. Contains the board and all rules for the board.

    Attributes:
        board (2d array): represents the board of pieces. None if no piece on a square
        to_play (boolean): True if white_to_play, False otherwise
    """

    def __init__(self, board=DEFAULT_BOARD, last_moved_from=(6, 3), last_moved_to=(4, 3)):
        self.board = board
        self.to_play = WHITE_TO_PLAY
        self.last_moved_from = last_moved_from
        self.last_moved_to = last_moved_to

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
            raise ValueError("Piece: " + str(piece) + " cannot make this move!")

        if from_row == to_row and from_col == to_col:
            raise ValueError("Can't move to the same square")

        self.board[to_row][to_col] = self.board[from_row][from_col]
        self.board[from_row][from_col] = None

        if (str(piece) == 'P' and to_row == 7) or (str(piece) == 'p' and to_row == 0):
            self.board[to_row][to_col] = Tiger(white=piece.white)

        # TODO - check if now in check and if so update check sequence, if not clear the check sequence

        self.last_moved_from = from_row, from_col
        self.last_moved_to = to_row, to_col
        self.to_play = not self.to_play

    def get_piece_at(self, row, col):
        """ Get the piece at the given row and column on this board

        :param row: (int) given row
        :param col: (int) given column
        :return: the piece at this square or None
        """
        return self.board[row][col]

    def is_in_check(self, white):
        """ Returns true if in check

        :param white: (boolean) True if checking if white is in check, false if black
        :return: True if the given color is in check
        """

        king_row, king_col = find_king(self.board, white)

        return square_is_threatened(self.board, king_row, king_col, white)

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
        # TODO - make a copy of the board probably
        return self.board

    def is_game_over(self):
        """ Determines if the game is over

        :return: 1 if white wins, 0 if draw, -1 if black wins
        """
        # TODO - make this return the right values and account for checks and stuff
        if len(self.generate_legal_moves()) == 0:
            # If white to play and white has no moves, black has won (not really, need to fix this lol)
            if self.to_play:
                return -1
            # otherwise white must have won (not really lol)
            else:
                return 1

    def generate_legal_moves(self, white):
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

# model = ShatarModel()
# print(model)
