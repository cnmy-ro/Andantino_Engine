'''
-GUI-based gameplay-

The GUI frontend of the game engine. Made up of the following sections:

    1. Settings- Contains bot parameters that can be set by the user:
        1.1. bot_algo- 'random', 'minimax', 'ab-minimax', 'negamax', 'ab-negamax',
                       'ab-minimax-ID', 'ab-negamax-TT', ab-negamax-TT-ID
        1.2. depth- Search depth
        1.3. ID_max_depth- Max depth for Iterative Deepening
        1.4. ID_max_time- Max time (in seconds) allowed to iteratively search deeper
        1.5. eval_fn- 'Fn1', 'Fn2'

    2. Start screen- Defines the start screen

    3. Game screen- Defines the game screen and all its components
'''

__author__ = "Chinmay Rao (i6218054)"

import pickle, time
import tkinter as tk
import engine.game_board as game_board
import engine.engine_utils as engine_utils
import engine.bots as bots
import engine.engine as engine

board_state = None
player_colors = [None, None]
game_count = 0
Bot = None
alt_to_def_mapping = engine_utils.getAltToDefMapping()
def_to_alt_mapping = engine_utils.getDefToAltMapping(alt_to_def_mapping)
game_option = ''

################################################################################
'''                               1-SETTINGS                                 '''
################################################################################
bot_algo = 'ab-negamax-TT-ID'
depth = 4
ID_max_depth = 3
ID_max_time = 15  # (seconds)
eval_fn = 'Fn2'

use_alt_coord = True
################################################################################
'''                             2-START SCREEN                               '''
################################################################################
start_window = tk.Tk()
start_window.wm_title("Start screen")

game_count_label = tk.Label(start_window, text='-ANDANTINO-')
game_count_label.config(font=("Courier", 44))
game_count_label.grid(row=0, column=0, columnspan=11, padx=10, pady=10)

def updateStartScreen(option):
    global board_state, player_colors, Bot, game_option, game_count
    game_option = option

    start_btn.grid_forget()
    reload_btn.grid_forget()

    if option == 'reload':
        with open('engine/save_file','rb') as file:
            game_state = pickle.load(file,encoding='bytes')
            board_state, player_colors, game_count = game_state
        with open('engine/bot_config','rb') as file:
            bot_config = pickle.load(file, encoding='bytes')
        engine.setPlayerColors(player_colors)
        Bot = bots.AndantinoBot(bot=bot_config[0], depth=bot_config[1], ID_max_depth=bot_config[2], ID_max_time=bot_config[3], eval_fn=bot_config[4])
        engine.reloadGame(board_state, player_colors, game_count)

        start_window.destroy()
        start_window.quit()
        return

    choose_clr_label.grid(row=2, column=4, columnspan=3, pady=10)
    clr_black.grid(row=3, column=2, columnspan=3, pady=10)
    clr_white.grid(row=3, column=6, columnspan=3, pady=10)

def setPlayerOneColor(color):
    global player_colors, board_state
    if color is 'black':
        player_colors = ['black', 'white']
    else:
        player_colors = ['white','black']

    engine.setPlayerColors(player_colors)
    board_state = engine.getInitialBoardState()

    global Bot
    Bot = bots.AndantinoBot(bot_algo, depth, ID_max_depth, ID_max_time, eval_fn, bot_id=2)  # inititalize the bot object
    with open('engine/bot_config','wb') as file:
        bot_config = [bot_algo, depth, ID_max_depth, ID_max_time, eval_fn]
        pickle.dump(bot_config, file)

    start_window.destroy()
    start_window.quit()

start_btn = tk.Button(start_window, text = "START", command = lambda:updateStartScreen(option='start'))
start_btn.grid(row=2, column=5, pady=10)

reload_btn = tk.Button(start_window, text = "RELOAD", command = lambda:updateStartScreen(option='reload'))
reload_btn.grid(row=3, column=5, pady=10)

choose_clr_label = tk.Label(start_window, text='CHOOSE COLOUR')
choose_clr_label.grid(row=2, column=4, columnspan=3, pady=10)
choose_clr_label.grid_forget()

clr_black = tk.Button(start_window, text = "Black", command = lambda:setPlayerOneColor('black'))
clr_black.grid(row=3, column=2, columnspan=3, pady=10)
clr_black.grid_forget()

