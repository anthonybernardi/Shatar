import math
import random

# import numpy as np

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
    def __init__(self, white):
        self.white = white


class RandomPlayer(ShatarAI):
    def __init__(self, white):
        super().__init__(white)

    def get_move(self, model):
        if model.to_play is not self.white:
            raise ValueError("Trying to play on wrong turn!")

        candidate_moves = model.generate_legal_moves()

        return random.choice(candidate_moves)


class GreedyPlayer(ShatarAI):
    def __init__(self, white):
        super().__init__(white)

    def get_move(self, model):
        if model.to_play is not self.white:
            raise ValueError("Trying to play on wrong turn!")

        candidate_moves = model.generate_legal_moves()

        # if there are a lot of moves with the same eval, we want to choose a random one
        best_moves_to_choose_from = []

        # Set up the first one so that I can max it later
        best_move = candidate_moves[0]
        board = model.get_board()
        test_model = ShatarModel(board=board, to_play=self.white)
        test_model.move(best_move[0], best_move[1], best_move[2], best_move[3])
        best_move_eval = count_material_evaluation(test_model.get_board())
        best_moves_to_choose_from.append(best_move)

        for move in candidate_moves:
            board = model.get_board()
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


class PacifistPlayer(ShatarAI):
    """
    AI that will randomly choose from moves that don't capture a piece.
    Randomly chooses a capturing move if that's the only option.
    """

    def __init__(self, white):
        super().__init__(white)

    def get_move(self, model):
        if model.to_play is not self.white:
            raise ValueError("Trying to play on wrong turn!")

        candidate_moves = model.generate_legal_moves()
        pacifist_moves = []

        for move in candidate_moves:
            if model.get_piece_at(move[2], move[3]) is None:
                pacifist_moves.append(move)

        if len(pacifist_moves) == 0:
            return random.choice(candidate_moves)

        return random.choice(pacifist_moves)


class MCTSPlayer(ShatarAI):
    """
    AI that will play based off of MCTS. It will keep track of win probabilities for every
    board state that it sees in dicts. To save space/time, we're going to hash boards.
    """

    # we will hash seen boards to save space/time
    # as suggested by Prof Gold

    root = None

    def __init__(self, white):
        super().__init__(white)

    def get_move(self, model):
        if model.to_play is not self.white:
            raise ValueError("Trying to play on wrong turn!")

        root = GameTree(model=model)
        selected_node = root.best_child()
        return selected_node


def get_greedy_move(model, candidate_moves):
    """
    this is the same as get_move in GreedyPlayer, this is going to be used
    in the rollout for the MCTS player
    :return:
    """

    # if model.to_play is not self.white:
    #    raise ValueError("Trying to play on wrong turn!")

    # this is not a player class so it doesn't have self.white
    # so I'm replacing it with model.to_play everywhere
    # should be enforced to be the same I think?

    # if there are a lot of moves with the same eval, we want to choose a random one
    best_moves_to_choose_from = []

    # Set up the first one so that I can max it later
    best_move = candidate_moves[0]
    board = model.get_board()
    test_model = ShatarModel(board=board, to_play=model.to_play)
    test_model.move(best_move[0], best_move[1], best_move[2], best_move[3])
    best_move_eval = count_material_evaluation(test_model.get_board())
    best_moves_to_choose_from.append(best_move)

    for move in candidate_moves:
        board = model.get_board()
        test_model = ShatarModel(board=board, to_play=model.to_play)
        test_model.move(move[0], move[1], move[2], move[3])
        curr_eval = count_material_evaluation(test_model.get_board())

        if model.to_play:
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


### ZOBRIST HASHING:
# https://en.wikipedia.org/wiki/Zobrist_hashing
# https://levelup.gitconnected.com/zobrist-hashing-305c6c3c54d0

# https://github.com/niklasf/python-chess/blob/master/chess/polyglot.py
# here's an example I don't really understand that uses some weird libraries? idk

# will use transposition tables (HashMap) as a cache to store already seen board positions

# used pseudocode on Wikipedia to write two functions below

