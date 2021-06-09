import pygame
from shatarview import ShatarView, get_square_under_mouse, draw_drag
from shatar import ShatarModel, fen_to_board
from basic_ai import RandomPlayer, GreedyPlayer
from time import sleep

TILESIZE = 64
BOARD_POS = (0, 0)


class ShatarController(object):

    def __init__(self, model):
        self.model = model

    def play_game(self, white_player, black_player):
        white_playable = white_player is None
        black_playable = black_player is None

        # initial pygame setup stuff
        pygame.init()
        font = pygame.font.SysFont('', 32)
        view = ShatarView(white_playable, black_playable, font)
        pygame.display.set_caption('Shatar')
        screen = pygame.display.set_mode((TILESIZE * 8 + 5, TILESIZE * 8 + 5))
        clock = pygame.time.Clock()
        board = self.model.get_board()
        selected_piece = None
        drop_pos = None

        while self.model.is_game_over() == 2:
            view.draw(screen, board, self.model.last_moved_from, self.model.last_moved_to, selected_piece)

            if self.model.to_play and not white_playable:
                move = white_player.get_move()
                sleep(1)
                self.model.move(move[0], move[1], move[2], move[3])
                board = self.model.get_board()
            elif not self.model.to_play and not black_playable:
                move = black_player.get_move()
                sleep(1)
                self.model.move(move[0], move[1], move[2], move[3])
                board = self.model.get_board()

            piece, x, y = get_square_under_mouse(self.model.get_board())
            events = pygame.event.get()
            for e in events:
                if e.type == pygame.QUIT:
                    return
                # if click on piece: select it and stuff
                if e.type == pygame.MOUSEBUTTONDOWN:
                    if piece is not None:
                        selected_piece = piece, x, y
                # if let go of click: try to place a piece
                if e.type == pygame.MOUSEBUTTONUP:
                    if drop_pos:
                        piece, old_x, old_y = selected_piece
                        new_x, new_y = drop_pos
                        try:
                            if (self.model.to_play and white_playable) or ((not self.model.to_play) and black_playable):
                                self.model.move(7 - old_y, old_x, 7 - new_y, new_x)
                                board = self.model.get_board()
                        except ValueError as e:
                            print(e)
                            pass

                    selected_piece = None
                    drop_pos = None

            # draw the board
            # view.draw(screen, board, self.model.last_moved_from, self.model.last_moved_to, selected_piece)
            # draw the dragging piece and update its position
            if selected_piece:
                drop_pos = draw_drag(screen, board, selected_piece)

            pygame.display.flip()
            clock.tick(60)

        print(self.model.is_game_over())


def main():
    model = ShatarModel()
    controller = ShatarController(model)
    controller.play_game(RandomPlayer(model, True), GreedyPlayer(model, False))


if __name__ == '__main__':
    main()
