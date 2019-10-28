'''
-ENGINE CORE-

This script defines the core of the game engine. It's made of following components:
    1. Global game variables
    2. Helper functions
    3. Win-condition-checking functions
    4. Gameplay functions (for performance testing, not used in GUI)
'''

__author__ = "Chinmay Rao (i6218054)"

import random, pickle, time
import numpy as np
import engine.engine_utils as engine_utils
import engine.game_board as game_board

np.random.seed(0)

################################################################################
'''                          1-GLOBAL GAME VARIABLES                         '''
################################################################################
NBHOOD_DICT = engine_utils.buildNeighborhoodDict()
BOARD_STATE = None
GAME_COUNT = 0
PLAYER_COLORS = None

TRANSPOSITION_TABLE = None
RANDOM_MATRIX = None
STATE_HASH = None
MOVE_HISTORY = [None]
################################################################################
'''                            2-HELPER FUNCTIONS                            '''
################################################################################
def getBoardState():
    return BOARD_STATE

def getGameCount():
    return GAME_COUNT

def setPlayerColors(player_colors):
    global PLAYER_COLORS
    PLAYER_COLORS = player_colors
    buildInitialTT()

def getPlayerColors():
    return PLAYER_COLORS

def getInitialBoardState():
    global BOARD_STATE

    BOARD_STATE = np.zeros((20,20), dtype=np.int8) - 9
    # Mark the on-board cells with '0' (empty)
    f=0
    for j in range(0,5):
        for i in range(5-j,5+10+j):
            BOARD_STATE[i,1+j+f] = 0
        for i in range(5-j,5+10+j+1):
            BOARD_STATE[i,1+1+j+f] = 0
        f += 1
    f=0
    for j in range(0,5):
        for i in range(1+j,19-j):
            BOARD_STATE[i,11+j+f] = 0
        if j!=4:
            for i in range(1+j+1,19-j):
                BOARD_STATE[i,11+1+j+f] = 0
        f += 1
    # Mark the cells with '1' for the USER(Player-1) and '2' for the BOT(Player-2)
    # player_colors list : [user color, bot color]
    if PLAYER_COLORS[0] == 'white':  # if Player-1(USER) color is WHITE
        BOARD_STATE[10,10] = 2 # central BLACK piece belongs to Player-2(BOT)
    elif PLAYER_COLORS[0] == 'black': # else
        BOARD_STATE[10,10] = 1 # central BLACK piece belongs to Player-1(USER)
    return BOARD_STATE


def updateBoardState(move, plyr_id):
    ''' Update the board state and return status after a move '''
    global BOARD_STATE, GAME_COUNT, MOVE_HISTORY
    BOARD_STATE[move[0],move[1]] = plyr_id
    status = checkIfWon(BOARD_STATE, plyr_id)
    player = 'p'+str(plyr_id)
    GAME_COUNT += 1
    MOVE_HISTORY.append(move)
    return BOARD_STATE, [status,player], GAME_COUNT

def reloadGame(board_state, player_colors, game_count):
    ''' Reload game from the last check move '''
    global BOARD_STATE, PLAYER_COLORS, GAME_COUNT
    BOARD_STATE = board_state
    PLAYER_COLORS = player_colors
    GAME_COUNT = game_count

def getAvailableMoves(board_state, first_move=False):
    ''' Return a list of legal/allowed moves '''
    if first_move:
        available_moves = [(9,9),(9,10),(9,11),(10,11),(11,10),(10,9)]
    else:
        user_pieces = np.argwhere(board_state == 1)
        bot_pieces = np.argwhere(board_state == 2)
        occupied_cells = np.vstack((user_pieces,bot_pieces))
        empty_cells = np.argwhere(board_state == 0)

        occupied_cells_neighbors = []
        for oc in occupied_cells:
            oc_nbrs = NBHOOD_DICT[tuple(oc)]
            for nbr in oc_nbrs:
                occupied_cells_neighbors.append(nbr)

        nbrs_of_2_plus = []
        for ocn in occupied_cells_neighbors:
            count = len([i for i in occupied_cells_neighbors if i == ocn])
            if count>1:
                nbrs_of_2_plus.append(ocn)

        available_moves = []
        for nc in nbrs_of_2_plus:
            for ec in empty_cells:
                if tuple(nc) == tuple(ec):
                    available_moves.append(nc)
        available_moves = list( dict.fromkeys(available_moves) ) # removing duplicates

    return available_moves

