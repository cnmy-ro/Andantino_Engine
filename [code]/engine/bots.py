'''
-BOTS-

This script defines all the components of the Andantino AI:

    1. AndantinoBot class:
        Used to define the game-playing bot

    2. Heuristic Evaluation Functions:
        3.1 Two different evaluation functions
        3,2 Evaluation-function selector

    3. Implementation of search algorithms:
        3.1. Minimax
        3.2. Minimax with Alpha-Beta
        3.3. Negamax
        3.4. Negamax with Alpha-Beta
        3.5. Negamax with Alpha-Beta and Transposition Table

Note: Player IDs are fixed - BOT's player ID = 2 and USER's player ID = 1.
      However, the user can choose color at the start of the game.
'''

__author__ = "Chinmay Rao (i6218054)"

import random, time
import numpy as np
import engine.engine as engine

################################################################################
'''                       1-AndantinoBot class                               '''
################################################################################

class AndantinoBot():
    def __init__(self, bot='random', depth=2, ID_max_depth=None, ID_max_time=None, eval_fn='Fn1', bot_id=2):
        self.bot_id = bot_id # BOT is by default the Player-2
        self.board_state = engine.getInitialBoardState()
        self.prev_board_state = None
        self.player_colors = engine.getPlayerColors() # player_colors[0] => user_color
        self.bot = bot
        self.depth = depth
        self.eval_fn = eval_fn
        self.ID_max_depth = ID_max_depth
        self.ID_max_time = ID_max_time
        self.game_count = engine.getGameCount()

    def undoMove(self):
        # Use case: user enters a move (by mistake), computer plays next. User wants to correct his previous move
        self.board_state = self.prev_board_state
        self.game_count -= 2

    def reloadGame(self, board_state, player_colors, game_count):
        self.board_state = board_state
        self.player_colors = player_colors
        self.game_count = game_count

    def generateFirstMove(self):
        bot_first_move = random.choice([(9,9),(9,10),(9,11),(10,11),(11,10),(10,9)])
        return bot_first_move

    def generateMove(self, board_state):
        ''' Bot algorithm selector '''
        available_moves = engine.getAvailableMoves(board_state)
        print("[bots]Available_moves: ", available_moves)
        # source_bot_id is for the Evaluation function to evaluate the board state for the bot that's generating the move (different bots in BvB mode)
        if self.bot == 'random':
            ''' Choice 1 - Random player '''
            bot_move = RandomPlayer(board_state)

        elif self.bot == 'minimax':
            ''' Choice 2 - Minimax '''
            score, bot_move = MinimaxPlayer(board_state, self.depth, player_minmax='MAX', plyr_id=self.bot_id, eval_fn=self.eval_fn, source_bot_id=self.bot_id, root=True)

        elif self.bot == 'ab-minimax':
            ''' Choice 3 - Minimax with Alpha-Beta prunings '''
            alpha, beta = -10000, 10000
            score, bot_move, _ = ABMinimaxPlayer(board_state, None, self.depth, alpha, beta, player_minmax='MAX', plyr_id=self.bot_id, eval_fn=self.eval_fn, source_bot_id=self.bot_id, root=True, ordered_children=None)

        elif self.bot == 'negamax':
            ''' Choice 4 - Negamax '''
            score, bot_move = NegamaxPlayer(board_state, self.depth, plyr_id=self.bot_id, eval_fn=self.eval_fn, source_bot_id=self.bot_id)

        elif self.bot == 'ab-negamax':
            ''' Choice 5 - Negamax with Alpha-Beta prunings '''
            alpha, beta = -10000, 10000
            score, bot_move = ABNegamaxPlayer(board_state, self.depth, alpha, beta, plyr_id=self.bot_id, eval_fn=self.eval_fn, source_bot_id=self.bot_id, root=True)

        elif self.bot == 'ab-negamax-TT':
            ''' Choice 6 - Alpha-Beta with TT '''
            alpha, beta = -10000, 10000
            score, bot_move, _ = ABNegamaxTTPlayer(board_state, None, self.depth, alpha, beta, plyr_id=self.bot_id, eval_fn=self.eval_fn, source_bot_id=self.bot_id, root=True, ordered_children=None)

        elif self.bot == 'ab-minimax-ID':
            ''' Choice 7 - Alpha-Beta with Iterative Deepening and move ordering '''
            alpha, beta = -10000, 10000
            eval_info = None
            ordered_children = []
            def sortOnEvals(ei):
                return ei[1]

            T1 = time.time()
            for i_depth in range(1, self.ID_max_depth+1): # Iterative Deepening
                print("ID iter: ", i_depth)
                if i_depth == 1:
                    ordered_children = None
                score, bot_move, eval_info = ABMinimaxPlayer(board_state, None, i_depth, alpha, beta, player_minmax='MAX', plyr_id=self.bot_id, eval_fn=self.eval_fn, source_bot_id=self.bot_id, root=True, ordered_children=ordered_children)
                T2 = time.time()
                if T2-T1 >= self.ID_max_time:
                    break

                ordered_children = []                         # Move ordering
                eval_info.sort(key=sortOnEvals, reverse=True) #
                for ord_ch in eval_info:                      #
                    ordered_children.append(ord_ch[0])        #

        elif self.bot == 'ab-negamax-TT-ID':
            ''' Choice 8 - Alpha-Beta negamax TT with Iterative Deepening and move ordering '''
            alpha, beta = -10000, 10000
            eval_info = None
            ordered_children = []
            def sortOnEvals(ei):
                return ei[1]

            T1 = time.time()
            for i_depth in range(1, self.ID_max_depth+1): # Iterative Deepening
                print("ID iter: ", i_depth)
                if i_depth == 1:
                    ordered_children = None
                score, bot_move, eval_info = ABNegamaxTTPlayer(board_state, None, i_depth, alpha, beta, plyr_id=self.bot_id, eval_fn=self.eval_fn, source_bot_id=self.bot_id, root=True, ordered_children=ordered_children)
                T2 = time.time()
                if T2-T1 >= self.ID_max_time:
                    break

                ordered_children = []                         # Move ordering
                eval_info.sort(key=sortOnEvals, reverse=True) #
                for ord_ch in eval_info:                      #
                    ordered_children.append(ord_ch[0])        #

        print("[bots]Computer's's move: ", bot_move,'\n')
        return bot_move


