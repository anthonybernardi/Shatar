import pygame
from shatar import ShatarModel, fen_to_board
from pieces import King, Pawn, Tiger

TILESIZE = 72
BOARD_POS = (0, 0)

DARK_TILE = pygame.Color(152, 165, 217)
LIGHT_TILE = pygame.Color(245, 245, 245)
LAST_MOVED_FROM = pygame.Color(194, 228, 255)
LAST_MOVED_TO = pygame.Color(116, 177, 227)


def get_piece(piece):
    if piece == 'n':
        s1 = pygame.image.load('piece pictures/black knight.png')
    elif piece == 'N':
        s1 = pygame.image.load('piece pictures/white knight.png')
    elif piece == 'q':
        s1 = pygame.image.load('piece pictures/black queen.png')
    elif piece == 'Q':
        s1 = pygame.image.load('piece pictures/white queen.png')
    elif piece == 'k':
        s1 = pygame.image.load('piece pictures/black king.png')
    elif piece == 'K':
        s1 = pygame.image.load('piece pictures/white king.png')
    elif piece == 'b':
        s1 = pygame.image.load('piece pictures/black bishop.png')
    elif piece == 'B':
        s1 = pygame.image.load('piece pictures/white bishop.png')
    elif piece == 'p':
        s1 = pygame.image.load('piece pictures/black pawn.png')
    elif piece == 'P':
        s1 = pygame.image.load('piece pictures/white pawn.png')
    elif piece == 'r':
        s1 = pygame.image.load('piece pictures/black rook.png')
    elif piece == 'R':
        s1 = pygame.image.load('piece pictures/white rook.png')

    return s1


def create_board_surf(last_moved_from, last_moved_to):
    board_surf = pygame.Surface((TILESIZE * 8, TILESIZE * 8))
    dark = False
    skip = False
    if last_moved_from is None or last_moved_to is None:
        skip = True

    for y in range(8):
        for x in range(8):
            rect = pygame.Rect(x * TILESIZE, y * TILESIZE, TILESIZE, TILESIZE)
            c = DARK_TILE
            if not dark:
                c = LIGHT_TILE

            if not skip:
                if last_moved_from == (7 - y, x):
                    c = LAST_MOVED_FROM
                elif last_moved_to == (7 - y, x):
                    c = LAST_MOVED_TO

            pygame.draw.rect(board_surf, c, rect)
            dark = not dark
        dark = not dark
    return board_surf


def get_square_under_mouse(board):
    mouse_pos = pygame.Vector2(pygame.mouse.get_pos()) - BOARD_POS
    x, y = [int(v // TILESIZE) for v in mouse_pos]
    try:
        if x >= 0 and y >= 0:
            return board[7 - y][x], x, y
    except IndexError:
        pass
    return None, None, None


def draw_pieces(screen, board, selected_piece):
    sx, sy = None, None
    if selected_piece:
        piece, sx, sy = selected_piece

    for y in range(8):
        for x in range(8):
            piece = board[7 - y][x]
            if piece:
                selected = x == sx and y == sy

                if selected:
                    continue

                type = str(piece)

                s1 = get_piece(type)
                s1 = pygame.transform.smoothscale(s1, (TILESIZE, TILESIZE))
                pos = pygame.Rect(BOARD_POS[0] + x * TILESIZE + 1, BOARD_POS[1] + y * TILESIZE + 1, TILESIZE,
                                  TILESIZE)
                screen.blit(s1, s1.get_rect(center=pos.center))


def draw_drag(screen, board, selected_piece):
    piece, x, y = get_square_under_mouse(board)
    if x is not None:
        rect = (BOARD_POS[0] + x * TILESIZE, BOARD_POS[1] + y * TILESIZE, TILESIZE, TILESIZE)
        pygame.draw.rect(screen, (90, 90, 90, 50), rect, 2)

    sel_piece = selected_piece[0]
    color = 'black'
    if sel_piece.white:
        color = 'white'

    type = str(sel_piece)

    pos = pygame.Vector2(pygame.mouse.get_pos())

    s1 = get_piece(type)
    s1 = pygame.transform.smoothscale(s1, (TILESIZE, TILESIZE))
    screen.blit(s1, s1.get_rect(center=pos))
    return x, y


class ShatarView(object):
    def __init__(self, white_playable, black_playable, font):
        self.white_playable = white_playable
        self.black_playable = black_playable
        self.font = font

    def draw(self, screen, board, last_moved_from, last_moved_to, selected_piece):
        board_surf = create_board_surf(last_moved_from, last_moved_to)
        screen.fill(pygame.Color('grey'))
        screen.blit(board_surf, BOARD_POS)
        draw_pieces(screen, board, selected_piece)
