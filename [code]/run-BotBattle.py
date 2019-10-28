'''
-BATTLE OF THE BOTS-

Note: No GUI. The gameplay log is generated on the command line.
'''

__author__ = "Chinmay Rao"

import engine.bots as bots
import engine.engine as engine


player_colors = ['white', 'black']     # [Bot-1 color, Bot-2 color]

engine.setPlayerColors(player_colors)

# WHITE
Bot1 = bots.AndantinoBot(bot='ab-negamax-TT-ID', depth=3,
                         ID_max_depth=3, ID_max_time=15,
                         eval_fn='Fn2', bot_id=1)
# BLACK
Bot2 = bots.AndantinoBot(bot='ab-negamax-TT-ID', depth=3,
                         ID_max_depth=3, ID_max_time=15,
                         eval_fn='Fn2', bot_id=2)

initial_board_state = engine.getInitialBoardState()

print("\n--------------- ANDANTINO ----------------")
final_board_state = engine.playBotvBot(Bot1, Bot2)