################################################################################
'''                      2-Heuristic Evaluation functions                    '''
################################################################################

def _evalFn1(board_state, player_to_move, source_bot_id=2):
    ''' Checking if a player can win in one move '''

    en_id = 1
    if source_bot_id == 1:
        en_id = 2

    bot_line_score, en_line_score = 0, 0
    bot_surr_score, en_surr_score = 0, 0

    available_moves = engine.getAvailableMoves(board_state)

    if player_to_move == source_bot_id: # If the player to move is the BOT (Player-2)
        for move in available_moves:
            board_state_copy = board_state.copy()
            board_state_copy[move[0],move[1]] = source_bot_id # Simulate a Bot's move (i.e. Player-2)
            status = engine.checkIfWon(board_state_copy, source_bot_id) # Check if Won
            if status == 'WC2-win':
                bot_line_score += 10

            if status == 'WC1-win':
                bot_surr_score += 10
        w1, w2 = 10, 10  # High weights for the Bot's Scores
        w3, w4 = -1, -1  # Low weights (Non-zero) for the Enemy's Scores

    if player_to_move == en_id: # If the player to move is the USER (Player-1)
        for move in available_moves:
            board_state_copy = board_state.copy()
            board_state_copy[move[0],move[1]] = en_id # Simulate a User's move (i.e. Player-1)
            status = engine.checkIfWon(board_state_copy, en_id) # Check if Won
            if status == 'WC2-win':
                en_line_score += 10
            if status == 'WC1-win':
                en_surr_score += 10
        w1, w2 = 1, 1     # Low weights (Non-zero) for the Bot's Scores
        w3, w4 = -10, -10 # High weights for the Enemy's Scores

    score = w1*bot_line_score + w2*bot_surr_score + w3*en_line_score + w4*en_surr_score
    #print("score: ", score)
    return score