def buildInitialTT():
    ''' Initialize the TT at the start of the game  '''
    global TRANSPOSITION_TABLE, STATE_HASH, RANDOM_MATRIX
    TRANSPOSITION_TABLE = {}

    RANDOM_MATRIX = np.random.randint(low=1, high=10000, size=(20,20,3), dtype=np.int16)
    STATE_HASH = 0
    board_state = getBoardState()
    p1_pieces = np.argwhere(board_state == 1)
    p2_pieces = np.argwhere(board_state == 2)
    empty_cells = np.argwhere(board_state == 0)
    board_cells = np.vstack((p1_pieces,p2_pieces,empty_cells))

    for cell in board_cells:
        # Compute hash
        STATE_HASH = STATE_HASH ^ RANDOM_MATRIX[cell[0],cell[1],board_state[cell[0],cell[1]]]
    TRANSPOSITION_TABLE[str(STATE_HASH)] = dict({'value':None, 'flag':None, 'depth':None})

def pushIntoTT(board_state, move, plyr_id, TT_entry):
    ''' Write board info into the TT '''
    p1_pieces = np.argwhere(board_state == 1)
    p2_pieces = np.argwhere(board_state == 2)
    empty_cells = np.argwhere(board_state == 0)
    board_cells = np.vstack((p1_pieces,p2_pieces,empty_cells))

    state_hash = 0
    for cell in board_cells:
        # Compute hash
        state_hash = state_hash ^ RANDOM_MATRIX[cell[0],cell[1],board_state[cell[0],cell[1]]]

    TRANSPOSITION_TABLE[str(state_hash)] = dict({'value':TT_entry['value'], 'flag':TT_entry['flag'], 'depth':TT_entry['depth']})


def retrieveTTEntry(board_state):
    ''' Retrieve the info given a board state '''
    p1_pieces = np.argwhere(board_state == 1)
    p2_pieces = np.argwhere(board_state == 2)
    empty_cells = np.argwhere(board_state == 0)
    board_cells = np.vstack((p1_pieces,p2_pieces,empty_cells))

    state_hash = 0
    for cell in board_cells:
        # Compute hash
        state_hash = state_hash ^ RANDOM_MATRIX[cell[0],cell[1],board_state[cell[0],cell[1]]]
    return TRANSPOSITION_TABLE[str(state_hash)]

################################################################################
'''                       3-WINNING CONDITIONS CHECKING                      '''
################################################################################

def _floodfill(board_state_copy, coord, plyr_id, en_id):
    ''' Recursive Flood-Fill algorithm '''
    x, y = coord[0], coord[1]

    if board_state_copy[x,y] == 0 or board_state_copy[x,y] == en_id:
        board_state_copy[x,y] = 100
        # Recursively invoke flood fill on all surrounding cells:
        if x > 0: # Common (along each row)
            _floodfill(board_state_copy, (x-1,y), plyr_id, en_id)
        if x < 19:
            _floodfill(board_state_copy, (x+1,y), plyr_id, en_id)
        if y % 2 == 0:  # For Even rows
            if y > 0:
                _floodfill(board_state_copy, (x,y-1), plyr_id, en_id)
            if y < 19:
                _floodfill(board_state_copy, (x,y+1), plyr_id, en_id)
            if x > 0 and y > 0:
                _floodfill(board_state_copy, (x-1,y-1), plyr_id, en_id)
            if x > 0 and y < 19:
                _floodfill(board_state_copy, (x-1,y+1), plyr_id, en_id)
        if y % 2 == 1:  # For Odd rows
            if y > 0:
                _floodfill(board_state_copy, (x,y-1), plyr_id, en_id)
            if y < 19:
                _floodfill(board_state_copy, (x,y+1), plyr_id, en_id)
            if x < 19 and y > 0:
                _floodfill(board_state_copy, (x+1,y-1), plyr_id, en_id)
            if x < 19 and y < 19:
                _floodfill(board_state_copy, (x+1,y+1), plyr_id, en_id)


