# Module that provides basic machinery to play Go (as per Tromp-Taylor
# rules).
#
# NEEDS SOME TEST CASES: WIKI HAS A BUNCH. ALSO, ABSTRACT OUT THE GO BOARD
# INTO A SEPARATE MODULE (AND INCLUDE A GoPlayer CLASS THERE AS WELL). CAN PUT
# THE TEST CASES IN THERE.

import random
import sys
import copy

empty_char = '+'

# COMPLEX FUNCTIONS (DFS, SCORING, MOVE DETERMINATION) NEED TESTS
class GoBoard:
    # Setup an empty board
    def __init__(self, size=9):
        if not isinstance(size, int) or size < 1:
            raise TypeError("Board size must be a positive integer!")

        self.states = []
        self.states.append([[empty_char for i in range(size)] for j in range(size)])
        self.size = size

    # Human-readable version of the current board state 
    def __str__(self):
        output = "  "+" ".join(str(x) for x in range(1,self.size+1))+"\n"
        # Row-wise board representation
        for x in range(self.size):
            output += str(x+1)+" "+" ".join(self.states[-1][x])+"\n"

        return output

    # Is a particular location within this board?
    def on_board(self, position):
        if position[0] < 0 or position[1] < 0 or position[0]+1 > self.size or position[1]+1 > self.size:
            return False
        else:
            return True

    # Is a particular location empty?
    def is_empty(self, position):
        if self.on_board(position) and self.states[-1][position[0]][position[1]] == empty_char: 
            return True
        else:
            return False 

    # Return all open positions on the board.
    def open_intersections(self):
        pos = []
        for x in range(self.size):
            for y in range(self.size):
                if self.is_empty((x,y)):
                    pos.append((x,y))
        
        return pos

    # Can you locate a position of a particular color, using only
    # positions of some color to form the search path?
    def path_exists(self, from_pos, target_color, path_color, checked):
        # Did we already look here?
        if from_pos in checked:
            return False

        # Apparently not, let's go ahead and take a gander
        curr_pos = from_pos
        checked.append(curr_pos)

        # Is this location even on the board?
        if not self.on_board(curr_pos):
            return False

        # Is this position of the target color (i.e. did we find what
        # we are looking for)?
        if self.states[-1][curr_pos[0]][curr_pos[1]] == target_color:
            return True
        
        # Is this position of the path color (i.e. can you go this
        # way)?
        if self.states[-1][curr_pos[0]][curr_pos[1]] != path_color:
            return False

        # Okay, keep searching (DFS) for the color of interest 
        neighbors = ((-1,0), (1,0), (0,-1), (0,1))
        for (dx,dy) in neighbors:
            next_pos = (curr_pos[0]+dx, curr_pos[1]+dy)
            if self.path_exists(next_pos, target_color, path_color, checked):
                return True

        # Guess there's not a path to be found...
        return False

    # Is there an empty position (a liberty) next to this stone or next to
    # a stone connected to it?
    def has_liberty(self, color, location, checked_locs):
        # Is this position even inside the playing field?
        if not self.on_board(location):
            return False

        # Okay, which color are we examining liberties for?
        local_color = self.states[-1][location[0]][location[1]]

        # This is an empty square, so it is it's own liberty.
        if local_color == empty_char:
            return True

        # There's a stone here. Can you find a connected path of stones with 
        # the same color leading to an empty square?
        already_checked = []
        if self.path_exists(location, empty_char, local_color, already_checked):
            return True
        else:
            return False

    # Attempt to play a particular color at some position.
    #
    # Raises a RuntimeError if the move is illegal.
    def make_move(self, color_played, move):
        # Step 1: Can you place a stone here?
        if not self.on_board(move):
            raise RuntimeError("Illegal move: can't place stones outside the board!")
        if not self.is_empty(move):
            raise RuntimeError("Illegal move: can't place stones on each other!")

        # Make a new board state and color the point
        self.states.append(copy.deepcopy(self.states[-1]))
        self.states[-1][move[0]][move[1]] = color_played

        # Step 2: Remove opposing stones with no liberties
        print "Removing non-%s stones without liberties..." % color_played
        to_remove = []
        for x in range(self.size):
            for y in range(self.size):
                checked = []
                local_color = self.states[-1][x][y]
                if local_color != color_played \
                        and not self.has_liberty(local_color, (x,y), checked):
                    print "\tNo liberties for "+str(x+1)+","+str(y+1)+", removing."
                    to_remove.append((x,y))
        for location in to_remove: 
            self.states[-1][location[0]][location[1]] = empty_char
    
        # Step 3: Check if it killed any of my stones (illegal under suicide 
        # rule)
        print "Checking for %s stones without liberties..." % color_played
        for x in range(self.size):
            for y in range(self.size):
                checked = []
                local_color = self.states[-1][x][y]
                if local_color == color_played \
                        and not self.has_liberty(color_played, (x,y), checked):

                    # Re-wind the board state.
                    self.states.pop()
                    
                    # Stop right here.
                    raise RuntimeError("Illegal move: your stone at %d,%d is dead (no suicides)!" % (x+1, y+1))

        # Step 4: Check for positional superko (may not repeat board states)
        print "Checking for previous board states identical to this one..."
        for state in self.states[:-1]:
            if state == self.states[-1]:
                self.states.pop()
                raise RuntimeError("Illegal move: repeats a previous board state!")

    # Score the game, according to Taylor-Trump rules (i.e. NZ rules, Chinese 
    # area scoring), as if it ended in the current state.
    def score(self, first_color, second_color):
        print "Scoring..."
        score_first = 0
        score_second = 0

        # Number stones contribute
        for x in range(self.size):
            for y in range(self.size):
                if self.states[-1][x][y] == first_color:
                    score_first += 1
                elif self.states[-1][x][y] == second_color:
                    score_second += 1

        # Number of intersections in each player's territory
        # contribute
        for pos in self.open_intersections():
            # Can you find a path to a stone of the first color?
            already_checked = []
            path_to_first = self.path_exists(pos, first_color, empty_char, already_checked)

            # How about one to the second color?
            already_checked = []
            path_to_second = self.path_exists(pos, second_color, empty_char, already_checked)

            # If you can find paths to both, it's neutral territory;
            # otherwise, to whichever color is found
            if path_to_first and path_to_second:
                continue
            elif path_to_first:
                #print "\tPosition (%d,%d) is in '%s' territory." % (pos[0]+1, pos[1]+1, first_color)
                score_first += 1
            elif path_to_second:
                #print "\tPosition (%d,%d) is in '%s' territory." % (pos[0]+1, pos[1]+1, second_color)
                score_second += 1
            else:
                raise RuntimeError("Couldn't score position (%d,%d)!" % (pos[0]+1, pos[1]+1))

        return (score_first, score_second)