def _evalFn2(board_state, player_to_move, source_bot_id=2):
    ''' Checking if a player can win in one move and the risks of the opponent winning '''

    en_id = 1
    if source_bot_id == 1:
        en_id = 2

    bot_line_score, en_line_score = 0, 0
    bot_surr_score, en_surr_score = 0, 0

    available_moves = engine.getAvailableMoves(board_state)
    board_state_copy = board_state.copy()
    for move in available_moves:
        board_state_copy[move[0],move[1]] = source_bot_id # Simulate a Bot's move (i.e. Player-2)
        status = engine.checkIfWon(board_state_copy, source_bot_id) # Check if BOT has Won
        if status == 'WC2-win':
            bot_line_score += 10
        if status == 'WC1-win':
            bot_surr_score += 10

        board_state_copy[move[0],move[1]] = en_id # Simulate a User's move (i.e. Player-1)
        status = engine.checkIfWon(board_state_copy, en_id) # Check if USER has Won
        if status == 'WC2-win':
            en_line_score += 10
        if status == 'WC1-win':
            en_surr_score += 10

    if player_to_move == source_bot_id:# If the player at leaf the leaf is BOT
        w1, w2 = 20, 20                    # High +ve weights for the Bot's Scores
        w3, w4 = -1, -1                    # Low -ve weights for the USER's scores
    elif player_to_move == en_id:      # Else if the player at the leaf is USER
        w1, w2 = 1, 1                      # Low +ve weights for BOT's scores
        w3, w4 = -20, -20                  # High -ve weights for USER's scores

    random_feature = np.random.random_integers(-5,5)

    score = w1*bot_line_score + w2*bot_surr_score + w3*en_line_score + w4*en_surr_score + random_feature
    #print("score: ", score)
    return score

'''   Evaluation-function selector  '''
def Evaluate(board_state, eval_fn, player_to_move, source_bot_id=2):  # Heuristic function Selector
    if eval_fn == 'Fn1':
        return _evalFn1(board_state, player_to_move, source_bot_id)
    elif eval_fn == 'Fn2':
        return _evalFn2(board_state, player_to_move, source_bot_id)

################################################################################
'''             3-Player Bots (Search algorithm implementations)             '''
################################################################################

def RandomPlayer(board_state):
    ''' Random Player '''
    available_moves = engine.getAvailableMoves(board_state)
    return random.choice(available_moves)


def MinimaxPlayer(board_state, depth, player_minmax, plyr_id, eval_fn, source_bot_id, root): # By default, 'p2' => MAX ; 'p1' => MIN
    ''' Minimax Player '''
    best_move = None
    game_over = False
    en_id = 1
    if plyr_id == 1:
        en_id = 2

    last_move_by = en_id
    win_status = engine.checkIfWon(board_state, last_move_by)
    if win_status == 'WC1-win' or win_status == 'WC2-win':
        game_over = True

    if depth == 0 or game_over: # Evaluation of the board by the bot who's generating the move
        player_to_move = plyr_id
        score = Evaluate(board_state, eval_fn, player_to_move, source_bot_id)
        if game_over: # If GAME OVER
            if last_move_by == source_bot_id: # If the last move was played by the BOT, make its score INFINITY
                score += 100000
            else:                             # Else make it -INFINITY
                score -= 100000
        return score, None

    else:
        available_moves = engine.getAvailableMoves(board_state)
        if player_minmax == 'MAX':  # BOT is MAXimizing
            best_score = -10000    # Lower limit, ideally -infinity
            for child in available_moves:
                board_state_copy = board_state.copy()
                board_state_copy[child[0],child[1]] = plyr_id
                score, _ = MinimaxPlayer(board_state_copy, depth-1, 'MIN', en_id, eval_fn, source_bot_id, root=False)
                if score > best_score:
                    best_score = score
                    if root:
                        best_move = child  # For the root node to select a move
                        print("[bots]best_score:",best_score,"best_move: ",best_move)
        elif player_minmax == 'MIN':  # USER is MINimizing
            best_score = 10000     # Higher limit, ideally infinity
            for child in available_moves:
                board_state_copy = board_state.copy()
                board_state_copy[child[0],child[1]] = plyr_id
                score, _ = MinimaxPlayer(board_state_copy, depth-1, 'MAX', en_id, eval_fn, source_bot_id, root=False)
                if score < best_score:
                    best_score = score
    return [best_score, best_move]


