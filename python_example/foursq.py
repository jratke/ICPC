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
GROUND_CHILD_RED = 10
GROUND_CHILD_BLUE = 11

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

TARGETS = [ [(7,22),(9,19)],[(22,22),(20,19)],[(7,7),(9,10)],[(22,7),(20,10)] ]

# Simple representation for a child in the game.
class Child:
    def __init__( self, i ):
        # Location of the child.
        self.pos = Point( 0, 0 )

       # True if  the child is standing.
        self.standing = 1
    
        # What's the child holding.
        self.holding = HOLD_EMPTY
    
        # How many more turns this child is dazed.
        self.dazed = 0

        self.index = i

class RedChild(Child):
    def __init__(self, i):
        Child.__init__(self, i)
        self.color = RED

        # Last location child attempted to pickup snow.
        self.last_action = "idle"
        self.last_dest = Point( -1, -1 )

        # The child index of the last child that we tried to
        # throw a snowball at...
        self.last_victim = 0

        # which run target...
        self.reached_target = False
        self.target_index = 0
        self.target = Point(0, 0)
        self.set_target(i)

    def set_target(self, i):
        if i < 4:
            self.target.set(TARGETS[i][self.target_index][0], 
                            TARGETS[i][self.target_index][1])
            
    def switch_target(self):
        self.target_index = (self.target_index + 1) % 2
        self.set_target(self.index)

class BlueChild(Child):
    def __init__(self, i):
        Child.__init__(self, i)
        self.color = BLUE
        # If pos of opponent is unknown, perhaps the last know pos
        # might be helpful.
        self.last_known = Point(0, 0)


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
        ground[px][py] != GROUND_CHILD_RED and
        ground[px][py] != GROUND_CHILD_BLUE and
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
                vics.append((dx,dy,dsq,cList[j].holding,cList[j].dazed,cList[j].standing,j))
        j += 1
    return vics

# if the victims are dazed, we should aim for the one that is the least dazed.
# aim for closest, as we are likely to hit it.
# if a victim is holding a medium or large snowball target them to disrupt them 
#  .. also likely to be standing still.

# snowball 0(none) 1(small) 2(med)
# dazed 0 .. 4
# dsq (distance) ....

def choose_victim(vics):
    vics.sort(lambda x,y:cmp(x[2],y[2])) # dsq 
    vics.sort(lambda x,y:cmp(x[4],y[4])) # dazed
    vics.sort(lambda x,y:cmp(x[3],y[3]), reverse=True)  # holding.  
    return vics[0]

def target_victim(c, vic, m):
    global ground
    global height
    steps = max(abs(vic[0] * 2), abs(vic[1] * 2))
    if c.standing:
        start_height = 9
    else:
        start_height = 6

    if vic[5]:
        vic_height = 9
    else:
        vic_height = 6

    take_the_shot = False
    # for each step 1 to steps
    for s in range(1,steps+1):
        # calculate height
        height_at_step_s = start_height - int(round((9 * s)/steps))
        # calculate position it will be at...
        atx = c.pos.x + int(round( ( s * ( vic[0] ) )/steps ))
        aty = c.pos.y + int(round( ( s * ( vic[1] ) )/steps ))

        # if anything we don't want to hit at this point
        # including the ground, abort!
        if (ground[atx][aty] == GROUND_TREE or
            (height[atx][aty] >= 0 and    # we know the height  and...
             (height_at_step_s < height[atx][aty]))): # or
             # (height_at_step_s == height[atx][aty] and
             #  ground[atx][aty] != GROUND_SMB)))):
            break

        # if something we do want to hit.  Take the shot!!!
        if ground[atx][aty] == GROUND_CHILD_BLUE:  # TODO: and they are not ducking...
            take_the_shot = True
            break

        # a blue snow man is ok, only if we are going to hit it in the head
        # a red snowman is ok, only if we throw over it..

        # if we went through all that, and we didn't hit anything, 
        # (maybe it would pass over the target) 
        # then don't take the shot either.

    if take_the_shot:
        m.action = "throw"
        # throw past the victim, so we will probably hit them
        # before the snowball falls into the snow.
        m.dest = Point( c.pos.x + vic[0] * 2,
                        c.pos.y + vic[1] * 2 )

    # TODO: but if something's in the way, like a tree, 
    # or a snowman that we can't throw over
    # or your own guy (although your own guy could move in this turn?), 
    # then it doesnt make sense to throw, because it will just be
    # blocked, or you will hit your own guy

