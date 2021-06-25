import math
import random

# import numpy as np

from shatar import ShatarModel

MATERIAL_VALUE = {'k': 0, 'K': 0, 'p': -1, 'P': 1, 'q': -7, 'Q': 7, 'r': -5, 'R': 5, 'b': -3, 'B': 3, 'n': -3, 'N': 3}
MOVES_PER_SIMULATION = 50
WINNING_POSITION_VALUE = 3
C_CONSTANT = 1.414
total_arm_pulls = 0


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


# we will hash seen boards to save space/time
# as suggested by Prof Gold

hash_to_legal_moves = dict()
hash_to_is_game_over = dict()
hash_to_best_moves = dict()
hash_to_eval = dict()


# these three dicts do not contain any information about simulation running,
# they only store things we can get from model functions / evaluation from get_greedy_move,
# so they can be global. Even if we have two MCTSPlayer's competing against each other,
# neither will gain an advantage from these dicts, but both will move faster


class MCTSPlayer(ShatarAI):
    """
    AI that will play based off of MCTS. It will keep track of win probabilities for every
    board state that it sees in dicts. To save space/time, we're going to hash boards.
    """

    def __init__(self, white, random_rollout):
        super().__init__(white)
        self.root = None
        self.simulation_number = 100
        self.random_rollout = random_rollout

    def get_move(self, model):
        if model.to_play is not self.white:
            raise ValueError("Trying to play on wrong turn!")

        if self.root is None:
            self.root = GameTree(model=model_copier(model), white=self.white, random_rollout=self.random_rollout)

        if model.to_play is not self.root.model.to_play:
            self.root = self.root.update_opponents_turn(model)

        selected_node = self.root.best_action(self.simulation_number)
        self.root = selected_node

        return selected_node.parent_action

    def set_simulation_number(self, simulation_number):
        self.simulation_number = simulation_number


def get_greedy_move(model, candidate_moves):
    """
    this is the same as get_move in GreedyPlayer, this is going to be used
    in the rollout for the MCTS player
    :return:
    """
    best_moves_to_choose_from = []

    # print('in ggm')
    # print(candidate_moves)

    # board = model.get_board()
    board_hash = hash(model)

    # if board_hash in hash_to_best_moves:
    #   best_moves_to_choose_from = hash_to_best_moves[board_hash]
    # else:

    # if we have not evaluated this board before

    # Set up the first one so that I can max it later
    best_move = candidate_moves[0]

    test_model = model_copier(model)
    test_model.move(best_move[0], best_move[1], best_move[2], best_move[3])

    test_board = test_model.get_board()
    # test_board_hash = hash(test_board, test_model.to_play)

    best_move_eval = count_material_evaluation(test_board)
    best_moves_to_choose_from.append(best_move)

    for move in candidate_moves:
        test_model = model_copier(model)
        test_model.move(move[0], move[1], move[2], move[3])

        test_board_hash = hash(test_model)

        if test_board_hash not in hash_to_eval:
            hash_to_eval[test_board_hash] = count_material_evaluation(test_model.get_board())

        curr_eval = hash_to_eval[test_board_hash]

        if test_board_hash not in hash_to_is_game_over:
            hash_to_is_game_over[test_board_hash] = test_model.is_game_over()
        gg = hash_to_is_game_over[test_board_hash]

        # curr_eval = count_material_evaluation(test_model.board)
        # gg = test_model.is_game_over()

        if model.to_play:

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

    hash_to_best_moves[board_hash] = best_moves_to_choose_from
    return random.choice(best_moves_to_choose_from)


### ZOBRIST HASHING:
# https://en.wikipedia.org/wiki/Zobrist_hashing
# https://levelup.gitconnected.com/zobrist-hashing-305c6c3c54d0

# https://github.com/niklasf/python-chess/blob/master/chess/polyglot.py
# here's an example I don't really understand that uses some weird libraries? idk

# will use transposition tables (HashMap) as a cache to store already seen board positions
# these tables are dicts: hash_to_legal_moves, hash_to_best_moves, hash_to_is_game_over

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


# table = [8][8][12]
# table = [[[None for k in range(12)] for j in range(8)] for i in range(8)]