clr_white = tk.Button(start_window, text = "White", command = lambda:setPlayerOneColor('white'))
clr_white.grid(row=3, column=6, columnspan=3, pady=10)
clr_white.grid_forget()

tk.mainloop()


################################################################################
'''                            3-GAME SCREEN                                 '''
################################################################################

game_window = tk.Tk()
game_window.wm_title("Andantino")

#-------------------------------------------------------------------------------
# Hex Grid
hex_grid = game_board.HexagonalGrid(game_window, scale=15, grid_width=21, grid_height=21)
hex_grid.grid(row=1, column=0, rowspan=21, columnspan=21, padx=5, pady=5)

# Render board state
def renderBoard():
    state_dict = game_board.getCoordinates(board_state, player_colors)

    for color, coords in state_dict.items():
        for coord in coords:
            hex_grid.setCell(coord[0], coord[1], fill=color)

    available_moves = engine.getAvailableMoves(board_state) # Highlight available moves
    for move in available_moves:
         hex_grid.setCell(move[0], move[1], fill='SpringGreen4')

def updateTerminal(prev_move, player_to_move, game_status, search_time=None):
    clearMessage()
    renderBoard()

    if game_status[0] is None:
        game_status = 'Game in progress'
    elif game_status[0] == 'WC1-win' or game_status[0] == 'WC2-win':
        if game_status[1] == 'p1':
            game_status = "USER WINS!"
            dispMessage(1,"Game status: " + str(game_status))
            return
        elif game_status[1] == 'p2':
            game_status = "COMPUTER WINS!"
            dispMessage(1,"Game status: " + str(game_status))
            return

    last_move_by = ''
    if player_to_move == 'USER':
        last_move_by = 'COMPUTER'
    elif player_to_move == 'COMPUTER':
        last_move_by = 'USER'

    game_count_label.config(text=str(engine.getGameCount()))
    first_move = False
    if engine.getGameCount() == 0:
        first_move = True

    allowed_moves = engine.getAvailableMoves(board_state, first_move)
    if use_alt_coord:
        if prev_move:
            prev_move = def_to_alt_mapping[prev_move]
            prev_move = prev_move[0] + str(prev_move[1])
        allowed_moves_alt = []
        for am in allowed_moves:
            am_alt = def_to_alt_mapping[am]
            am_alt = am_alt[0] + str(am_alt[1])
            allowed_moves_alt.append(am_alt)
        allowed_moves = allowed_moves_alt

    dispMessage(1,"GAME STATUS: " + str(game_status))
    dispMessage(2,'')
    dispMessage(3, 'PLAYER-1 (USER): ' + player_colors[0])
    dispMessage(4,'')
    dispMessage(5, 'PLAYER-2 (COMPUTER): ' + player_colors[1])
    dispMessage(6,'')
    dispMessage(7,'-------------------------------')
    dispMessage(8,'')
    if prev_move:
        dispMessage(9,last_move_by+'\'s move: '+str(prev_move))
        if search_time:
            dispMessage(10, "Search time: " + str(search_time))
    dispMessage(11,'')
    dispMessage(12,'')
    dispMessage(13, ">>> " + str(player_to_move) + "'s turn --")
    dispMessage(14,'')
    dispMessage(15, "Allowed moves: "+str(allowed_moves))

#-------------------------------------------------------------------------------
# Game Count
game_count_label = tk.Label(game_window, text='GAME STEP -')
game_count_label.grid(row=0, column=10, pady=10)

game_count_label = tk.Label(game_window, text=str(engine.getGameCount()))
game_count_label.grid(row=0, column=11, sticky='w')

#-------------------------------------------------------------------------------
# Display box
disp_box_label = tk.Label(game_window, text='MESSAGE')
disp_box_label.grid(row=2, column=22, sticky='w')

disp_box = tk.Listbox(game_window, height=20, width=50)
disp_box.grid(row=3, column=22, rowspan=10, columnspan=10)

scroll_bar = tk.Scrollbar(game_window)
scroll_bar.grid(row=3, column=33, rowspan=10, padx=10, pady=10)
disp_box.configure(xscrollcommand = scroll_bar.set)
scroll_bar.configure(command = disp_box.xview)

def dispMessage(i,text):
    disp_box.insert(i,text)

def clearMessage():
    disp_box.delete(0, tk.END)

#-------------------------------------------------------------------------------
# User input box
user_ip_label = tk.Label(game_window, text='USER INPUT')
user_ip_label.grid(row=15, column=24, sticky='w')