white_pawn = 1
white_rook = 2
white_knight = 3
white_bishop = 4
white_tiger = 5
white_king = 6
black_pawn = 7
black_rook = 8
black_knight = 9
black_bishop = 10
black_tiger = 11
black_king = 12


def init_zobrist():
    # fill a table of random numbers/bitstrings
    table = [64][12]
    for i in range(64):  # loop over the board, represented as a linear array
        for j in range(12):  # loop over the pieces
            table[i][j] = random.getrandbits(64)


def hash(board):
    h = 0
    for i in range(64):  # loop over the board, represented as a linear array
        if board[i] is not None:
            piece_hash = 0
            if board[i].__str__() == 'P':
                piece_hash = white_pawn
            if board[i].__str__() == 'R':
                piece_hash = white_rook
            if board[i].__str__() == 'N':
                piece_hash = white_knight
            if board[i].__str__() == 'B':
                piece_hash = white_bishop
            if board[i].__str__() == 'Q':
                piece_hash = white_tiger
            if board[i].__str__() == 'K':
                piece_hash = white_king
            if board[i].__str__() == 'p':
                piece_hash = black_pawn
            if board[i].__str__() == 'r':
                piece_hash = black_rook
            if board[i].__str__() == 'n':
                piece_hash = black_knight
            if board[i].__str__() == 'b':
                piece_hash = black_bishop
            if board[i].__str__() == 'q':
                piece_hash = black_tiger
            if board[i].__str__() == 'k':
                piece_hash = black_king

            # h = h XOR table[i][j]
            h = h ^ piece_hash

    return h


class GameTree:
    """
    A class representing a tree in Monte Carlo tree search
    """

    def __init__(self, model, this_hash, parent_hash=None, parent_action=None):
        self.parent = None
        self.model = model
        self.hash = this_hash
        self.parent_hash = parent_hash
        self.parent_action = parent_action
        # children: array of GameTrees
        self.children = []
        self.num_wins = 0
        self.num_sims = 0

    # https://ai-boson.github.io/mcts/
    def untried_actions(self):
        return self.model.generate_legal_moves()

    def expansion(self):
        # not sure if pop is the best thing here?
        # actually it probably is because you want to expand until untried_actions is empty
        action = self.untried_actions().pop()
        next_state = self.model.move(action)
        child = GameTree(model=next_state, parent_hash=hash(self), parent_action=action)
        self.children.append(child)
        return child

    def is_terminal_node(self):
        return self.model.is_game_over()

    # rollout
    def simulation(self):
        current_state = self.model

        # while the game is not over
        while current_state.is_game_over() != 2:
            possible_moves = current_state.generate_legal_moves()
            action = self.rollout_policy(current_state, possible_moves)
            current_state = current_state.move(action)

        # 1 for white win, -1 for black win, 0 for draw
        # should probably change what is returned here but leaving it for now
        return current_state.is_game_over()

    def backpropagate(self, result):
        self.num_sims += 1
        if result == 1:
            self.num_wins += 1
        if self.parent:
            self.parent.backpropagate(result)

    def is_fully_expanded(self):
        return len(self.untried_actions()) == 0

    def best_child(self, c=1):
        # ucb = [(i.num_wins() / i.num_sims()) + c * math.sqrt(2 * math.log(self.num_sims))]
        # return self.children[np.argmax(ucb)]

        max_of_ucb = 0
        best_children = []

        for child in self.children:

            ni = child.num_sims
            if ni == 0:
                ni = 0.0001
            xi = child.num_wins / ni

            # the selection equation           # this might be wrong
            ucb = xi + c * math.sqrt(2 * math.log(self.num_sims) / ni)

            if ucb > max_of_ucb:
                best_children = []

            max_of_ucb = max(max_of_ucb, ucb)
            if ucb == max_of_ucb:
                best_children.append(child)

        return random.choice(best_children)

    def rollout_policy(self, model, possible_moves):
        # the example uses random rollout but we are not using that
        # we're going to use an evaluation function like in the greedy AI
        return get_greedy_move(model, possible_moves)

    def tree_policy(self):

        current_node = self
        while not current_node.is_terminal_node():

            if not current_node.is_fully_expanded():
                return current_node.expansion()
            else:
                current_node = current_node.best_child()

        return current_node