# NEEDS TESTS, PERIOD.
#
# MAJOR INCREMENTAL IMPROVEMENT: GAINING THE ABILITY TO PASS (SO AS TO
# AVOID MOVES THAT FILL IN EYES, ETC.).
class GoPlayer:
    def __init__(self, color='b'):
        self.color = color

    # Attempts to make a random legal move.
    #
    # If no legal move exists, raises a RuntimeError.
    def make_random_move(self, board):
        move_set = board.open_intersections()
        random.shuffle(move_set)
        made_move = False
        for move in move_set:
            try:
                print "Trying to play %s at %d,%d." % (self.color, move[0]+1, move[1]+1)
                board.make_move(self.color, move)
                made_move = True
                break
            except RuntimeError, e:
                print str(e)+"\n"
        
        if not made_move:
            raise RuntimeError("No moves possible, passing...")

    # Parses and makes a move from an open input file (could be e.g. 
    # sys.stdin). Moves are on single lines, of the form 'x,y' (row, column) 
    # or the string 'pass'. 
    #
    # Returns whether or not the move could successfully be completed.
    #
    # Raises a RuntimeError if the player passes.
    def parse_and_move(self, in_file, board):
        in_str = in_file.readline().rstrip("\n")
        if in_str == 'pass':
            raise RuntimeError("Passed, not placing stones.")
        else:
            try:
                (x,y) = in_str.split(',')
                intersection = (int(x)-1, int(y)-1)
                move_successful = self.place_stone(intersection, board)
            except ValueError:
                print "Moves must be given on the form row,column!"
                move_successful = False
        
        return move_successful

    # Attempts to place a stone at a particular position.
    #
    # Returns True if the move was legal, False otherwise (and prints
    # the reason for the failure to STDOUT).
    def place_stone(self, intersection, board):
        try:
            board.make_move(self.color, intersection)
            return True
        except RuntimeError, e:
            print str(e)+"\n"
            return False

# Run unit tests
if __name__ == '__main__':
    import unittest

    # Board setup
    class TestBoardSetup(unittest.TestCase):
        def test_sizing(self):
            self.assertEqual(GoBoard().size, 9)
            self.assertEqual(GoBoard(19).size, 19)
            self.assertRaises(TypeError, GoBoard, -1)
        
        def test_init_state(self):
            board = GoBoard()
            
            for x in range(board.size):
                for y in range(board.size):
                    self.assertTrue(board.is_empty, (x,y))
            
            self.assertFalse(board.on_board((board.size,board.size-1)))
            self.assertFalse(board.on_board((board.size-1,board.size)))
            self.assertFalse(board.on_board((-1,board.size-1)))
            self.assertFalse(board.on_board((board.size-1,-1)))
            self.assertTrue(board.on_board((board.size-1,board.size-1)))
            self.assertTrue(board.on_board((0,0)))
    
            self.assertTrue(len(board.open_intersections()) == board.size*board.size)
    
        def test_string_rep(self):
            board = GoBoard(3)
            self.assertEqual(str(board), '  1 2 3\n1 + + +\n2 + + +\n3 + + +\n')

    unittest.main()

    exit(0)
