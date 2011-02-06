# A simple player that just tries to hit children on the opponent's
# team with snowballs.
#
# Feel free to use this as a starting point for your own player.
# Also, feel free to send in refinements or fixes to this code.  I'm
# not a python programmer.
#
# ICPC Challenge
# Sturgill, UNC Greensboro

import random
import sys
import string
import unittest

# Constants supporting a player in the icypc challenge game.  Feel
# free to use this and extend it for your own implementation.

# Width and height of the playing field.
SIZE = 31

# Number of children on each team.
CCOUNT = 4

# Constants for the objects in each cell of the field
GROUND_EMPTY = 0  # Just powdered snow in this space.
GROUND_TREE = 1   # A tree in this space
GROUND_S = 2      # A small snowball in this space
GROUND_M = 3      # A medium snowball in this space
GROUND_MS = 4     # A small snowball on a medium one
GROUND_L = 5      # A large snowball in this space
GROUND_LM = 6     # A medium snowball on a large one.
GROUND_LS = 7     # A small snowball on a large one.
GROUND_SMR = 8    # A red Snowman in this space
GROUND_SMB = 9    # A blue Snowman in this space

# Constants for the things a child can be holding
HOLD_EMPTY = 0    # Child is holding nothing
HOLD_P1 = 1       # Child is holding one unit of powdered snow
HOLD_P2 = 2       # Child is holding two units of powdered snow
HOLD_P3 = 3       # Child is holding three units of powdered snow
HOLD_S1 = 4       # Child is holding one small snowball.
HOLD_S2 = 5       # Child is holding two small snowballs.
HOLD_S3 = 6       # Child is holding three small snowballs.
HOLD_M = 7        # Child is holding one medium snowball.
HOLD_L = 8        # Child is holding one large snowball.

# Constant for the red player color
RED = 0

# Constant for the blue player color
BLUE = 1

# Height for a standing child.
STANDING_HEIGHT = 9

# Height for a crouching child.
CROUCHING_HEIGHT = 6

# Maximum Euclidean distance a child can throw.
THROW_LIMIT = 24

# Snow capacity limit for a space.
MAX_PILE = 9

# Snow that's too deep to move through.
OBSTACLE_HEIGHT = 6

# Constant used to mark child locations in the map, not used in this player.
GROUND_CHILD = 10

# Representation of a 2D point, used for playing field locations.
class Point:
    def __init__( self, xv, yv ):
        self.x = xv
        self.y = yv
    def set( self, vx, vy ):
        self.x = vx
        self.y = vy
    def __eq__(self, other):
        if other == None:
            return False
        else:
            return self.__dict__ == other.__dict__
    def __ne__(self, other):
        if other == None:
            return True
        else:
            return self.__dict__ != other.__dict__

# Simple representation for a child in the game.
class Child:
    def __init__( self ):
        # Location of the child.
        self.pos = Point( 0, 0 )

        # True if  the child is standing.
        self.standing = 1
    
        # Side the child is on.
        self.color = RED
    
        # What's the child holding.
        self.holding = HOLD_EMPTY
    
        # How many more turns this child is dazed.
        self.dazed = 0

        # Last location child attempted to pickup snow.
        self.last_pickup = Point( 0, 0 )

        self.mode = 0  
        # 0 = move to position.  (while looking for victims)
        # 1 = (if no victims) drop small snowball and make a snowman 
        # 2 = just look for victims, and do a better job of searching for them.


# Simple representation for a child's action
class Move:
    # Action the child is making.
    action = "idle"

    # Destiantion of this action (or null, if it doesn't need one) */
    dest = None

# Return the value of x, clamped to the [ a, b ] range.
def clamp( x, a, b ):
    if x < a:
        return a
    if x > b:
        return b
    return x

def moveOrRandom(c,px,py,m):
    if can_move(px,py):
        m.dest = Point(px,py)
    else:
        valid_random_movement(c,m)

