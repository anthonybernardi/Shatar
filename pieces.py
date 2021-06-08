KING_DIRECTIONS = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
ROOK_DIRECTIONS = [(1, 0), (-1, 0), (0, 1), (0, -1)]
KNIGHT_DIRECTIONS = [(2, 1), (2, -1), (1, 2), (1, -2), (-2, 1), (-2, -1), (-1, 2), (-1, -2)]


def puts_self_in_check(board, from_row, from_col, to_row, to_col, white):
    """ Determines if the given move puts the given color in check

    :param board:
    :param from_row:
    :param from_col:
    :param to_row:
    :param to_col:
    :param white: (boolean) True if checking if the given move puts white in check
    :return:
    """
    backup_from = board[from_row][from_col]
    backup_to = board[to_row][to_col]

    board[to_row][to_col] = board[from_row][from_col]
    board[from_row][from_col] = None

    king_row, king_col = find_king(board, white)

    in_check = square_is_threatened(board, king_row, king_col, not white)

    board[from_row][from_col] = backup_from
    board[to_row][to_col] = backup_to

    return in_check


def square_is_threatened(board, row, col, white):
    """ True if the given color has a piece that can see the given square

    :param board:
    :param row:
    :param col:
    :param white:
    :return:
    """
    for i in range(len(board)):
        for j in range(len(board)):
            piece = board[i][j]
            if piece is not None and piece.white == white and piece.is_threatening(board, i, j, row, col):
                return True
    return False


def is_invalid_indices(row, col):
    """ Return true if an invalid index is given

    :param row: row
    :param col: col
    :return: true if given index is invalid for a shatar board
    """
    if row < 0 or col < 0 or row >= 8 or col >= 8:
        return True
    else:
        return False


def find_king(board, white):
    """ Find the row and col of the King of the given color

    :param board: (2d array) shatar board
    :param white: (boolean) True if find white King, otherwise False
    :return: tuple (row, col) of King
    """
    s = 'k'
    if white:
        s = 'K'

    for i in range(len(board)):
        for j in range(len(board)):
            piece = board[i][j]
            if str(piece) is s:
                return i, j


def get_piece_delta(row_diff, col_diff):
    """ Get a tuple of the direction to move for row and column

    :param row_diff:
    :param col_diff:
    :return:
    """
    row = 0
    col = 0

    if row_diff > 0:
        row += 1
    elif row_diff < 0:
        row -= 1

    if col_diff > 0:
        col += 1
    elif col_diff < 0:
        col -= 1

    return row, col


def rook_bishop_move_helper(board, from_row, from_col, to_row, to_col, row_diff, col_diff, white):
    delta = get_piece_delta(row_diff, col_diff)

    for i in range(1, max(abs(row_diff), abs(col_diff))):
        square = board[from_row + delta[0] * i][from_col + delta[1] * i]
        if square is not None:
            return False

    square = board[to_row][to_col]

    if square is None:
        return True

    return white is not square.white


def king_knight_move_helper(board, directions, from_row, from_col, to_row, to_col, white):
    row_diff = to_row - from_row
    col_diff = to_col - from_col

    if (row_diff, col_diff) not in directions:
        return False

    piece = board[to_row][to_col]
    if piece is not None and piece.white == white:
        return False
    else:
        return True


class Piece(object):
    """ Superclass for all Pieces in Shatar

    Attributes:
        white (boolean): whether or not this is a white piece
    """

    def __init__(self, white=True):
        self.white = white

    def is_legal_move(self, board, from_row, from_col, to_row, to_col):
        return self.is_threatening(board, from_row, from_col, to_row, to_col) and \
               not puts_self_in_check(board, from_row, from_col, to_row, to_col, self.white)


class Pawn(Piece):
    """ Represents a pawn in a game of Shatar. """

    def __init__(self, white=True):
        super().__init__(white)

    def __str__(self):
        if self.white:
            return 'P'
        else:
            return 'p'

    def is_threatening(self, board, from_row, from_col, to_row, to_col):
        if is_invalid_indices(to_row, to_col) or is_invalid_indices(from_row, from_col):
            return False

        row_diff = to_row - from_row
        if not self.white:
            row_diff = from_row - to_row

        if row_diff != 1:
            return False

        col_diff = to_col - from_col
        if abs(col_diff) == 1:
            piece = board[to_row][to_col]
            if piece is None or piece.white == self.white:
                return False
            else:
                return True
        elif col_diff == 0:
            piece = board[to_row][to_col]
            if piece is None:
                return True
            else:
                return False
        else:
            return False

    def generate_legal_moves(self, board, from_row, from_col):
        """ Return a list of legal moves to make

        :param board:
        :param from_row:
        :param from_col:
        :return: returns a list of legal moves in format [(from_row, from_col, to_row, to_col), ...]
        """
        if is_invalid_indices(from_row, from_col):
            return []

        moves = []

        row_delta = 1
        if not self.white:
            row_delta = -1

        if self.is_legal_move(board, from_row, from_col, from_row + row_delta, from_col):
            moves.append(from_row, from_col, from_row + row_delta, from_col)

        if self.is_legal_move(board, from_row, from_col, from_row + row_delta, from_col + 1):
            moves.append(from_row, from_col, from_row + row_delta, from_col + 1)

        if self.is_legal_move(board, from_row, from_col, from_row + row_delta, from_col - 1):
            moves.append(from_row, from_col, from_row + row_delta, from_col - 1)

        return moves