def ABMinimaxPlayer(board_state, prev_move, depth, alpha, beta, player_minmax, plyr_id, eval_fn, source_bot_id, root=True, ordered_children=None): # 'p2' => MAX ; 'p1' => MIN
    ''' Alpha-Beta Minimax Player '''

    best_move = None
    game_over = False

    en_id = 1
    if plyr_id == 1:
        en_id = 2

    last_move_by = en_id
    win_status = engine.checkIfWon(board_state, last_move_by)
    if win_status == 'WC1-win' or win_status == 'WC2-win':
        game_over = True

    if depth == 0 or game_over: # Evaluation of the board by the bot who's generating the move
        player_to_move = plyr_id
        score = Evaluate(board_state, eval_fn, player_to_move, source_bot_id)
        if game_over: # If GAME OVER
            if last_move_by == source_bot_id: # If the last move was played by the BOT, make its score INFINITY
                score += 10000
            else:                             # Else make it -INFINITY
                score -= 10000
        return score, None, None

    else:
        available_moves = engine.getAvailableMoves(board_state)
        children = available_moves
        eval_info = []   # List to store the Eval scores or the children
        if ordered_children is not None:
            children = ordered_children

        if player_minmax == 'MAX':  # BOT is MAXimizing
            best_score = -10000   # Lower limit, ideally -INFINITY
            for child in children:
                board_state_copy = board_state.copy()
                board_state_copy[child[0],child[1]] = plyr_id  # plyr_id=2 for MAX player (BOT) by default(in Single Player mode)
                score, _, _ = ABMinimaxPlayer(board_state_copy, child, depth-1, alpha, beta, 'MIN', en_id, eval_fn, source_bot_id, root=False)
                eval_info.append([child, score])
                if score > best_score:
                    best_score = score
                    best_move = child  # For the ROOT node to select a move
                    if root:
                        print("[bots]best_score:",best_score,"best_move: ",best_move)
                alpha = max(alpha, score)
                if beta <= alpha:
                    #print("[bots]Pruning @ depth: ", depth)
                    break
        elif player_minmax == 'MIN':  # USER is MINimizing
            best_score = 10000     # Higher limit, ideally infinity
            for child in children:
                board_state_copy = board_state.copy()
                board_state_copy[child[0],child[1]] = plyr_id
                score, _, _ = ABMinimaxPlayer(board_state_copy, child, depth-1, alpha, beta,'MAX', en_id, eval_fn, source_bot_id, root=False)
                if score < best_score:
                    best_score = score
                beta = min(beta, score)
                if beta <= alpha:
                    #print("[bots]Pruning @ depth: ", depth)
                    break
    return best_score, best_move, eval_info

def NegamaxPlayer(board_state, depth, plyr_id, eval_fn, source_bot_id, root):
    ''' Negamax Player '''
    best_move = None
    game_over = False

    en_id = 1
    if plyr_id == 1:
        en_id = 2

    last_move_by = en_id
    win_status = engine.checkIfWon(board_state, last_move_by)
    if win_status == 'WC1-win' or win_status == 'WC2-win':
        game_over = True

    if depth == 0 or game_over: # Evaluation of the board by the bot who's generating the move
        player_to_move = plyr_id
        score = Evaluate(board_state, eval_fn, player_to_move, source_bot_id)
        if game_over: # If GAME OVER
            if last_move_by == source_bot_id: # If the last move was played by the BOT, make its score INFINITY
                score += 100000
            else:                             # Else make it -INFINITY
                score -= 100000
        if player_to_move != source_bot_id: # Eval score from the perspective of the MIN player at the leaf
            score = -score
        return score, None

    else:
        available_moves = engine.getAvailableMoves(board_state)
        best_score = -100000    # Lower limit, ideally -infinity
        for child in available_moves:
            board_state_copy = board_state.copy()
            board_state_copy[child[0],child[1]] = plyr_id   # Current player simulates a move
            passed_score, _ = NegamaxPlayer(board_state_copy, depth-1, en_id, eval_fn, source_bot_id, root=False)
            passed_score = -passed_score
            if passed_score > best_score:
                best_score = passed_score
                if root:
                    best_move = child  # For the root node to select a move
                    print("[bots]best_score:",best_score,"best_move: ",best_move)
    return [best_score, best_move]