def checkWC1(board_state, plyr_id):
    ''' Winning Condition 1: Encircling '''
    status = None

    if plyr_id == 1:
        en_id = 2
    elif plyr_id == 2:
        en_id = 1

    seed_piece = random.choice([(5,1),(14,1),(19,10),(14,19),(5,19),(1,10)])
    board_state_copy = board_state.copy()
    _floodfill(board_state_copy, seed_piece, plyr_id, en_id)

    en_pieces = np.argwhere(board_state_copy == en_id)

    if len(en_pieces) > 0:
        status = 'WC1-win'
        #print("[engine]Surrounded!")
    return status

def checkWC2(board_state, plyr_id):
    ''' Winning Condition 2: 5-in-a-row '''

    status = None
    alt_board_state = engine_utils.getAltBoardState(board_state)
    plyr_pieces = [k for k,v in alt_board_state.items() if v == plyr_id]
    plyr_pieces.sort()

    # checking along the A-axis
    for pp in plyr_pieces:
        a_axis = pp[0]
        piece_count = 1
        pp2_prev = pp
        for pp2 in plyr_pieces:
            if pp2 != pp:
                if pp2[0] == a_axis and int(pp2[1]) == int(pp2_prev[1])+1:
                    piece_count += 1
                    pp2_prev = pp2
        if piece_count >= 5:
            status = 'WC2-win'
            #print("[engine]WC2-win along a_axis")
            return status
    # checking along the number axis
    for pp in plyr_pieces:
        num_axis = pp[1]
        piece_count = 1
        pp2_prev = pp
        for pp2 in plyr_pieces:
            if pp2 != pp:
                if pp2[1] == num_axis and ord(pp2[0]) == ord(pp2_prev[0])+1:
                    piece_count += 1
                    pp2_prev = pp2
        if piece_count >= 5:
            status = 'WC2-win'
            #print("[engine]WC2-win along num_axis")
            return status
    # checking along the cross-axis line
    for pp in plyr_pieces:
        piece_count = 1
        pp2_prev = pp
        for pp2 in  plyr_pieces:
            if pp2 != pp:
                if ord(pp2[0]) != ord(pp2_prev[0])+1:
                    continue
                elif ord(pp2[0]) == ord(pp2_prev[0])+1:
                    if int(pp2[1]) == int(pp2_prev[1])+1:
                        piece_count += 1
                        pp2_prev = pp2
            if piece_count >= 5:
                status = 'WC2-win'
                #print("[engine]WC2-win along cross-axis line")
                return status

def checkIfWon(board_state, plyr_id):
    status = None
    status = checkWC1(board_state, plyr_id)
    if status != 'WC1-win':
        status = checkWC2(board_state, plyr_id)
    return status

################################################################################
'''                           4-GAME-PLAY FUNCTIONS                          '''
################################################################################
def getUserMove(board_state, first_move=False):
    is_legal = False
    while not is_legal:
        user_move = []
        allowed_moves = getAvailableMoves(board_state, first_move)
        print("[engine]Available_moves: ", allowed_moves)
        user_move = input("Enter your move:   ").split(',') # Get input from user
        user_move = tuple([int(i) for i in user_move])
        if user_move in allowed_moves:
            is_legal = True
        else:
            print("[Illegal move!]")
    return user_move


def userPlay(board_state):  # USER's turn
    user_move = getUserMove(board_state)
    board_state, result, GAME_COUNT = updateBoardState(user_move, plyr_id=1)
    game_board.render(board_state, PLAYER_COLORS)

    with open('engine/save_file','wb') as file:  # Save the game state after user plays
        game_state = [board_state, PLAYER_COLORS, GAME_COUNT]
        pickle.dump(game_state, file)

    return board_state, result

def botPlay(Bot, board_state):   # BOT's turn
    bot_id = Bot.bot_id
    t1 = time.time()
    bot_move = Bot.generateMove(board_state)
    t2 = time.time()
    board_state, result, GAME_COUNT = updateBoardState(bot_move, plyr_id=bot_id)
    print("[engine]Search time: ", t2-t1)
    #game_board.render(board_state, PLAYER_COLORS)

    with open('engine/save_file','wb') as file: # Save the game state after computer plays
        game_state = [board_state, PLAYER_COLORS, GAME_COUNT]
        pickle.dump(game_state, file)

    return board_state, result

# ------------------------------------------------------------------------------

