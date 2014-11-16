# Driver script to run a game of Go in AI vs AI mode.
#
# CURRENTLY NOT VERY CLEVER, JUST MAKES RANDOM MOVES.

import GoGoGo
import random

# Main game loop.
if __name__ == '__main__':
    # Setup an empty 9x9 board
    board = GoGoGo.GoBoard(9)
    players = [GoGoGo.GoPlayer('b'), GoGoGo.GoPlayer('w')]

    # Black always makes the first move
    random.seed(0)
    players[0].make_random_move(board)
    print "Opening move:"
    print board

    # Take turns making moves until two consequtive passes occur, or
    # until one player is completely eliminated from the board.
    num_passes = 0
    move_num = 2
    active_player = players[1]
    other_player = players[0]
    while(num_passes < 2):
        try:
            active_player.make_random_move(board)
            num_passes = 0
        except RuntimeError, e:
            print str(e)+"\n"
            num_passes += 1
        
        # Calculate the current score
        score = board.score(players[0].color, players[1].color)
        
        # Report the game state
        print "Move %d: " % move_num
        print board
        print "Score: %d-%d.\n" % (score[0], score[1])
        move_num += 1

        # Did one player get entirely elminated? If so, game is over.
        if score[0] == 0:
            print "Black player lost all its stones!"
            break
        elif score[1] == 0:
            print "White player lost all its stones!"
            break
        
        # Toggle the player color
        other_player = active_player
        active_player = players[int(active_player.color == 'b')]

    # Finish up
    print "Game over."
    exit(0)