def ABNegamaxPlayer(board_state, depth, alpha, beta, plyr_id, eval_fn, source_bot_id, root):
    ''' Alpha-Beta Negamax Player '''
    best_move = None
    game_over = False

    en_id = 1
    if plyr_id == 1:
        en_id = 2

    last_move_by = en_id
    win_status = engine.checkIfWon(board_state, last_move_by)
    if win_status == 'WC1-win' or win_status == 'WC2-win':
        game_over = True

    if depth == 0 or game_over: # Evaluation of the board by the bot who's generating the move
        player_to_move = plyr_id
        score = Evaluate(board_state, eval_fn, player_to_move, source_bot_id)
        if game_over: # If GAME OVER
            if last_move_by == source_bot_id: # If the last move was played by the BOT, make its score INFINITY
                score += 100000
            else:                             # Else make it -INFINITY
                score -= 100000
        if player_to_move != source_bot_id: # Eval score from the perspective of the MIN player at the leaf
            score = -score
        return score, None

    else:
        available_moves = engine.getAvailableMoves(board_state)
        best_score = -10000    # Lower limit, ideally -infinity
        for child in available_moves:
            board_state_copy = board_state.copy()
            board_state_copy[child[0],child[1]] = plyr_id  # Current player makes a move
            score, _ = ABNegamaxPlayer(board_state_copy, depth-1, -beta, -alpha, en_id, eval_fn,source_bot_id, root=False)
            score = -score
            if score > best_score:
                best_score = score
                best_move = child  # For the root node to select a move
                if root:
                    print("[bots]best_score:",best_score,"best_move: ",best_move)
            alpha = max(alpha,best_score)
            if alpha >= beta:
                #print("[bots]Pruning @ depth: ", depth)
                break
    return [best_score, best_move]


def ABNegamaxTTPlayer(board_state, prev_move, depth, alpha, beta, plyr_id, eval_fn, source_bot_id, root=True, ordered_children=None):
    ''' Alpha-Beta Negamax Player with Transposition Table '''
    best_move = None
    game_over = False
    eval_info = []   # List to store the Eval scores or the children

    en_id = 1
    if plyr_id == 1:
        en_id = 2
    last_move_by = en_id

    old_alpha = alpha # save original alpha value
    try:
        if not root:
            entry = engine.retrieveTTEntry(board_state) # Transposition-table lookup
            if entry['depth'] >= depth:
                if entry['flag'] == 'Exact':
                    #print("TT-exact")
                    return entry['value'], None, None
                elif entry['flag'] == 'LowerBound':
                    alpha = max(alpha, entry['value'])
                    #print("TT-lower bound")
                elif entry['flag'] == 'UpperBound':
                    beta = min(beta, entry['value'])
                    #print("TT-upper bound")
                if alpha >= beta:
                    return entry['value'], None, None
    except:
        entry = {'value':None, 'flag':None, 'depth':None}

    win_status = engine.checkIfWon(board_state, last_move_by)
    if win_status == 'WC1-win' or win_status == 'WC2-win':
        game_over = True

    if depth == 0 or game_over: # Evaluation of the board by the bot who's generating the move
        player_to_move = plyr_id
        score = Evaluate(board_state, eval_fn, player_to_move, source_bot_id)

        if game_over: # If GAME OVER
            if last_move_by == source_bot_id: # If the last move was played by the BOT, make its score INFINITY
                score += 100000
            else:                             # Else make it -INFINITY
                score -= 100000

        if player_to_move != source_bot_id: # Eval score from the perspective of the MIN player at the leaf
            score = -score

        return score, None, None

    best_score = -10000
    available_moves = engine.getAvailableMoves(board_state)
    children = available_moves

    if ordered_children is not None:
        children = ordered_children
    for child in children:
        board_state_copy = board_state.copy()
        board_state_copy[child[0],child[1]] = plyr_id
        score, _, _ = ABNegamaxTTPlayer(board_state_copy, child, depth-1, -alpha, -beta, en_id, eval_fn, source_bot_id, root=False, ordered_children=None)
        score = -score
        eval_info.append([child, score])
        if score > best_score:
            best_score = score
            best_move = child
            if root:
                print("[bots]best_score:",best_score,"best_move: ",best_move)
            if best_score >= alpha:
                alpha = best_score
            if best_score >= beta:
                #print("Pruning")
                break

    # Fail-low
    if best_score <= old_alpha:
        flag = 'UpperBound'
    # Fail-high
    elif best_score >= beta:
        flag = 'LowerBound'
    else:
        flag = 'Exact'

    TT_entry = {'value':best_score, 'flag':flag, 'depth':depth}
    engine.pushIntoTT(board_state, best_move, plyr_id, TT_entry)

    return best_score, best_move, eval_info