def playSinglePlayer(Bot, board_state, option):
    user_color = Bot.player_colors[0]
    if option == '1':     # Start NEW game
        game_board.render(board_state, PLAYER_COLORS) # Render initial board
        # 1st move -----------------------------------------------------------------
        if user_color == 'white':  # USER plays first
            print("\n----------  YOUR TURN  ---------- ")
            user_move = getUserMove(board_state, first_move=True)
            board_state, _, _ = updateBoardState(user_move, plyr_id=1)
            game_board.render(board_state, PLAYER_COLORS)
        else:                  # BOT plays first
            print("\n----------  COMPUTER'S TURN ---------- ")
            bot_move = Bot.generateFirstMove()
            board_state, _, _ = updateBoardState(bot_move, plyr_id=2)
            game_board.render(board_state, PLAYER_COLORS)
        # Continue the game --------------------------------------------------------
        if user_color == 'black': # USER continues after the BOT has played first
            while True:
                # USER's turn
                print("\n----------  YOUR TURN  ---------- ")
                board_state, result = userPlay(board_state)
                if (result[0] == 'WC1-win' or result[0] == 'WC2-win') and result[1] == 'p1':
                    print("-- User wins! --")
                    break
                # BOT's turn
                print("\n----------  COMPUTER'S TURN ---------- ")
                board_state, result = botPlay(Bot, board_state)
                if (result[0] == 'WC1-win' or result[0] == 'WC2-win') and result[1] == 'p2':
                    print("-- Computer wins! --")
                    break

        else:                # BOT continues after the USER has played first
            while True:
                # BOT's turn
                print("\n----------  COMPUTER'S TURN ---------- ")
                board_state, result = botPlay(Bot, board_state)
                if (result[0] == 'WC1-win' or result[0] == 'WC2-win') and result[1] == 'p2':
                    print("-- Computer wins! --")
                    break

                # USER's turn
                print("\n----------  YOUR TURN  ---------- ")
                board_state, result = userPlay(board_state)
                if (result[0] == 'WC1-win' or result[0] == 'WC2-win') and result[1] == 'p1':
                    print("-- User wins! --")
                    break

    elif option == '2' and GAME_COUNT > 0:  # RELOAD game
        game_board.render(board_state, PLAYER_COLORS)
        if GAME_COUNT%2 == 0: # If game count is EVEN -> White's turn
            if user_color == 'white':
                while True:
                    # USER's turn
                    print("\n----------  YOUR TURN  ---------- ")
                    board_state, result = userPlay(board_state)
                    if (result[0] == 'WC1-win' or result[0] == 'WC2-win') and result[1] == 'p1':
                        print("-- User wins! --")
                        break

                    # BOT's turn
                    print("\n----------  COMPUTER'S TURN ---------- ")
                    board_state, result = botPlay(Bot, board_state)
                    if (result[0] == 'WC1-win' or result[0] == 'WC2-win') and result[1] == 'p2':
                        print("-- Computer wins! --")
                        break
            else:                # BOT(black) continues after the USER(white) has played first
                while True:
                    # BOT's turn
                    print("\n----------  COMPUTER'S TURN ---------- ")
                    board_state, result = botPlay(Bot, board_state)
                    if (result[0] == 'WC1-win' or result[0] == 'WC2-win') and result[1] == 'p2':
                        print("-- Computer wins! --")
                        break

                    # USER's turn
                    print("\n----------  YOUR TURN  ---------- ")
                    board_state, result = userPlay(board_state)
                    if (result[0] == 'WC1-win' or result[0] == 'WC2-win') and result[1] == 'p1':
                        print("-- User wins! --")
                        break
        elif GAME_COUNT%1 == 0: # If game count is ODD -> Black's turn
            if user_color == 'white':
                while True:
                    # BOT's turn
                    print("\n----------  COMPUTER'S TURN ---------- ")
                    board_state, result = botPlay(Bot, board_state)
                    if (result[0] == 'WC1-win' or result[0] == 'WC2-win') and result[1] == 'p2':
                        print("-- Computer wins! --")
                        break
                    # USER's turn
                    print("\n----------  YOUR TURN  ---------- ")
                    board_state, result = userPlay(board_state)
                    if (result[0] == 'WC1-win' or result[0] == 'WC2-win') and result[1] == 'p1':
                        print("-- User wins! --")
                        break
            else:                # BOT(black) continues after the USER(white) has played first
                while True:
                    # USER's turn
                    print("\n----------  YOUR TURN  ---------- ")
                    board_state, result = userPlay(board_state)
                    if (result[0] == 'WC1-win' or result[0] == 'WC2-win') and result[1] == 'p1':
                        print("-- User wins! --")
                        break
                    # BOT's turn
                    print("\n----------  COMPUTER'S TURN ---------- ")
                    board_state, result = botPlay(Bot, board_state)
                    if (result[0] == 'WC1-win' or result[0] == 'WC2-win') and result[1] == 'p2':
                        print("-- Computer wins! --")
                        break
    return board_state