# Fill in move m to move the child c twoard the given target location, either
# crawling or running.
def moveToward( c, target, m ):
    if c.standing:
        # Run to the destination
        if c.pos.x != target.x:
            if c.pos.y != target.y:
                # Run diagonally.
                m.action = "run"
                px = c.pos.x + clamp( target.x - c.pos.x, -1, 1 )
                py = c.pos.y + clamp( target.y - c.pos.y, -1, 1 )
                moveOrRandom(c,px,py,m)
            else:
                # Run left or right
                m.action = "run"
                px = c.pos.x + clamp( target.x - c.pos.x, -2, 2 )
                py = c.pos.y
                # Check both spaces!!! (closer one first)
                moveOrRandom(c,px,py,m)
        elif c.pos.y != target.y:
            # Run up or down.
            m.action = "run"
            px = c.pos.x 
            py = c.pos.y + clamp( target.y - c.pos.y, -2, 2 )
            # Check both spaces!!! (closer one first)
            moveOrRandom(c,px,py,m)
    else:
        # Crawl to the destination
        if c.pos.x != target.x:
            # crawl left or right
            m.action = "crawl"
            px = c.pos.x + clamp( target.x - c.pos.x, -1, 1 )
            py = c.pos.y
            moveOrRandom(c,px,py,m)
        elif c.pos.y != target.y:
            # crawl up or down.
            m.action = "crawl"
            px = c.pos.x 
            py = c.pos.y + clamp( target.y - c.pos.y, -1, 1 )
            moveOrRandom(c,px,py,m)


# show height of thrown snowball for each step up to n steps.
def show_heights(h, n):
    for t in range(n+1):
        height = h - round((9 * t)/n)
        print height

def dist(dx, dy):
    return math.sqrt(dx * dx + dy * dy)

def can_c_hit_snowman_head(c, sx, sy, height):
    dx = abs(c.pos.x - sx)
    dy = abs(c.pos.y - sy)
    steps = max(dx, dy)

    # At time t/n, the entity moves to integer location 
    # ( x1 + round( ( t ( x2 - x1 ) )/n ), y1 + round( ( t ( y2 - y1 ) )/n ) )

# is the path one that can be walked and/or thrown
# if there is a tree or child in the way, it can't.
def good_path(x1,y1,x2,y2):
    pass

def random_movement(c):
    if c.standing:
        options = [(-2,0),(-1,0,),(-1,-1),(0,2),(0,1),(1,1),(1,0),(2,0),(1,-1),(0,-1),(0,-2),(-1,-1)]
        return options[int(round(rnd.uniform(0,11)))]
    else:
        options = [(-1,0),(0,1),(1,0),(0,-1)]
        return options[int(round(rnd.uniform(0,3)))]

# is location px, py valid (on the board)
# and available to move to?
#  px = c.pos.x + dx
#  py = c.pos.y + dy
def can_move(px, py):
    global ground
    global height
    if (px >= 0 and px < SIZE and
        py >= 0 and py < SIZE and
        # no trees or children
        height[px][py] < 6 and 
        ground[px][py] != GROUND_TREE and
        ground[px][py] != GROUND_CHILD and
        ground[px][py] != GROUND_SMR and     # these last two probably redundant
        ground[px][py] != GROUND_SMB):
        return True
    else:
        return False

def valid_random_movement(c, m):
    valid = False
    p = (0,0)

    while valid == False:
        p = random_movement(c)
        if can_move(c.pos.x + p[0], c.pos.y + p[1]):
            valid = True
        else:
            valid = False

    if c.standing:
        m.action = "run"
        m.dest = Point(c.pos.x + p[0], c.pos.y + p[1])
    else:
        m.action = "crawl"
        m.dest = Point(c.pos.x + p[0], c.pos.y + p[1])


# come up with a list of potential victims... 
# current criteria is just "in range" 
# TODO: consider the path to the target. If it is blocked, it's not a good target...
def victims_in_range(c, cList):
    vics = []

    j = CCOUNT
    while j < CCOUNT * 2:
        if cList[ j ].pos.x >= 0:
            # We know where this child is, see if it's not too far away.
            dx = cList[ j ].pos.x - c.pos.x
            dy = cList[ j ].pos.y - c.pos.y
            #steps = max(dx,dy)
            dsq = dx * dx + dy * dy

            if dsq < 8 * 8:
                vics.append((dx,dy,dsq,cList[j].holding,cList[j].dazed))
        j += 1
    return vics

# if the victims are dazed, we should aim for the one that is the least dazed.
# aim for closest, as we are likely to hit it.
# if a victim is holding a medium or large snowball target them to disrupt them  .. also likely to be standing still.