# def init_zobrist():
#     # fill a table of random numbers/bitstrings
#     #print(table)
#     for i in range(8):  # loop over the board
#         for j in range(8):
#             for k in range(12):  # loop over the pieces
#
#                 table[i][j][k] = random.getrandbits(64)
#     #print(table[0][0][0])
#
#
# def hash(board, to_play):
#     h = 0
#
#     # if the table hasn't been initialized yet
#     #if table[1][1][0] is None:
#         #init_zobrist()
#
#     for i in range(8):  # loop over the board
#         for j in range(8):
#             if board[i][j] is not None:
#                 piece_hash = 0
#                 if board[i][j].__str__() == 'P':
#                     # piece_hash = white_pawn
#                     piece_hash = table[i][j][0]
#                 if board[i][j].__str__() == 'R':
#                     # piece_hash = white_rook
#                     piece_hash = table[i][j][1]
#                 if board[i][j].__str__() == 'N':
#                     # piece_hash = white_knight
#                     piece_hash = table[i][j][2]
#                 if board[i][j].__str__() == 'B':
#                     # piece_hash = white_bishop
#                     piece_hash = table[i][j][3]
#                 if board[i][j].__str__() == 'Q':
#                     # piece_hash = white_tiger
#                     piece_hash = table[i][j][4]
#                 if board[i][j].__str__() == 'K':
#                     # piece_hash = white_king
#                     piece_hash = table[i][j][5]
#                 if board[i][j].__str__() == 'p':
#                     # piece_hash = black_pawn
#                     piece_hash = table[i][j][6]
#                 if board[i][j].__str__() == 'r':
#                     # piece_hash = black_rook
#                     piece_hash = table[i][j][7]
#                 if board[i][j].__str__() == 'n':
#                     # piece_hash = black_knight
#                     piece_hash = table[i][j][8]
#                 if board[i][j].__str__() == 'b':
#                     # piece_hash = black_bishop
#                     piece_hash = table[i][j][9]
#                 if board[i][j].__str__() == 'q':
#                     # piece_hash = black_tiger
#                     piece_hash = table[i][j][10]
#                 if board[i][j].__str__() == 'k':
#                     # piece_hash = black_king
#                     piece_hash = table[i][j][11]
#
#                 # h = h XOR table[i][j]
#                 h = h ^ piece_hash
#
#     # we can't just hash the board state to legal moves because the same board state could occur
#     # but it could be white's turn one time it's seen and black's turn another time
#
#     if to_play:
#         string_hash = '0' + str(h)
#     else:
#         string_hash = '1' + str(h)
#
#     #print(string_hash)
#
#     return string_hash  # h