def playTestSinglePlayer(Bot, user_moves_list):
    ''' Play a test game with a fixed sequence of user's moves '''
    board_state = getInitialBoardState()
    print("-- TEST MODE --\n Black belongs to computer")
    game_board.render(board_state, PLAYER_COLORS) # Render initial board

    # 1st move -----------------------------------------------------------------
    print("\n----------  YOUR TURN  ---------- ")
    user_move = user_moves_list[0]
    print("Enter your move: ", user_move)
    board_state, _, _ = updateBoardState(user_move, plyr_id=1)
    game_board.render(board_state, PLAYER_COLORS)
    # Continue the game --------------------------------------------------------
    for i in range(1, len(user_moves_list)):
        # BOT's turn
        print("\n----------  COMPUTER'S TURN ---------- ")
        t1 = time.time()
        bot_move = Bot.generateMove(board_state)
        t2 = time.time()
        board_state, result, GAME_COUNT = updateBoardState(bot_move, plyr_id=2)
        print("[engine]Search time: ",  t2-t1)
        game_board.render(board_state, PLAYER_COLORS)
        if (result[0] == 'WC1-win' or result[0] == 'WC2-win') and result[1] == 'p2':
            print("-- Computer wins! --")
            break
        # USER's turn
        print("\n----------  YOUR TURN  ---------- ")
        user_move = user_moves_list[i]
        print("Enter your move: ", user_move)
        board_state, result, _ = updateBoardState(user_move, plyr_id=1)
        game_board.render(board_state, PLAYER_COLORS)
        if (result[0] == 'WC1-win' or result[0] == 'WC2-win') and result[1] == 'p1':
            print("-- User wins! --")
            break
    return board_state

def playBotvBot(Bot1, Bot2):
    board_state = getInitialBoardState()
    #game_board.render(board_state, PLAYER_COLORS) # Render initial board

    bot1_clr = PLAYER_COLORS[0]
    # 1st move -----------------------------------------------------------------
    if bot1_clr == 'white':  # BOT-1 plays first
        print("\n----------  BOT-1's TURN  ---------- ")
        bot1_move = Bot1.generateFirstMove()
        board_state, _, _ = updateBoardState(bot1_move, plyr_id=1)
        #game_board.render(board_state, PLAYER_COLORS)
    else:                  # BOT-2 plays first
        print("\n----------  BOT-2's TURN ---------- ")
        bot2_move = Bot2.generateFirstMove()
        board_state, _, _ = updateBoardState(bot2_move, plyr_id=2)
        #game_board.render(board_state, PLAYER_COLORS)
    # Continue the game --------------------------------------------------------
    if bot1_clr == 'black': # BOT-1 continues after BOT-2 has played first
        while True:
            # BOT-1's turn
            print("\n----------  BOT-1's TURN  ---------- ")
            board_state, result = botPlay(Bot1, board_state)
            if (result[0] == 'WC1-win' or result[0] == 'WC2-win') and result[1] == 'p1':
                print("-- Bot-1 wins! --")
                break
            # BOT-2's turn
            print("\n----------  BOT-2's TURN ---------- ")
            board_state, result = botPlay(Bot2, board_state)
            if (result[0] == 'WC1-win' or result[0] == 'WC2-win') and result[1] == 'p2':
                print("-- Bot-2 wins! --")
                break

    else:                # BOT-2 continues after BOT-1 has played first
        while True:
            # BOT-2's turn
            print("\n----------  BOT-2's TURN ---------- ")
            board_state, result = botPlay(Bot2, board_state)
            if (result[0] == 'WC1-win' or result[0] == 'WC2-win') and result[1] == 'p2':
                print("-- Bot-2 wins! --")
                break

            # BOT-1's turn
            print("\n----------  BOT-1's TURN  ---------- ")
            board_state, result = botPlay(Bot1, board_state)
            if (result[0] == 'WC1-win' or result[0] == 'WC2-win') and result[1] == 'p1':
                print("-- Bot-1 wins! --")
                break