# snowball 0(none) 1(small) 2(med)
# dazed 0 .. 4
# dsq (distance) ....

def choose_victim(vics):
    vics.sort(lambda x,y:cmp(x[2],y[2])) # dsq 
    vics.sort(lambda x,y:cmp(x[4],y[4])) # dazed
    vics.sort(lambda x,y:cmp(x[3],y[3]), reverse=True)  # holding.  
    return vics[0]

def target_victim(c, vic, m):
    m.action = "throw"
    # throw past the victim, so we will probably hit them
    # before the snowball falls into the snow.
    m.dest = Point( c.pos.x + vic[0] * 2,
                    c.pos.y + vic[1] * 2 )
    # but if something's in the way, like a tree, 
    # or a snowman that we can't throw over
    # or your own guy (although your own guy could move in this turn?), 
    # then it doesnt make sense to throw, because it will just be
    # blocked, or you will hit your own guy



########################################################################################

# Source of randomness
rnd = random.Random()

# Current game score for self (red) and opponent (blue).
score = [ 0, 0 ]

# Current snow height in each cell.
height = []

# Contents of each cell.
ground = []

# Allocate the whole field.  Is there a better way to do this?
for i in range( SIZE ):
    height.append( [ 0 ] * SIZE )
    ground.append( [ 0 ] * SIZE )

# List of children on the field, half for each team.
cList = []

# Random destination for each player.
runTarget = []

# How long the child has left to run toward its destination.
runTimer = []

for i in range( 2 * CCOUNT ):
    cList.append( Child() )
    runTarget.append( Point( 0, 0 ) )
    runTimer.append( 0 )

def init_ground():
    for i in range(SIZE):
        for j in range(SIZE):
            height[i][j] = 3
            ground[i][j] = GROUND_EMPTY

def snowball_matcher(ox, oy):
    return (ground[ ox ][ oy ] == GROUND_S or
            ground[ ox ][ oy ] == GROUND_MS or
            ground[ ox ][ oy ] == GROUND_LS)

def snow_matcher(ox, oy):
    return (ground[ ox ][ oy ] == GROUND_EMPTY and 
            height[ ox ][ oy ] > 0)

def look_for(c, matcher):
    for oy in range( c.pos.y + 1, c.pos.y - 2, -1 ):
        for ox in range( c.pos.x + 1, c.pos.x - 2, -1 ):
            # Is there snow to pick up?
            if ( ox >= 0 and ox < SIZE and
                 oy >= 0 and oy < SIZE and
                 ( ox != c.pos.x or oy != c.pos.y ) and
                 matcher(ox, oy) == True):
                return (ox, oy)
    return (-1, -1)

def look_for_small_snowball(c):
    return look_for(c, snowball_matcher)

def look_for_snow(c):
    return look_for(c, snow_matcher)

def xy_for_step_s(c, s, dx, dy, steps):
    atx = c.pos.x + int(round( float( s * ( dx ) )/float(steps) ))
    aty = c.pos.y + int(round( float( s * ( dy ) )/float(steps) ))
    return (atx, aty)

class TestTargeter(unittest.TestCase):
    def setUp(self):
        init_ground();
        self.c = Child()
        self.c.pos = Point(15,15)  # middle

    def testRight(self):
        for i in range(0, 11):
            self.assertEqual((15+i,15), xy_for_step_s(self.c, i, 10, 0, 10))
        #self.assertEqual((2,1), xy_for_step_s(self.c, 1, 10, 0, 10))
        #self.assertEqual((3,1), xy_for_step_s(self.c, 1, 10, 0, 10))
        
    def testLeft(self):
        for i in range(0, 11):
            self.assertEqual((15-i,15), xy_for_step_s(self.c, i, -10, 0, 10))

    def testUp(self):
        for i in range(0, 11):
            self.assertEqual((15,15+i), xy_for_step_s(self.c, i, 0, 10, 10))

    def testDown(self):
        for i in range(0, 11):
            self.assertEqual((15,15-i), xy_for_step_s(self.c, i, 0, -10, 10))

    def testDiag(self):
        #loc = []
        for i in range(0, 11):
            self.assertEqual((15+i,15+i), xy_for_step_s(self.c, i, 10, 10, 10))

    def testDiag2(self):
        loc = [ (15,15),(16,15),(17,15),(18,15),(19,16),(20,16),(21,16),(22,16) ]
        for i in range(0, 8):
            self.assertEqual((loc[i][0],loc[i][1]), 
                             xy_for_step_s(self.c, i, 14, 2, 14))


