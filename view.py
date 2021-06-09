import pygame
from shatar import ShatarModel, fen_to_board
from pieces import King, Pawn, Tiger

TILESIZE = 64
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


def draw_pieces(screen, board, font, selected_piece):
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
                pos = pygame.Rect(BOARD_POS[0] + x * TILESIZE + 1, BOARD_POS[1] + y * TILESIZE + 1, TILESIZE, TILESIZE)
                screen.blit(s1, s1.get_rect(center=pos.center))


def draw_selector(screen, piece, x, y):
    if piece is not None:
        rect = (BOARD_POS[0] + x * TILESIZE, BOARD_POS[1] + y * TILESIZE, TILESIZE, TILESIZE)
        pygame.draw.rect(screen, (255, 0, 0, 50), rect, 2)


def draw_drag(screen, board, selected_piece, font):
    if selected_piece:
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


TOUGH_BOARD = [[King(), None, None, None, None, None, None, None],
               [Tiger(), None, None, None, None, None, None, None],
               [None, None, None, None, None, None, None, None],
               [None, None, None, None, None, None, Pawn(white=False), None],
               [None, None, None, None, None, None, None, None],
               [None, Pawn(), None, None, None, None, None, None],
               [Pawn(white=False), None, None, None, None, None, None, None],
               [King(white=False), None, None, None, None, None, None, None]]


def main():
    model = ShatarModel(fen_to_board("7k/6pp/4Qn1P/8/3B4/8/8/K7"), last_moved_from=None, last_moved_to=None)
    pygame.init()
    pygame.display.set_caption('Shatar')
    font = pygame.font.SysFont('', 32)
    screen = pygame.display.set_mode((TILESIZE * 8 + 5, TILESIZE * 8 + 5))
    board = model.get_board()
    board_surf = create_board_surf(model.last_moved_from, model.last_moved_to)
    clock = pygame.time.Clock()
    selected_piece = None
    drop_pos = None
    while model.is_game_over() == 2:
        piece, x, y = get_square_under_mouse(board)
        events = pygame.event.get()
        for e in events:
            if e.type == pygame.QUIT:
                return
            if e.type == pygame.MOUSEBUTTONDOWN:
                if piece != None:
                    selected_piece = piece, x, y
            if e.type == pygame.MOUSEBUTTONUP:
                if drop_pos:
                    piece, old_x, old_y = selected_piece
                    new_x, new_y = drop_pos
                    try:
                        model.move(7 - old_y, old_x, 7 - new_y, new_x)
                        board = model.get_board()
                    except ValueError as e:
                        print(e)
                        pass

                selected_piece = None
                drop_pos = None

        board_surf = create_board_surf(model.last_moved_from, model.last_moved_to)
        screen.fill(pygame.Color('grey'))
        screen.blit(board_surf, BOARD_POS)
        draw_pieces(screen, board, font, selected_piece)
        drop_pos = draw_drag(screen, board, selected_piece, font)

        pygame.display.flip()
        clock.tick(60)

    print(model.is_game_over())


if __name__ == '__main__':
    main()