class GameTree:
    """
    A class representing a tree in Monte Carlo tree search
    """

    def __init__(self, model, parent=None, parent_action=None, white=True, random_rollout=True):
        self.white = white
        self.parent = parent
        self.model = model
        self.parent_action = parent_action
        self.board_hash = hash(self.model)  # hash(self.model.board, self.model.to_play)
        self.untried_actions = self.get_untried_actions()
        # children: array of GameTrees
        self.children = []
        self.num_wins = 0
        self.num_sims = 0
        self.random_rollout = random_rollout

    # https://ai-boson.github.io/mcts/
    def get_untried_actions(self):
        if self.board_hash not in hash_to_legal_moves:
            hash_to_legal_moves[self.board_hash] = self.model.generate_legal_moves()

        return hash_to_legal_moves[self.board_hash]
        # return self.model.generate_legal_moves()

    def expansion(self):
        """ Returns a random untried child node

        :return:
        """

        action = random.choice(self.untried_actions)
        self.untried_actions.remove(action)

        next_model = self.model_copier()
        next_model.move(action[0], action[1], action[2], action[3])
        child = GameTree(model=next_model, parent=self, parent_action=action, white=self.white)
        self.children.append(child)
        return child

    def is_terminal_node(self):
        if self.board_hash not in hash_to_is_game_over:
            hash_to_is_game_over[self.board_hash] = self.model.is_game_over()

        return hash_to_is_game_over[self.board_hash]

    def backpropagate(self, result):
        self.num_sims += 1

        if result == 1 and self.white:
            self.num_wins += 1
        elif result == -1 and not self.white:
            self.num_wins += 1
        elif result == 0:
            self.num_wins += 0.5
        else:
            self.num_wins -= 1

        if self.parent:
            self.parent.backpropagate(result)

    def is_fully_expanded(self):
        return len(self.untried_actions) == 0

    def best_child(self):
        max_win_percentage = float('-inf')
        best_children = []

        for child in self.children:
            win_percentage = child.num_wins / child.num_sims

            print(str(child.parent_action) + ': ' + str(win_percentage))
            if win_percentage > max_win_percentage:
                best_children = []
                max_win_percentage = win_percentage
                best_children.append(child)
            elif max_win_percentage == win_percentage:
                best_children.append(child)

        return random.choice(best_children)

    # rollout
    def simulation(self):
        current_state = self.model_copier()
        starting_move = current_state.total_moves

        # while the game is not over
        while current_state.is_game_over() == 2 and \
                not (current_state.total_moves - starting_move > MOVES_PER_SIMULATION):
            board_hash = hash(current_state)
            if board_hash not in hash_to_legal_moves:
                hash_to_legal_moves[board_hash] = current_state.generate_legal_moves()

            possible_moves = hash_to_legal_moves[board_hash]

            if len(possible_moves) == 0:
                # print("*"*20)
                # print("THIS SHOULD NOT HAPPEN WEE WOO WEE WOO")
                gen = current_state.generate_legal_moves()
                possible_moves = gen
                # print('ACTUAL LEGAL MOVES: ' + str(gen))
                # print("*" * 20)

            # possible_moves = current_state.generate_legal_moves()
            action = self.rollout_policy(current_state, possible_moves)
            # print('v.to_play=' + str(current_state.to_play))
            current_state.move(action[0], action[1], action[2], action[3])

        if current_state.is_game_over() == 2:
            evaluation = count_material_evaluation(current_state.board)
            if evaluation >= WINNING_POSITION_VALUE:
                result = 1
            elif evaluation <= -WINNING_POSITION_VALUE:
                result = -1
            else:
                result = 0
        else:
            result = current_state.is_game_over()

        # 1 for white win, -1 for black win, 0 for draw
        # should probably change what is returned here but leaving it for now
        return result

    def rollout_policy(self, model, possible_moves):
        # the example uses random rollout but we are not using that
        # we're going to use an evaluation function like in the greedy AI

        if self.random_rollout:
            return random.choice(possible_moves)
        else:
            return get_greedy_move(model, possible_moves)


    def tree_policy(self, c=C_CONSTANT):

        # SELECTION:
        if len(self.untried_actions) == 0:
            # if no untried children, calculate best ucb1

            max_of_ucb = float('-inf')
            best_children = []

            for child in self.children:

                ni = child.num_sims
                # if ni == 0:
                #     ni = 0.0001
                xi = child.num_wins / ni

                global total_arm_pulls
                # the selection equation
                ucb = xi + c * math.sqrt(2 * math.log(total_arm_pulls) / ni)

                if ucb > max_of_ucb:
                    best_children = []
                    max_of_ucb = ucb
                    best_children.append(child)
                elif ucb == max_of_ucb:
                    best_children.append(child)

            current_node = random.choice(best_children)

        else:
            # we have untried children so greedily choose one
            move = get_greedy_move(model_copier(self.model), self.untried_actions)
            # print(self.untried_actions)
            # print(move)
            # print(move in self.untried_actions)
            self.untried_actions.remove(move)
            # print(len(self.untried_actions))
            new_model = self.model_copier()
            new_model.move(move[0], move[1], move[2], move[3])
            current_node = GameTree(new_model, parent=self, parent_action=move, white=self.white)
            self.children.append(current_node)

        # EXPANSION OF SELECTED NODE
        while not current_node.is_terminal_node():

            if not current_node.is_fully_expanded():
                return current_node.expansion()
            else:
                current_node = current_node.best_child()

        return current_node

    def best_action(self, simulation_no):

        for i in range(simulation_no):
            # gets the next
            # child which is selection and also expansion
            v = self.tree_policy()

            # print(i)
            if i % 100 == 0:
                print(i)

            # simulate on the child and backpropagate
            reward = v.simulation()
            v.backpropagate(reward)

            # reward = v.alpha_simulation()
            # v.alpha_backpropagate(reward)

            global total_arm_pulls
            total_arm_pulls += 1

        return self.best_child()

    def alpha_simulation(self):
        evaluation = count_material_evaluation(self.model.board)
        return evaluation

    def alpha_backpropagate(self, result):
        self.num_sims += 1

        if result >= WINNING_POSITION_VALUE and self.white:
            self.num_wins += 1
        elif result <= -WINNING_POSITION_VALUE and not self.white:
            self.num_wins += 1
        else:
            self.num_wins += 0.5

        # self.num_wins += result

        if self.parent:
            self.parent.backpropagate(result)

    def model_copier(self):
        return model_copier(self.model)

    def update_opponents_turn(self, model):
        for child in self.children:
            if hash(child.model) == hash(model):
                return child
        return GameTree(model_copier(model), white=self.white)


def model_copier(model):
    new_model = ShatarModel(model.get_board(), to_play=model.to_play)
    new_model.shak_sequence_white = model.shak_sequence_black
    new_model.shak_sequence_black = model.shak_sequence_black
    new_model.moves_since_last_capture = model.moves_since_last_capture
    new_model.total_moves = model.total_moves
    return new_model
