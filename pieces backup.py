#
#
#
# KING_DIRECTIONS = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
# ROOK_DIRECTIONS = [(1, 0), (-1, 0), (0, 1), (0, -1)]
#
#
# def is_invalid_indices(row, col):
#     """ Return true if an invalid index is given
#
#     :param row: row
#     :param col: col
#     :return: true if given index is invalid for a shatar board
#     """
#     if row < 0 or col < 0 or row >= 8 or col >= 8:
#         return True
#     else:
#         return False
#
#
# def cant_move_piece(row, col):
#     return False
#
#
# def square_is_threatened(board, to_row, to_col, white):
#     """ Return True if the given square is threatened by the opposite color on the given board.
#
#     :param board: (2d array) the board to check
#     :param to_row: (int) the row of the square
#     :param to_col: (int) the column of the square
#     :param white: (boolean) True if we want to know if the square is threatened by white, False for black
#     :return:
#     """
#
#
# class Piece(object):
#     """ Superclass for all Pieces in Shatar
#
#     Attributes:
#         white (boolean): whether or not this is a white piece
#         row (int): row location on the board of this piece
#         col (int): column location on the board of this piece
#         vision (list): list of tuples (row, col) of squares that this piece is attacking
#     """
#
#     def __init__(self, row, col, white=True):
#         self.row = row
#         self.col = col
#         self.white = white
#         self.vision = []
#         self.update_vision()
#
#     def move(self, row, col):
#         if is_invalid_indices(row, col):
#             raise ValueError("Invalid row and col!")
#
#         self.row = row
#         self.col = col
#         self.update_vision()
#
#
# class Pawn(Piece):
#     """ Represents a pawn in a game of Shatar. """
#
#     def __init__(self, row, col, white=True):
#         super().__init__(row, col, white)
#
#     def update_vision(self):
#         vision = []
#
#         row_mod = 1
#         if not self.white:
#             row_mod = -1
#
#         if not is_invalid_indices(self.row + row_mod, self.col + 1):
#             vision.append((self.row + row_mod, self.col + 1))
#
#         if not is_invalid_indices(self.row + row_mod, self.col - 1):
#             vision.append((self.row + row_mod, self.col - 1))
#
#         self.vision = vision
#
#     def __str__(self):
#         if self.white:
#             return 'P'
#         else:
#             return 'p'
#
#     def is_legal_move(self, board, to_row, to_col):
#         if is_invalid_indices(to_row, to_col) or cant_move_piece(self.row, self.col):
#             return False
#
#         row_diff = to_row - self.row
#         if not self.white:
#             row_diff = self.row - to_row
#
#         if row_diff != 1:
#             return False
#
#         col_diff = to_col - self.col
#         if abs(col_diff) == 1:
#             piece = board[to_row][to_col]
#             if piece is None or piece.white == self.white:
#                 return False
#             else:
#                 return True
#         elif col_diff == 0:
#             piece = board[to_row][to_col]
#             if piece is None:
#                 return True
#             else:
#                 return False
#         else:
#             return False
#
#
# class King(Piece):
#     """ Represents a King in a game of chess.
#
#     Attributes:
#         white (boolean): whether or not this is a white piece
#         row (int): row location on the board of this piece
#         col (int): column location on the board of this piece
#
#     """
#
#     def __init__(self, row, col, white=True):
#         super().__init__(row, col, white)
#
#     def __str__(self):
#         if self.white:
#             return 'K'
#         else:
#             return 'k'
#
#     def update_vision(self):
#         vision = []
#
#         for direction in KING_DIRECTIONS:
#             square = (self.row + direction[0], self.col + direction[1])
#             if not is_invalid_indices(square[0], square[1]):
#                 vision.append(square)
#
#         self.vision = vision
#
#     def is_legal_move(self, board, to_row, to_col):
#         if is_invalid_indices(to_row, to_col):
#             return False
#
#         row_diff = to_row = self.row
#         col_diff = to_col - self.col
#
#         if (row_diff, col_diff) not in KING_DIRECTIONS:
#             return False
#
#         piece = board[to_row][to_col]
#         if piece is None or piece.white == self.white:
#             return False
#         else:
#             return not square_is_threatened(board, to_row, to_col, not self.white)
#
#
# class Rook(Piece):
#     """ Represents a Rook in a game of Shatar."""
#
#     def __init__(self, row, col, white=True):
#         super().__init__(row, col, white)
#
#     def __str__(self):
#         if self.white:
#             return 'R'
#         else:
#             return 'r'
#
#     def update_vision(self, board=None):
#         vision = []
#
#         for direction in ROOK_DIRECTIONS:
#             blocked = False
#             while not blocked:
#                 square = (self.row + direction[0], self.col + direction[1])
#                 if is_invalid_indices(square[0], square[1]):
#                     blocked = True
#
#
#
#         self.vision = vision
#
#     def is_legal_move(self, board, to_row, to_col):
#         if is_invalid_indices(to_row, to_col):
#             return False
#
#         row_diff = to_row = self.row
#         col_diff = to_col - self.col
#
#         if (row_diff, col_diff) not in KING_DIRECTIONS:
#             return False
#
#         piece = board[to_row][to_col]
#         if piece is None or piece.white == self.white:
#             return False
#         else:
#             return not square_is_threatened(board, to_row, to_col, not self.white)
#
