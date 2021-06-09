import random
from shatar import ShatarModel

MATERIAL_VALUE = {'k': 0, 'K': 0, 'p': -1, 'P': 1, 'q': -7, 'Q': 7, 'r': -5, 'R': 5, 'b': -3, 'B': 3, 'n': -3, 'N': 3}


def count_material_evaluation(board):
    material = 0
    for i in range(len(board)):
        for j in range(len(board)):
            piece = board[i][j]
            if piece is not None:
                material += MATERIAL_VALUE[str(piece)]
    return material


class ShatarAI(object):
    def __init__(self, model, white):
        self.model = model
        self.white = white


class RandomPlayer(ShatarAI):
    def __init__(self, model, white):
        super().__init__(model, white)

    def get_move(self):
        if self.model.to_play is not self.white:
            raise ValueError("Trying to play on wrong turn!")

        candidate_moves = self.model.generate_legal_moves()

        return random.choice(candidate_moves)


class GreedyPlayer(ShatarAI):
    def __init__(self, model, white):
        super().__init__(model, white)

    def get_move(self):
        if self.model.to_play is not self.white:
            raise ValueError("Trying to play on wrong turn!")

        candidate_moves = self.model.generate_legal_moves()

        # if there are a lot of moves with the same eval, we want to choose a random one
        best_moves_to_choose_from = []

        # Set up the first one so that I can max it later
        best_move = candidate_moves[0]
        board = self.model.get_board()
        test_model = ShatarModel(board=board, to_play=self.white)
        test_model.move(best_move[0], best_move[1], best_move[2], best_move[3])
        best_move_eval = count_material_evaluation(test_model.get_board())
        best_moves_to_choose_from.append(best_move)

        for move in candidate_moves:
            board = self.model.get_board()
            test_model = ShatarModel(board=board, to_play=self.white)
            test_model.move(move[0], move[1], move[2], move[3])
            curr_eval = count_material_evaluation(test_model.get_board())

            if self.white:
                gg = test_model.is_game_over()
                if gg == 1:
                    return move
                if gg == -1 or 0:
                    continue

                if curr_eval == best_move_eval:
                    best_moves_to_choose_from.append(move)
                elif curr_eval > best_move_eval:
                    best_move = move
                    best_move_eval = curr_eval
                    best_moves_to_choose_from = [move]
            else:
                gg = test_model.is_game_over()
                if gg == -1:
                    return move
                if gg == 1 or 0:
                    continue

                if curr_eval == best_move_eval:
                    best_moves_to_choose_from.append(move)
                elif curr_eval < best_move_eval:
                    best_move = move
                    best_move_eval = curr_eval
                    best_moves_to_choose_from = [move]

        return random.choice(best_moves_to_choose_from)