def moveToAverage(c, cList, m):
    # come up with a list of known team members of the opposite team.
    locations = []
    for i in range( CCOUNT, CCOUNT * 2 ):
        if cList[i].pos.x >= 0:
            # we know where he is.
            locations.append( (cList[i].pos.x, cList[i].pos.y) )
    # now get the average 
    if len(locations) > 0:
        # figure out the average
        xsum = 0
        ysum = 0
        for j in locations:
            xsum += j[0]
            ysum += j[1]
        xav = int(round(xsum / len(locations)))
        yav = int(round(ysum / len(locations)))
        # move toward it
        moveToward(c, Point(xav, yav), m)
    else:
        # random move.
        valid_random_movement(c, m)

def snowball_matcher(ox, oy):
    return (ground[ ox ][ oy ] == GROUND_S or
            ground[ ox ][ oy ] == GROUND_MS or
            ground[ ox ][ oy ] == GROUND_LS or
            ground[ ox ][ oy ] == GROUND_SMB)  # because we can take the top off.

def snow_matcher(ox, oy):
    return (ground[ ox ][ oy ] == GROUND_EMPTY and 
            height[ ox ][ oy ] > 0)

def almost_snowman(ox, oy):
    return (ground[ ox ][ oy ] == GROUND_LM)

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

def stand_and_throw(c, m):
    # Stand up if the child is armed.
    if not c.standing:
        m.action = "stand"
    else:
        # find potential victims.
        vics = victims_in_range(c, cList)
        if len(vics) > 0:
            # choose the best one.
            # throw at that one.
            target_victim(c, choose_victim(vics), m)

# TODO:
# function: can I get next to it in one run?


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

for i in range( 2 * CCOUNT ):
    if i < CCOUNT:
        c = RedChild(i)
    else:
        c = BlueChild(i)
    cList.append( c )

