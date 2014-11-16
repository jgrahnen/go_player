# Driver script to run Go AI vs a human player.
#
# ARTIFICIALLY STUPID AT PRESENT, JUST MAKES RANDOM MOVES...

import GoGoGo
import random
import sys

# Main game loop.
if __name__ == '__main__':
    # Parse input arguments
    args = ['board size']
    if len(sys.argv)-1 < len(args):
        print "Usage: python "+sys.argv[0]+" "+" ".join(["[%s]" % arg for arg in args])
        exit(1)
    board_size = int(sys.argv[1])

    # Instructions
    print "Welcome to GoGoGo!"
    print ""
    print "You will be playing as the black player (b), against the white AI player (w),"
    print "on a %d,%d board." % (board_size, board_size)
    print ""
    print "During each turn, you can:"
    print "\t* Place a black stone by specifying a position as 'row,column'."
    print "\t* Pass by typing 'pass'."
    print "\t* Quit by typing Ctrl-C (or otherwise issuing a keyboard interrupt)."
    print ""
    print "The game will continue until both players pass, or until one player"
    print "has no stones left on the board."

    # Setup an empty NxN board
    board = GoGoGo.GoBoard(board_size)
    human_player = GoGoGo.GoPlayer('b')
    ai_player = GoGoGo.GoPlayer('w')
    random.seed(0)
    print board

    # Black (human) always makes the first move
    move_made = False
    while not move_made:
        print "Make an opening move (x,y):"
        # Parse the move
        move_made = human_player.parse_and_move(sys.stdin, board)

    print "Opening move:"
    print board

    # Take turns making moves until two consequtive passes occur, or
    # until one player is completely eliminated from the board.
    move_num = 2
    conseq_passes = 0
    while conseq_passes < 2:
        # Computer tries to make a move.
        try:
            ai_player.make_random_move(board)
            conseq_passes = 0
        except RuntimeError, e:
            print str(e)+"\n"
            conseq_passes += 1
        
        # Calculate the current score
        score = board.score(human_player.color, ai_player.color)
        
        # Report the game state
        print "Move %d: " % move_num
        print board
        print "Score: %d-%d.\n" % (score[0], score[1])
        move_num += 1

        # Did the human player get eliminated? If so, finish.
        if score[0] == 0:
            print "Black player lost all its stones!"
            break
        
        # Human player makes a move or passes
        made_move = False
        while not made_move:
            print "Make a move (x,y):"
            try:
                made_move = human_player.parse_and_move(sys.stdin, board)
                conseq_passes = 0
            except RuntimeError:
                conseq_passes += 1
                break

        # Calculate the current score
        score = board.score(human_player.color, ai_player.color)

        # Did the AI player get eliminated? If so, finish.
        if score[1] == 0:
            print "White player lost all its stones!"
            break

    # Finish up
    print "Game over."
    exit(0)