class King(Piece):
    """ Represents a King in a game of Shatar. """

    def __init__(self, white=True):
        super().__init__(white)

    def __str__(self):
        if self.white:
            return 'K'
        else:
            return 'k'

    def is_threatening(self, board, from_row, from_col, to_row, to_col):
        if is_invalid_indices(to_row, to_col) or is_invalid_indices(from_row, from_col):
            return False

        return king_knight_move_helper(board, KING_DIRECTIONS, from_row, from_col, to_row, to_col, self.white)

    def generate_legal_moves(self, board, from_row, from_col):
        """ Return a list of legal moves to make

        :return: returns a list of legal moves in format [(from_row, from_col, to_row, to_col), ...]
        """
        if is_invalid_indices(from_row, from_col):
            return []

        moves = []

        for direction in KING_DIRECTIONS:
            if self.is_legal_move(board, from_row, from_col, from_row + direction[0], from_col + direction[1]):
                moves.append(from_row, from_col, from_row + direction[0], from_col + direction[1])

        return moves


class Rook(Piece):
    """ Represents a Rook in a game of Shatar."""

    def __init__(self, white=True):
        super().__init__(white)

    def __str__(self):
        if self.white:
            return 'R'
        else:
            return 'r'

    def is_threatening(self, board, from_row, from_col, to_row, to_col):
        if is_invalid_indices(to_row, to_col) or is_invalid_indices(from_row, from_col):
            return False

        row_diff = to_row - from_row
        col_diff = to_col - from_col

        if not ((row_diff == 0 or col_diff == 0) and (row_diff != col_diff)):
            return False

        return rook_bishop_move_helper(board, from_row, from_col, to_row, to_col, row_diff, col_diff, self.white)

    def generate_legal_moves(self, board, from_row, from_col):
        """ Return a list of legal moves to make

        :return: returns a list of legal moves in format [(from_row, from_col, to_row, to_col), ...]
        """
        if is_invalid_indices(from_row, from_col):
            return []

        # TODO
        moves = []

        return moves


class Bishop(Piece):
    """ Represents a Bishop in a game of Shatar."""

    def __init__(self, white=True):
        super().__init__(white)

    def __str__(self):
        if self.white:
            return 'B'
        else:
            return 'b'

    def is_threatening(self, board, from_row, from_col, to_row, to_col):
        if is_invalid_indices(to_row, to_col) or is_invalid_indices(from_row, from_col):
            return False

        row_diff = to_row - from_row
        col_diff = to_col - from_col

        if not (abs(row_diff) == abs(col_diff)):
            return False

        if row_diff == 0 or col_diff == 0:
            return False

        return rook_bishop_move_helper(board, from_row, from_col, to_row, to_col, row_diff, col_diff, self.white)

    def generate_legal_moves(self, board, from_row, from_col):
        """ Return a list of legal moves to make

        :return: returns a list of legal moves in format [(from_row, from_col, to_row, to_col), ...]
        """
        if is_invalid_indices(from_row, from_col):
            return []

        # TODO
        moves = []

        return moves


class Tiger(Piece):
    """ Represents a Tiger in a game of Shatar."""

    def __init__(self, white=True):
        super().__init__(white)

    def __str__(self):
        if self.white:
            return 'Q'
        else:
            return 'q'

    def is_threatening(self, board, from_row, from_col, to_row, to_col):
        if Rook().is_threatening(board, from_row, from_col, to_row, to_col) or \
                king_knight_move_helper(board, KING_DIRECTIONS, from_row, from_col, to_row, to_col, self.white):
            return True

    def generate_legal_moves(self, board, from_row, from_col):
        """ Return a list of legal moves to make

        :return: returns a list of legal moves in format [(from_row, from_col, to_row, to_col), ...]
        """
        if is_invalid_indices(from_row, from_col):
            return []

        # TODO
        moves = []

        return moves


class Knight(Piece):
    """ Represents a Knight in a game of Shatar."""

    def __init__(self, white=True):
        super().__init__(white)

    def __str__(self):
        if self.white:
            return 'N'
        else:
            return 'n'

    def is_threatening(self, board, from_row, from_col, to_row, to_col):
        if is_invalid_indices(to_row, to_col) or is_invalid_indices(from_row, from_col):
            return False

        return king_knight_move_helper(board, KNIGHT_DIRECTIONS, from_row, from_col, to_row, to_col, self.white)

    def generate_legal_moves(self, board, from_row, from_col):
        """ Return a list of legal moves to make

        :return: returns a list of legal moves in format [(from_row, from_col, to_row, to_col), ...]
        """
        if is_invalid_indices(from_row, from_col):
            return []

        # TODO
        moves = []

        return moves