#             T   B
#   R g g g g g g g
#


# return the number of steps needed (minimum) when the snowball hits the snowman on
# the maximum step of all the steps taken.
def return_steps_max_needed(snowman_head_height, start_height, min_steps):
#snowman_head_height = 6
#start_height = 9
    for i in range(min_steps, MAX_DIST+1):
        for j in range(i, 0, -1):  # step number 
                                 # even though highly unlikely to hit in first or last step..
            if (start_height - int(round(float(9 * j)/float(i))) == snowman_head_height and
                j >= min_steps):
                print "at that height on step", j
                # gotcha!
                return i
    return 0

def return_max_steps_max_needed(snowman_head_height, start_height, min_steps):
#snowman_head_height = 6
#start_height = 9
    for i in range(MAX_DIST, min_steps-1, -1):
        for j in range(i, 0, -1):  # step number 
                                 # even though highly unlikely to hit in first or last step..
            if (start_height - int(round(float(9 * j)/float(i))) == snowman_head_height and
                j >= min_steps):
                print "at that height on step", j
                # gotcha!
                return i
    return 0

def show_x_y_height(sx, sy, dx, dy, start_height):
    steps = max(dx, dy)
    for s in range(1,steps+1):
        # calculate height
        height_at_step_s = start_height - int(round(float(9 * s)/float(steps)))
        # calculate position it will be at...
        atx = sx + int(round( float( s * ( dx ) )/float(steps) ))
        aty = sy + int(round( float( s * ( dy ) )/float(steps) ))
        print "height:",height_at_step_s," x:",atx," y:",aty 




class TestCrawling(unittest.TestCase):
    def setUp(self):
        init_ground()
        self.c = Child()
        self.c.pos.x = 15
        self.c.pos.y = 15

    def make_p(self, sx, sy):
        return Point(self.c.pos.x + ((sx - self.c.pos.x)/2),
                     self.c.pos.y + ((sy - self.c.pos.y)/2))   

    def testUR(self):
        p = self.make_p(15+1, 15+2)
        self.assertEqual(Point(15,16), p)
    def testU(self):
        p = self.make_p(15, 15+2)
        self.assertEqual(Point(15,16), p)
    def testUL(self):
        p = self.make_p(15-1, 15+2)
        self.assertEqual(Point(15,16), p)

    def testRU(self):
        p = self.make_p(15+2, 15+1)
        self.assertEqual(Point(16,15), p)
    def testR(self):
        p = self.make_p(15+2, 15)
        self.assertEqual(Point(16,15), p)
    def testRD(self):
        p = self.make_p(15+2, 15-1)
        self.assertEqual(Point(16,15), p)
        
    def testDR(self):
        p = self.make_p(15+1, 15-2)
        self.assertEqual(Point(15,14), p)
    def testD(self):
        p = self.make_p(15, 15-2)
        self.assertEqual(Point(15,14), p)
    def testDL(self):
        p = self.make_p(15-1, 15-2)
        self.assertEqual(Point(15,14), p)
        
    def testLD(self):
        p = self.make_p(15-2, 15-1)
        self.assertEqual(Point(14,15), p)
    def testL(self):
        p = self.make_p(15-2, 15)
        self.assertEqual(Point(14,15), p)
    def testLU(self):
        p = self.make_p(15-2, 15+1)
        self.assertEqual(Point(14,15), p)
        

class TestSnow(unittest.TestCase):
    def setUp(self):
        init_ground()
        self.c = Child()
        self.c.pos.x = 1
        self.c.pos.y = 1

    def testCantFindAny(self):
        result = look_for_small_snowball(self.c)
        self.assertEqual((-1,-1), result)

    def testCanFindOne(self):
        ground[2][2] = GROUND_S
        result = look_for_small_snowball(self.c)
        self.assertEqual((2,2), result)

    def testUpperRightPreferred(self):
        ground[2][2] = GROUND_S
        ground[1][2] = GROUND_S
        ground[2][1] = GROUND_S
        result = look_for_small_snowball(self.c)
        self.assertEqual((2,2), result)


if __name__ == '__main__':
    unittest.main()