user_ip = tk.StringVar()
user_ip_entry = tk.Entry(game_window, textvariable=user_ip)
user_ip_entry.grid(row=16, column=24, padx=5, pady=5, sticky='w')

def userMove():
    global board_state
    clearMessage()

    allowed_moves = engine.getAvailableMoves(board_state)
    user_move = user_ip.get()

    if not use_alt_coord:
        user_move = user_move.split(',')
        user_move = tuple([int(i) for i in user_move])
        if engine.getGameCount() > 0 and user_move not in allowed_moves:
            dispMessage(tk.END, "Invalid move! Try again")
            dispMessage(tk.END, "Available moves: "+str(allowed_moves))
            return
    else:
        user_move_a = user_move[0].upper()
        user_move_1 = int(user_move[1:])
        user_move = (user_move_a, user_move_1)
        user_move = alt_to_def_mapping[user_move]
        allowed_moves_alt = []
        for am in allowed_moves:
            am_alt = def_to_alt_mapping[am]
            am_alt = am_alt[0] + str(am_alt[1])
            allowed_moves_alt.append(am_alt)
        if engine.getGameCount() > 0 and user_move not in allowed_moves:
            dispMessage(tk.END, "Invalid move! Try again")
            dispMessage(tk.END, "Available moves: "+str(allowed_moves_alt))
            return

    board_state, result, game_count = engine.updateBoardState(user_move, plyr_id=1)
    with open('engine/save_file','wb') as file: # Save the game state after user plays
        game_state = [board_state, player_colors, engine.getGameCount()]
        pickle.dump(game_state, file)

    updateTerminal(prev_move=user_move, player_to_move='COMPUTER', game_status=result)
    #allowed_moves = engine.getAvailableMoves(board_state, first_move='False')
    begin_search_btn.grid(row=19, column=24, sticky='w')
    enter_btn.grid_forget()

enter_btn = tk.Button(game_window, text = "ENTER", command = lambda:userMove())
enter_btn.grid(row=16, column=25, sticky='w')
enter_btn.grid_forget()

#-------------------------------------------------------------------------------
# Bot section
bot_section_label = tk.Label(game_window, text='BOT SECTION')
bot_section_label.grid(row=18, column=24, sticky='w')

def botMove():
    global board_state
    clearMessage()
    t1 = time.time()
    dispMessage(tk.END, "Searching...")
    if engine.getGameCount() == 0:
        bot_move = Bot.generateFirstMove()
    elif engine.getGameCount() > 0:
        bot_move = Bot.generateMove(board_state)
    t2 = time.time()
    #dispMessage(tk.END, "Search time: " + str(t2-t1))
    board_state, result, game_count = engine.updateBoardState(bot_move, plyr_id=2)

    with open('engine/save_file','wb') as file: # Save the game state after computer plays
        game_state = [board_state, player_colors, engine.getGameCount()]
        pickle.dump(game_state, file)

    updateTerminal(prev_move=bot_move, player_to_move='USER', game_status=result, search_time = t2-t1)

    begin_search_btn.grid_forget()
    enter_btn.grid(row=16, column=25, sticky='w')


begin_search_btn = tk.Button(game_window, text = "Initiate search", command = lambda:botMove())
begin_search_btn.grid(row=19, column=24, sticky='w')
begin_search_btn.grid_forget()

#-------------------------------------------------------------------------------
if game_option == 'start':
    if player_colors[0] == 'white':
        player_to_move = 'USER'
        enter_btn.grid(row=16, column=25, sticky='w')
    else:
        player_to_move = 'COMPUTER'
        begin_search_btn.grid(row=19, column=24, sticky='w')
    game_status = 'Game started'

elif game_option == 'reload':
    if game_count % 2 == 0:
        if player_colors[0] == 'white':
            player_to_move = 'USER'
            enter_btn.grid(row=16, column=25, sticky='w')
        else:
            player_to_move = 'COMPUTER'
            begin_search_btn.grid(row=19, column=24, sticky='w')
    else:
        if player_colors[0] == 'white':
            player_to_move = 'COMPUTER'
            begin_search_btn.grid(row=19, column=24, sticky='w')
        else:
            player_to_move = 'USER'
            enter_btn.grid(row=16, column=25, sticky='w')
    game_status = 'Game in progress'

updateTerminal(None, player_to_move, game_status)
tk.mainloop()
