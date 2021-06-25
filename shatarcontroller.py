import pygame
from shatarview import ShatarView, get_square_under_mouse, draw_drag
from shatar import ShatarModel, fen_to_board
from basic_ai import MCTSPlayer, GreedyPlayer, PacifistPlayer, RandomPlayer, count_material_evaluation
from time import sleep
from shatarview import TILESIZE

BOARD_POS = (0, 0)
SLEEP_TIME = .1


def win_statement(num):
    if num == 0:
        print('Draw!')
    if num == -1:
        print('Black wins!')
    if num == 1:
        print('White wins!')


def score_statement(score):
    # print the score / who is winning
    # negative score means black is winning
    if score < 0:
        print('black is up ' + str(abs(score)) + ' points of material!')
    # positive score means white is winning
    elif score > 0:
        print('white is up ' + str(score) + ' points of material!')
    else:
        print('the material count is even!')


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

        view.draw(screen, board, self.model.last_moved_from, self.model.last_moved_to, selected_piece)

        while self.model.is_game_over() == 2:
            if self.model.to_play and not white_playable:
                clock.tick()
                move = white_player.get_move(self.model)
                clock.tick()
                sleep(SLEEP_TIME)
                self.model.move(move[0], move[1], move[2], move[3])
                board = self.model.get_board()
                print('white move took ' + str(clock.get_rawtime() / 1000) + ' seconds')
                score = count_material_evaluation(self.model.get_board())
                score_statement(score)
            elif not self.model.to_play and not black_playable:
                clock.tick()
                move = black_player.get_move(self.model)
                clock.tick()
                sleep(SLEEP_TIME)
                self.model.move(move[0], move[1], move[2], move[3])
                board = self.model.get_board()
                print('black move took ' + str(clock.get_rawtime() / 1000) + ' seconds')
                score = count_material_evaluation(self.model.get_board())
                score_statement(score)

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
            view.draw(screen, board, self.model.last_moved_from, self.model.last_moved_to, selected_piece)
            # draw the dragging piece and update its position
            if selected_piece:
                drop_pos = draw_drag(screen, board, selected_piece)

            pygame.display.flip()
            clock.tick(60)

        # print(self.model.is_game_over())
        win_statement(self.model.is_game_over)

        while True:
            events = pygame.event.get()
            for e in events:
                if e.type == pygame.QUIT:
                    return
            # draw the board
            view.draw(screen, board, self.model.last_moved_from, self.model.last_moved_to, selected_piece)

            pygame.display.flip()
            clock.tick(10)

    def simulate_game(self, white_player, black_player):
        sim_model = ShatarModel(board=self.model.get_board(), to_play=self.model.to_play)
        prev_score = 0

        while sim_model.is_game_over() == 2:
            if sim_model.to_play:
                move = white_player.get_move(sim_model)
            else:
                move = black_player.get_move(sim_model)

            if move is None:
                # sim_model.to_play = not sim_model.to_play
                continue

            sim_model.move(move[0], move[1], move[2], move[3])
            score = count_material_evaluation(sim_model.get_board())

            # only print when the score changes
            if score != prev_score:
                score_statement(score)
                prev_score = score

        # print(f'Game had: {sim_model.total_moves} total moves')

        win_statement(sim_model.is_game_over())

        return sim_model.is_game_over()


def simulate_n_games(white_player, black_player, n):
    white_win = 0
    black_win = 0
    draw = 0

    for i in range(n):
        model = ShatarModel()
        controller = ShatarController(model)
        w = controller.simulate_game(white_player, black_player)
        if w == 1:
            white_win += 1
        elif w == 0:
            draw += 1
        elif w == -1:
            black_win += 1

        print(f'game {i} finished')

    print(f'White won: {white_win} games')
    print(f'Black won: {black_win} games')
    print(f'There were: {draw} drawn games')


def main():
    fen = "k6p/7P/8/8/8/8/8/K7"
    model = ShatarModel()

    #white_player = None
    white_player = RandomPlayer(white=True)
    # white_player = GreedyPlayer(white=True)
    # white_player = PacifistPlayer(white=True)
    black_player = MCTSPlayer(white=False, random_rollout=False)
    black_player.set_simulation_number(100)

    controller = ShatarController(model)
    #controller.play_game(white_player, black_player)
    simulate_n_games(white_player, black_player, 10)


if __name__ == '__main__':
    main()