turnNum = string.atoi( sys.stdin.readline() )
while turnNum >= 0:
    # read the scores of the two sides.
    tokens = string.split( sys.stdin.readline() )
    score[ RED ] = tokens[ 0 ]
    score[ BLUE ] = tokens[ 1 ]
    
    # Parse the current map.
    for i in range( SIZE ):
        tokens = string.split( sys.stdin.readline() )
        for j in range( SIZE ):
            # Can we see this cell?
            if tokens[ j ][ 0 ] == '*':
                height[ i ][ j ] = -1
                ground[ i ][ j ] = -1
            else:
                height[ i ][ j ] = string.find( string.digits, tokens[ j ][ 0 ] )
                ground[ i ][ j ] = string.find( string.ascii_lowercase, tokens[ j ][ 1 ] )
                
    # Read the states of all the children.
    for i in range( CCOUNT * 2 ):
        c = cList[ i ]
        
        # Can we see this child?        
        tokens = string.split( sys.stdin.readline() )
        if tokens[ 0 ] == "*":
            c.pos.x = -1
            c.pos.y = -1
        else:
            # Record the child's location.
            c.pos.x = string.atoi( tokens[ 0 ] )
            c.pos.y = string.atoi( tokens[ 1 ] )
            if i >= CCOUNT:
                c.last_known.set(c.pos.x, c.pos.y)

            # Read the stance, what the child is holding and how much
            # longer he's dazed.
            c.standing = ( tokens[ 2 ] == "S" )
            
            c.holding = string.find( string.ascii_lowercase, tokens[ 3 ] )

            c.dazed = string.atoi( tokens[ 4 ] )

    # Mark all the children in the map, so they are easy to
    # look up.
    for i in range( 2 * CCOUNT ):
        c = cList[ i ]
        if c.pos.x >= 0:
            if i < CCOUNT:
                ground[ c.pos.x ][ c.pos.y ] = GROUND_CHILD_RED
            else:
                ground[ c.pos.x ][ c.pos.y ] = GROUND_CHILD_BLUE

    # Decide what each child should do
    for i in range( CCOUNT ):
        c = cList[ i ]
        m = Move()

        # If we somehow (bug?) hold a medium or large snowball, drop it!
        if (c.holding == HOLD_M or c.holding == HOLD_L or
            c.holding == HOLD_P2 or c.holding == HOLD_P3):
            m.action = "drop"
            m.dest = Point(c.pos.x + 1, c.pos.y)

        # Try to acquire a snowball if we need one.
        elif (c.holding != HOLD_S1 and c.holding != HOLD_S2 and c.holding != HOLD_S3):
            # Crush into a snowball, if we have snow.
            if c.holding == HOLD_P1:
                m.action = "crush"
            else:
                sx, sy = look_for_small_snowball(c)

                if sx == -1:
                    sx, sy = look_for_snow(c)

                # If there is a small snowball or snow, try to get it.
                if sx >= 0:
                    if c.standing:
                        m.action = "crouch"
                    else:
                        m.action = "pickup"
                        m.dest = Point( sx, sy )

                        # But, if a previous child is going to pick up 
                        # from the same spot, then move randomly instead.
                        if i > 0:
                            for prev_c_index in range(0, i):
                                if (cList[prev_c_index].last_action == "pickup" and
                                    cList[prev_c_index].last_dest == m.dest):
                                   valid_random_movement(c,m)
                else:
                    # move randomly to try to find some small snowballs or snow
                    valid_random_movement(c,m)
        else:
            # Child is holding one (or more!) small snow ball.

            # If next to any space containing a medium on a large,
            # finish the snowman for our team!
            sx, sy = look_for(c, almost_snowman)
            if sx >= 0:
                m.action = "drop"
                m.dest = Point(sx,sy)
            else:
                # Stand up if the child is armed.
                if not c.standing:
                    m.action = "stand"
                else:
                    # find potential victims.
                    vics = victims_in_range(c, cList)
                    if len(vics) > 0:
                        # choose the best one.
                        vic = choose_victim(vics)
                        # set action to throw and set the dest.
                        target_victim(c, vic, m)
                        c.last_victim = vic[6]
                    else:
                        # TODO: Look for any almost complete snowmen near by that
                        # we can run to in one step and complete?

                        # are we at our target?
                        if c.reached_target == True:
                            # now go free range...
                            if c.last_victim > 0:
                                # do we know where he is now?
                                if cList[c.last_victim].pos.x >= 0:
                                    # move towards him
                                    moveToward(c, Point(cList[c.last_victim].pos.x,
                                                        cList[c.last_victim].pos.y), m)
                                else:
                                    if cList[c.last_victim].last_known.x >= 0:
                                        moveToward(c, 
                                                   Point(cList[c.last_victim].last_known.x,
                                                         cList[c.last_victim].last_known.y), m)
                                    else:
                                        moveToAverage(c, cList, m)
                            else:
                                moveToAverage(c, cList, m)
                        else:
                            if c.pos == c.target:
                                c.reached_target = True

                # If nothing else to do, try to move somewhere
                if m.action == "idle":
                    if c.dazed == 0:
                        moveToward( c, c.target, m )

        # TODO: avoid a attempt to move into the same space as well.

        c.last_action = m.action

        # Write out the child's move
        if m.dest == None:
            sys.stdout.write( "%s\n" % m.action )
            c.last_dest.set(-1,-1)
        else:
            sys.stdout.write( "%s %d %d\n" % ( m.action, m.dest.x, m.dest.y ) )
            c.last_dest.set(m.dest.x, m.dest.y)

    sys.stdout.flush()
    turnNum = string.atoi( sys.stdin.readline() )
