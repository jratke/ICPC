#
# Icy Projectile Challenge
# Player code by John Ratke
# Based on hunter.py example program
# 
# To run, use:
#  java -jar icypc.jar -player pipe 2 python python_example/player.py \
#                      -player java -cp java_example Planter -map maps/map5.txt

import random
import sys
import string

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

TARGETS = [ [(7,22)],[(22,22)],[(7,6),(22,7),(22,22),(7,22)],[(22,7)] ]

BUILD_STAGE_BASE = 0
BUILD_STAGE_MIDDLE = 1
BUILD_STAGE_TOP = 2

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

        self.last_action = "idle"
        # Last location child attempted to pickup snow from, drop to or move to.
        self.last_dest = Point( -1, -1 )

        self.last_pos = Point(-1, -1)

        # The child index of the last child that we tried to
        # throw a snowball at...
        self.last_victim = 0

        # which run target...
        self.reached_target = False
        self.target = Point(0, 0)
        self.target_index = 0
        self.set_target()
        self.completed_circuit = False
        self.got_four_targets = False

        # if building a snowman
        self.build_stage = BUILD_STAGE_BASE

        self.mode = 0   # get a snowball and get to target looking for victims
        if i == 2:
            self.mode = 1 # get to target, build a snowman.

    def set_target(self):
        self.target.set(TARGETS[self.index][self.target_index][0], 
                        TARGETS[self.index][self.target_index][1])

    def next_target(self):
        self.target_index = (self.target_index + 1) % len(TARGETS[self.index])
        self.set_target()
        self.reached_target = False

class BlueChild(Child):
    def __init__(self, i):
        Child.__init__(self, i)
        self.color = BLUE
        # If pos of opponent is unknown, perhaps the last know pos
        # might be helpful.
        self.last_known = Point(-1, -1)

        # The index of the child on the Red team, if any, that is
        # targeting this child for a throw in this turn.
        self.targeted_by = -1


# Simple representation for a child's action
class Move:
    # Action the child is making.
    action = "idle"

    # Destiantion of this action (or null, if it doesn't need one)
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


def run_diagonal(c, target, m):
    # Run diagonally.
    m.action = "run"
    px = c.pos.x + clamp( target.x - c.pos.x, -1, 1 )
    py = c.pos.y + clamp( target.y - c.pos.y, -1, 1 )

    if can_move(px, py):
        m.dest = Point(px,py)
    else:
        # just try up or down only
        if can_move(c.pos.x, py):
            m.dest = Point(c.pos.x,py)
        elif can_move(c.pos.x+1, c.pos.y):  # try right...
            m.dest = Point(c.pos.x+1, c.pos.y)
        elif can_move(c.pos.x-1, c.pos.y):  # try left...
            m.dest = Point(c.pos.x-1, c.pos.y)
        else:
            m.action = "idle"
            m.dest = None

def run_horizontal(c, target, m):
    # Run left or right
    m.action = "run"
    dx = clamp( target.x - c.pos.x, -2, 2 )
    if dx > 0:
        if not can_move(c.pos.x + 1, c.pos.y):
            if can_move(c.pos.x + 1, c.pos.y+1):
                m.dest = Point(c.pos.x + 1, c.pos.y+1)
            elif can_move(c.pos.x + 1, c.pos.y-1):
                m.dest = Point(c.pos.x + 1, c.pos.y-1)
            elif target.y >= c.pos.y and can_move(c.pos.x, c.pos.y+1):
                m.dest = Point(c.pos.x, c.pos.y+1)
            elif target.y <= c.pos.y and can_move(c.pos.x, c.pos.y-1):
                m.dest = Point(c.pos.x, c.pos.y-1)
            else:
                m.action = "idle"
                m.dest = None
                return
        else:
            # want to move two and can move two as well?
            if dx > 1 and can_move(c.pos.x + 2, c.pos.y):
                # good, do it...
                m.dest = Point(c.pos.x + 2, c.pos.y)
            else:
                # just one will have to do
                m.dest = Point(c.pos.x + 1, c.pos.y)
    elif dx < 0:
        if not can_move(c.pos.x - 1, c.pos.y):
            # can't do it.  
            # we're already at target y, but try to move diagonally
            if can_move(c.pos.x - 1, c.pos.y+1):
                m.dest = Point(c.pos.x - 1, c.pos.y+1)
            elif can_move(c.pos.x - 1, c.pos.y-1):
                m.dest = Point(c.pos.x - 1, c.pos.y-1)
            # else have to go off course for a bit.
            elif target.y >= c.pos.y and can_move(c.pos.x, c.pos.y+1):
                m.dest = Point(c.pos.x, c.pos.y+1)
            elif target.y <= c.pos.y and can_move(c.pos.x, c.pos.y-1):
                m.dest = Point(c.pos.x, c.pos.y-1)
            else:
                m.action = "idle"
                m.dest = None
                return
        else:
            # want to move left two and can move two as well?
            if dx < 1 and can_move(c.pos.x - 2, c.pos.y):
                # good, do it...
                m.dest = Point(c.pos.x - 2, c.pos.y)
            else:
                # just one will have to do
                m.dest = Point(c.pos.x - 1, c.pos.y)

def run_vertical(c, target, m):
    # Run up or down.
    m.action = "run"
    dy = clamp( target.y - c.pos.y, -2, 2 )
    if dy > 0:
        if not can_move(c.pos.x, c.pos.y+1):
            # can't do it.  
            # we're already at target x, but try to move diagonal
            if can_move(c.pos.x+1, c.pos.y+1):
                m.dest = Point(c.pos.x+1, c.pos.y+1)
            elif can_move(c.pos.x-1, c.pos.y+1):
                m.dest = Point(c.pos.x-1, c.pos.y+1)
            elif target.x >= c.pos.x and can_move(c.pos.x+1, c.pos.y):
                m.dest = Point(c.pos.x+1, c.pos.y)
            elif target.x <= c.pos.x and can_move(c.pos.x-1, c.pos.y):
                m.dest = Point(c.pos.x-1, c.pos.y)
            else:
                m.action = "idle"
                m.dest = None
                return
        else:
            # want to move two and can move two as well?
            if dy > 1 and can_move(c.pos.x, c.pos.y+2):
                # good, do it...
                m.dest = Point(c.pos.x, c.pos.y+2)
            else:
                # just one
                m.dest = Point(c.pos.x, c.pos.y+1)
    elif dy < 0:
        if not can_move(c.pos.x, c.pos.y-1):
            # can't do it.  
            # we're already at target x, but try to move diagonal
            if can_move(c.pos.x+1, c.pos.y-1):
                m.dest = Point(c.pos.x+1, c.pos.y-1)
            elif can_move(c.pos.x-1, c.pos.y-1):
                m.dest = Point(c.pos.x-1, c.pos.y-1)
            elif target.x >= c.pos.x and can_move(c.pos.x+1, c.pos.y):
                m.dest = Point(c.pos.x+1, c.pos.y)
            elif target.x <= c.pos.x and can_move(c.pos.x-1, c.pos.y):
                m.dest = Point(c.pos.x-1, c.pos.y)
            else:
                m.action = "idle"
                m.dest = None
                return
        else:
            # want to move two and can move two as well?
            if dy < 1 and can_move(c.pos.x, c.pos.y-2):
                # good, do it...
                m.dest = Point(c.pos.x, c.pos.y-2)
            else:
                # just one will have to do
                m.dest = Point(c.pos.x, c.pos.y-1)


# Fill in move m to move the child c twoard the given target location, either
# crawling or running.
def moveToward( c, target, m ):

    dx = target.x - c.pos.x
    dy = target.y - c.pos.y

    if c.standing:
        # Run to the destination
        if c.pos.x != target.x:
            if c.pos.y != target.y:
                if dx*dx > dy*dy:
                    run_horizontal(c, target, m)
                else:
                    run_diagonal(c, target, m)
            else:
                run_horizontal(c, target, m)
        elif c.pos.y != target.y:
            run_vertical(c, target, m)
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

#def find_child_at(x1,y1,cList):
#    i = 0
#    while i < CCOUNT * 2:
#        if cList[i].pos.x == x1 and cList[i].pos.y == y1:
#            return i
#    return -1

def random_movement(c):
    if c.standing:
        options = [(-2,0),(-1,0,),(-1,-1),(0,2),(0,1),(1,1),(1,0),(2,0),(1,-1),(0,-1),(0,-2),(-1,-1)]
        return options[int(round(rnd.uniform(0,11)))]
    else:
        options = [(-1,0),(0,1),(1,0),(0,-1)]
        return options[int(round(rnd.uniform(0,3)))]

# is location px, py valid (on the board)
# and available to move to?
# NOTE: This assumes we can actually see it...
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
        ground[px][py] != GROUND_SMR and     # these two probably redundant
        ground[px][py] != GROUND_SMB and
        ground[px][py] != GROUND_LM):      # don't smash a potential snowman!
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
        # TODO:  Didn't check if we can run through middle space!
        m.dest = Point(c.pos.x + p[0], c.pos.y + p[1])
    else:
        m.action = "crawl"
        m.dest = Point(c.pos.x + p[0], c.pos.y + p[1])


# come up with a list of potential victims... 
#  criteria is just "in range" and we will find out if we can hit them later.
def victims_in_range(c, cList):
    vics = []

    j = CCOUNT
    while j < CCOUNT * 2:
        if cList[ j ].pos.x >= 0:
            # We know where this child is, see if it's not too far away.
            dx = cList[ j ].pos.x - c.pos.x
            dy = cList[ j ].pos.y - c.pos.y
            dsq = dx * dx + dy * dy

            if dsq <= 12 * 12:
                vics.append((dx,dy,dsq,cList[j].holding,cList[j].dazed,cList[j].standing,j))
        j += 1
    return vics

def what_to_do(c, cList, vics, m):

    vics.sort(lambda x,y:cmp(x[2],y[2])) # dsq 

    if c.holding == HOLD_S3:
        target_best(c, cList, vics, m)
    else:
        # Not holding three snowballs, so we could catch
        threats = 0
        threat = -1
        for v in vics:
            if (v[5] and    # standing
                v[4] == 0 and # not dazed
                (v[3] == HOLD_S1 or v[3] == HOLD_S2 or v[3] == HOLD_S3) and
                v[2] <= 8*8):
                threat = v[6]  # index
                threats += 1

        if threats == 0:
            target_best(c, cList, vics, m)
        elif threats == 1:
            m.action = "catch"
            m.dest = Point( cList[threat].pos.x,
                            cList[threat].pos.y)
        else:
            # two or more threats... hmm.. fight or flee! Could crouch or run.
            target_best(c, cList, vics, m)
            # if I can't hit them, perhaps they can't hit me...

def throw_at_victim(c, cList, v, m):
    m.action = "throw"
    # throw past the victim, so we will probably hit them
    # before the snowball falls into the snow.
    m.dest = Point( c.pos.x + v[0] * 2,
                    c.pos.y + v[1] * 2 )
    
    # now this guy is targeting that one.
    c.last_victim = v[6]
    cList[v[6]].targeted_by = c.index


def target_best(c, cList, vics, m):
    vics.sort(lambda x,y:cmp(x[4],y[4])) # dazed
    
    # "Can Hit" array.
    # -1 = not in contention. 0 = in contention but haven't checked if this child, c, can hit yet.. 
    # 1 = in contention, can hit,  2 = in contention, can't hit
    ch = [-1,-1,-1,-1,-1,-1,-1,-1] 
    targeting = 0

    for v in vics:
        ch[v[6]] = 0
        # if they are not already targeted.
        if cList[v[6]].targeted_by == -1:

            if can_hit(c, cList, v):
                
                ch[v[6]] = 1
    
                # if dazed two or less, target this one...
                if v[4] <= 2:
                    targeting = v[6]
                    throw_at_victim(c, cList, v, m)
                    break
            else:
                ch[v[6]] = 2

    if targeting == 0:
        # check if we can hit ones we didn't check yet.
        for v in vics:

            if ch[v[6]] == 1:  # already checked, and can hit them...
                throw_at_victim(c, cList, v, m)
                break
            elif ch[v[6]] == 0:  # haven't checked yet
                if can_hit(c, cList, v):
                    throw_at_victim(c, cList, v, m)
                    break
            # else, 2, checked and can't hit.

def can_hit(c, cList, vic):
    global ground
    global height
    global child_at
    steps = max(abs(vic[0] * 2), abs(vic[1] * 2))
    if c.standing:  start_height = 9
    else: start_height = 6

    if vic[5]: vic_height = 9
    else: vic_height = 6

    good_shot = False

    # for each step 1 to steps
    for s in range(1,steps+1):
        # calculate height
        height_at_step_s = start_height - int(round(float(9 * s)/float(steps)))
        # calculate position it will be at...
        atx = c.pos.x + int(round( float( s * ( vic[0] * 2 ) )/float(steps) ))
        aty = c.pos.y + int(round( float( s * ( vic[1] * 2 ) )/float(steps) ))

        if ground[atx][aty] == GROUND_TREE:
            break

        if ground[atx][aty] == GROUND_CHILD_RED:
            cindex = child_at[(atx, aty)]
            if cList[cindex].standing:
                break
            else:
                # height = 6, they might stand up in this turn, so don't risk throwing
                if cList[cindex].holding == HOLD_S1 or cList[cindex].holding == HOLD_S2 or cList[cindex].holding == HOLD_S3:
                    break
                if height[atx][aty] <= 6:
                    break

        if ground[atx][aty] == GROUND_CHILD_BLUE:
            # perhaps it is the one we are targeting, vic[6], but perhaps not.
            cindex = child_at[(atx, aty)]

            child_height = 6
            if cList[cindex].standing:
                child_height = 9

            if height_at_step_s <= child_height:
                good_shot = True
                break

        # if anything we don't want to hit at this point
        # including the ground, abort!
        if ((height[atx][aty] >= 0 and    # we know the height  and...
             (height_at_step_s < height[atx][aty]  or
              (height_at_step_s == height[atx][aty] and
               ground[atx][aty] != GROUND_SMB)))):
            break

    if good_shot:
        return True
    else:
        return False


def find_average_and_move(c, locations, m):
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

def moveToAverage(c, cList, m):
    # come up with a list of known team members of the opposite team.
    locations = []
    for i in range( CCOUNT, CCOUNT * 2 ):
        if cList[i].pos.x >= 0:
            # we know where he is.
            locations.append( (cList[i].pos.x, cList[i].pos.y) )
    # now get the average 
    if len(locations) > 0:
        find_average_and_move(c, locations, m)
    else:
        # we don't know where anyone is for sure, what about last-knowns?
        for i in range( CCOUNT, CCOUNT * 2 ):
            if cList[i].last_known.x >= 0:
                # we know where he was!
                locations.append( (cList[i].last_known.x, cList[i].last_known.y) )
        if len(locations) > 0:
            find_average_and_move(c, locations, m)
        else:
            # random move.
            #valid_random_movement(c, m)
            moveToward(c, Point(15,15), m)

def snowball_matcher(ox, oy):
    return (ground[ ox ][ oy ] == GROUND_S or
            ground[ ox ][ oy ] == GROUND_MS or
            ground[ ox ][ oy ] == GROUND_LS or
            ground[ ox ][ oy ] == GROUND_SMB)  # because we can take the top off.

def medium_snowball_matcher(ox,oy):
    return ground[ox][oy] == GROUND_M

def snowman_base_matcher(ox,oy):
    return (ground[ox][oy] == GROUND_L and
            height[ox][oy] < 7)

def powdered_snow_matcher(ox, oy):
    return (ground[ ox ][ oy ] == GROUND_EMPTY and 
            height[ ox ][ oy ] > 0)

def almost_snowman(ox, oy):
    return (ground[ ox ][ oy ] == GROUND_LM and
            height[ ox ][ oy ] < 9)

def blue_snowman(ox, oy):
    return (ground[ ox ][ oy ] == GROUND_SMB)

def can_drop_small(ox, oy):
    return (ground[ox][oy] == GROUND_EMPTY and
            height[ox][oy] < 9)

def can_drop_medium(ox, oy):
    return (ground[ox][oy] == GROUND_EMPTY and
            height[ox][oy] < 8)

def can_start_snowman(ox,oy):
    return (ground[ox][oy] == GROUND_EMPTY and
            height[ox][oy] < 4)

def safe_drop_medium(ox,oy):
    return (ground[ox][oy] == GROUND_EMPTY and
            height[ox][oy] < 7)

def look_for(c, matcher):
    for oy in range( c.pos.y + 1, c.pos.y - 2, -1 ):
        for ox in range( c.pos.x + 1, c.pos.x - 2, -1 ):
            if ( ox >= 0 and ox < SIZE and
                 oy >= 0 and oy < SIZE and
                 ( ox != c.pos.x or oy != c.pos.y ) and
                 matcher(ox, oy) == True):
                return (ox, oy)
    return (-1, -1)

def look_for_small_snowball(c):
    return look_for(c, snowball_matcher)

def look_for_powdered_snow(c):
    return look_for(c, powdered_snow_matcher)


def check_list_of_positions(c, l, matcher):
    for (ox, oy) in l:
        if ( c.pos.x + ox >= 0 and c.pos.x + ox < SIZE and
             c.pos.y + oy >= 0 and c.pos.y + oy < SIZE and
             matcher(c.pos.x + ox, c.pos.y + oy) == True):
            return (c.pos.x + ox, c.pos.y + oy)
    return (-1, -1)
    

# function: can I get next to it in one crawl?
# if child at P, N are the locations child can crawl to,
# so C are the (new) locations that the child can pickup or drop from.
#
#     C C C
#   C   N   C
#   C N P N C
#   C   N   C
#     C C C
#
def can_crawl_to(c, matcher):
    if can_move(c.pos.x, c.pos.y+1):
        # pass c to get current position... because list is relative.
        px, py = check_list_of_positions(c, [(-1,2),(0,2),(1,2)], matcher)
        if px >= 0:
            return (px, py)
    
    if can_move(c.pos.x+1, c.pos.y):
        px, py = check_list_of_positions(c, [(2,1),(2,0),(2,-1)], matcher)
        if px >= 0:
            return (px, py)

    if can_move(c.pos.x, c.pos.y-1):
        px, py = check_list_of_positions(c, [(1,-2),(0,-2),(-1,-2)], matcher)
        if px >= 0:
            return (px, py)

    if can_move(c.pos.x-1, c.pos.y):
        px, py = check_list_of_positions(c, [(-2,-1),(-2,0),(-2,1)], matcher)
        if px >= 0:
            return (px, py)

    return (-1, -1)
        
# can_run_to(c, matcher)
# depending on which spot, N, you can run to, check certain spots, C, for 
# whatever we are trying to match.
#     C C C
#   C C N C C
# C C N N N C C
# C N N P N N C
# C C N N N C C
#   C C N C C
#     C C C
#

def can_run_to(c, matcher):
    if can_move(c.pos.x+1,c.pos.y+1):
        px, py = check_list_of_positions(c, [(0,2),(1,2),(2,2),(2,1),(2,0)], matcher)
        if px >= 0:
            return (px, py)

    if can_move(c.pos.x+1,c.pos.y-1):
        px, py = check_list_of_positions(c, [(2,0),(2,-1),(2,-2),(1,-2),(0,-2)], matcher)
        if px >= 0:
            return (px, py)

    if can_move(c.pos.x-1,c.pos.y-1):
        px, py = check_list_of_positions(c, [(0,-2),(-1,-2),(-2,-2),(-2,-1),(-2,0)], matcher)
        if px >= 0:
            return (px, py)

    if can_move(c.pos.x-1,c.pos.y+1):
        px, py = check_list_of_positions(c, [(-2,0),(-2,1),(-2,2),(-1,2),(0,2)], matcher)
        if px >= 0:
            return (px, py)

    if (can_move(c.pos.x,c.pos.y+1) and
        can_move(c.pos.x,c.pos.y+2)):
        px, py = check_list_of_positions(c, [(-1,2),(-1,3),(0,3),(1,3),(1,2)], matcher)
        if px >= 0:
            return (px, py)

    if (can_move(c.pos.x+1,c.pos.y) and
        can_move(c.pos.x+2,c.pos.y)):
        px, py = check_list_of_positions(c, [(2,1),(3,1),(3,0),(3,-1),(2,-1)], matcher)
        if px >= 0:
            return (px, py)

    if (can_move(c.pos.x,c.pos.y-1) and
        can_move(c.pos.x,c.pos.y-2)):
        px, py = check_list_of_positions(c, [(1,-2),(1,-3),(0,-3),(-1,-3),(-1,-2)], matcher)
        if px >= 0:
            return (px, py)

    if (can_move(c.pos.x-1,c.pos.y) and
        can_move(c.pos.x-2,c.pos.y)):
        px, py = check_list_of_positions(c, [(-2,-1),(-3,-1),(-3,0),(-3,1),(-2,1)], matcher)
        if px >= 0:
            return (px, py)

    return (-1, -1)

def figure_crawl_dest(c, sx, sy, m):
    dx = sx - c.pos.x
    dy = sy - c.pos.y
    if dx > 1:
        m.dest = Point(c.pos.x + 1, c.pos.y)
    elif dx < -1:
        m.dest = Point(c.pos.x - 1, c.pos.y)
    elif dy > 1:
        m.dest = Point(c.pos.x, c.pos.y + 1)
    else:
        m.dest = Point(c.pos.x, c.pos.y - 1)


def pickup_if_no_one_else_will(c, i, cList, sx, sy, m):
    m.action = "pickup"
    m.dest = Point( sx, sy )

    # But, if a previous child is going to pick up 
    # from the same spot, then move randomly instead.
    if i > 0:
        for prev_c_index in range(0, i):
            if (cList[prev_c_index].last_action == "pickup" and
                cList[prev_c_index].last_dest == m.dest):
                # shouldn't try to move into a space 
                # where somebody else is trying to pickup something,
                # but our move checking at the end should prevent that.
                valid_random_movement(c,m)

def someones_going_to_throw_at_me(c, cList):
    # find any threats!
    # return the threat!
    j = CCOUNT
    while j < CCOUNT * 2:
        if cList[ j ].pos.x >= 0:
            dx = cList[ j ].pos.x - c.pos.x
            dy = cList[ j ].pos.y - c.pos.y

            if (dx*dx+dy*dy <= 64 and
                cList[j].standing and
                cList[j].dazed == 0 and
                (cList[j].holding == HOLD_S1 or cList[j].holding == HOLD_S2 or cList[j].holding == HOLD_S3)):
                return (cList[j].pos.x, cList[j].pos.y)
        j += 1
    return (-1,-1)

def acquire_small_snowball(i, c, cList, m):
    # Crush into a snowball, if we have snow.
    if c.holding == HOLD_P1:
        m.action = "crush"
    else:
        if not c.standing:
            # First priority, I'm next to a blue snowman
            sx, sy = look_for(c, blue_snowman)
            if sy >= 0:
                pickup_if_no_one_else_will(c, i, cList, sx, sy, m)
            else:
                sx, sy = can_crawl_to(c, blue_snowman)
                if sx >= 0:
                    m.action = "crawl"
                    figure_crawl_dest(c, sx, sy, m)
                else:
                    # am I next to a med snowball, and next to a large base, 
                    # or can crawl to a large base?
                    sx,sy = look_for(c, medium_snowball_matcher)
                    sx2, sy2 = look_for(c, snowman_base_matcher)
                    sx3, sy3 = can_crawl_to(c, snowman_base_matcher)
                    if sx >= 0 and (sx2 >= 0 or sx3 >= 0):
                        # pick it up.
                        pickup_if_no_one_else_will(c, i, cList, sx, sy, m)
                    else:
                        sx, sy = can_crawl_to(c, snowball_matcher)
                        if sx >= 0:
                            m.action = "crawl"
                            figure_crawl_dest(c, sx, sy, m)
        else:
            # if now next to a blue snowman...
            sx,sy = look_for(c, blue_snowman)
            if sx >= 0:
                m.action = "crouch"
            else:
                sx, sy = can_run_to(c, blue_snowman)
                if sx >= 0:
                    moveToward(c, Point(sx,sy), m)

                else:
                    # the fastest way to get a snowball is to catch one 
                    # that someone is going to throw!
                    sx, sy = someones_going_to_throw_at_me(c, cList)
                    if sx >= 0:
                        m.action = "catch"
                        m.dest = Point(sx,sy)

        # if not going to crawl (or run) somewhere or pick up a snowball, of some sort...
        if m.action == "idle":
            sx, sy = look_for_small_snowball(c)

            if sx == -1:
                sx, sy = look_for_powdered_snow(c)

            # If there is a small snowball or snow, try to get it.
            if sx >= 0:
                if c.standing:
                    m.action = "crouch"
                else:
                    pickup_if_no_one_else_will(c, i, cList, sx, sy, m)
            else:
                # move randomly to try to find some small snowballs or snow
                valid_random_movement(c,m)


def finish_nearby_snowman_or_stand(c, m):
    # Child is holding one (or more!) small snow ball.

    # If next to any space containing a medium on a large,
    # finish the snowman for our team!
    sx, sy = look_for(c, almost_snowman)
    if sx >= 0:
        m.action = "drop"
        m.dest = Point(sx,sy)
    else:
        # TODO: If we can hit somebody without standing up, then try that!

        # Stand up if the child is armed.
        if not c.standing:

            # Is there a snowman within crawling range that I can 
            # finish for my team?
            sx, sy = can_crawl_to(c, almost_snowman)
            if sx >= 0:
                m.action = "crawl"
                figure_crawl_dest(c, sx, sy, m)
            else:
                m.action = "stand"

# Fill in move, m, with a _potential_ action and destination!
#
def snowman_or_move_action(c, smb_list, m):
    sx, sy = can_run_to(c, almost_snowman)
    if sx >= 0:
        moveToward(c, Point(sx,sy), m)
    else:
        # have we already reached our target at least once at some point?
        if c.reached_target == True:

            # am I within one of a blue snowman while holding a snowball?
            # have to drop it, temporarily, so I can convert that snowman.
            sx,sy = look_for(c, blue_snowman)
            if sx >= 0:
                sx,sy = look_for(c, can_drop_small)
                if sy >= 0:
                    m.action = "drop"
                    m.dest = Point(sx,sy)

            if m.action == "idle":
                snowmen = []
                for sm in smb_list:
                    dx = sm[0] - c.pos.x
                    dy = sm[1] - c.pos.y                    
                    snowmen.append((dx*dx+dy*dy, sm[0], sm[1]))

                if len(snowmen) > 1:
                    snowmen.sort(lambda x,y:cmp(x[0],y[0])) # sort by the distances 

                if len(snowmen) > 0:
                    moveToward(c, Point(snowmen[0][1], snowmen[0][2]), m)

def drop_medium_or_crawl(c, m):
    sx,sy = look_for(c, snowman_base_matcher)
    if sx >= 0:
        m.action = "drop"
        m.dest = Point(sx, sy)
    else:
        sx,sy = can_crawl_to(c, snowman_base_matcher)
        if sx >= 0:
            m.action = "crawl"
            figure_crawl_dest(c, sx, sy, m)
        else:
            # something went wrong with our plans, perhaps someone
            # walked through the large snowball base!
            sx,sy = look_for(c, safe_drop_medium)
            if sx >= 0:
                m.action = "drop"
                m.dest = Point(sx, sy)


def move_toward_last_victim_or_average(c, cList, m):
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


def target_or_alternate_move(c, i, cList, smb_list, m, possible_m):
    # possible_m is an alternate move 
    # that this child could take if there is no victim to target,
    # the victim(s) can't be hit, or the victim is already
    # targeted by another member of the team in this turn.
    snowman_or_move_action(c, smb_list, possible_m)

    # find potential victims.
    vics = victims_in_range(c, cList)
    if len(vics) > 0:
        what_to_do(c, cList, vics, m)
        # might be nothing...
        if m.action == "idle":
            m.action = possible_m.action
            m.dest = possible_m.dest


def alternate_or_move(c, cList, m, possible_m):
    if possible_m.action != "idle":
        m.action = possible_m.action
        m.dest = possible_m.dest
    else:
        if c.reached_target == True:
            move_toward_last_victim_or_average(c, cList, m)
        else:
            if c.pos == c.target:
                c.reached_target = True
                # TODO, do something better...  valid_random_movement(c, m)
                moveToward(c, Point(15,15), m)
            else:
                if c.dazed == 0:
                    moveToward( c, c.target, m )
                    if m.action == "idle":
                        # we must be pretty blocked, so give up..
                        c.reached_target = True

def determine_action_for_child(c, i, cList, smb_list, m):
    # If we picked up a medium snowball, assume we are crouched, and look for
    # a large one near by to drop this one on.
    if c.holding == HOLD_M:
        drop_medium_or_crawl(c, m)
    # Try to acquire a snowball if we need one.
    elif (c.holding != HOLD_S1 and c.holding != HOLD_S2 and c.holding != HOLD_S3):
        acquire_small_snowball(i, c, cList, m)
    else:
        finish_nearby_snowman_or_stand(c, m)
            
        possible_m = Move()

        if m.action == "idle":
            target_or_alternate_move(c, i, cList, smb_list, m, possible_m)

        if m.action == "idle":
            alternate_or_move(c, cList, m, possible_m)

def reached_target_now_what(c, smb_seen, m):
    c.reached_target = True

    # if third or fourth target, and no blue snowmen seen yet, plant ours.
    if (((c.target_index == 2 or c.target_index == 3) and smb_seen == 0) or
        not c.completed_circuit):
        m.action = "crouch"
        c.build_stage = BUILD_STAGE_BASE
    else:
        if c.target_index == 3 and smb_seen == 0:
            c.got_four_targets = True
        else:
            c.next_target()

def determine_special_action(c, cList, smb_list, m):
    if c.reached_target == True:
        # Go look for close blue snowman, or snowman base (large),
        # or go on programmed route around the field.

        if c.holding == HOLD_L:
            m.action = "drop"
            sx,sy = look_for(c, can_start_snowman)
            if sx >= 0:
                m.dest = Point(sx,sy)
            c.build_stage = BUILD_STAGE_MIDDLE
        elif c.holding == HOLD_M:
            m.action = "drop"
            sx,sy = look_for(c, snowman_base_matcher)
            if sx >= 0:
                m.dest = Point(sx,sy)
                c.build_stage = BUILD_STAGE_TOP
            else:
                # somebody walked through our large!
                # look for any safe place to drop it, and go back to BUILD_STAGE_BASE
                sx,sy = look_for(c, can_drop_medium)
                if sx >= 0:
                    m.dest = Point(sx,sy)
                c.build_stage = BUILD_STAGE_BASE

        elif c.holding == HOLD_S1:
            m.action = "drop"
            sx,sy = look_for(c, almost_snowman)
            if sx >= 0:
                m.dest = Point(sx,sy)
            else:
                # maybe someone else (teammate?) finished this snowman...
                # Todo, if it's blue, take it back!
                # Todo: any snowmen nearby I can crawl to, or run to?
                sx,sy = look_for(c, can_drop_small)
                if sx >= 0:
                    m.dest = Point(sx,sy)
            c.build_stage = 3
        else:
            if c.build_stage == BUILD_STAGE_BASE:
 
                if c.holding < HOLD_P3:
                    if c.standing:
                        m.action = "crouch"
                    else:
                        # find 3 powdered snow
                        sx, sy = look_for_powdered_snow(c)
                        if sx >= 0:
                            m.action = "pickup"
                            m.dest = Point( sx, sy )
                        else:
                            # TODO: crap.. go get some?
                            pass
                else:
                    m.action = "crush"
            elif c.build_stage == BUILD_STAGE_MIDDLE:

                # TODO, if I'm crouched next to a middle, pick it up instead of making one
                
                if c.holding < HOLD_P2:
                    # find 2 powdered snow
                    sx, sy = look_for_powdered_snow(c)
                    if sx >= 0:
                        m.action = "pickup"
                        m.dest = Point( sx, sy )
                    else:
                        # TODO: crap.. go get some?
                        pass
                else:
                    m.action = "crush"
            elif c.build_stage == BUILD_STAGE_TOP:

                if c.holding < HOLD_P1:
                    # find 1 powdered snow
                    sx, sy = look_for_powdered_snow(c)
                    if sx >= 0:
                        m.action = "pickup"
                        m.dest = Point( sx, sy )
                    else:
                        # TODO: crap.. go get some?
                        pass
                else:
                    m.action = "crush"
            elif c.build_stage == 3:
                # 
                m.action = "stand"

                if c.target_index == 1:   # How about after two snowmen?
                    # went around once.  Now primary mission should be snowmen!
                    c.completed_circuit = True

                if c.target_index == 3 and smb_seen == 0:
                    c.got_four_targets = True
                else:
                    c.next_target()

    else:
        if c.pos != c.target:

            sx,sy = look_for(c, blue_snowman)
            if sx >= 0:
                # take steps to convert it...
                if c.standing:
                    m.action = "crouch"
                else:
                    if c.holding == HOLD_EMPTY:
                        pickup_if_no_one_else_will(c, 2, cList, sx, sy, m)
                    else:
                        # might have powdered snow that I need to get rid of now...
                        # TODO: if I have a snow ball and there is a bad guy, throw it at him.
                        sx,sy = look_for(c, can_drop_small)
                        if sx >= 0:
                            m.action = "drop"
                            m.dest = Point(sx,sy)
            else:
                sx,sy = can_run_to(c, blue_snowman)
                if sx >= 0:
                    if not c.standing:
                        m.action = "stand"
                    else:
                        moveToward(c, Point(sx,sy), m)
                else:
                    sx,sy = look_for(c, almost_snowman)
                    if sx >= 0:
                        if c.holding == HOLD_S1 or c.holding == HOLD_S2 or c.holding == HOLD_S3:
                            if c.standing:
                                m.action = "crouch"
                            else:
                                m.action = "drop"
                                m.dest = Point(sx,sy)
                        else:
                            if c.standing:
                                m.action = "crouch"
                            else:
                                if c.holding == HOLD_P1:
                                    m.action = "crush"
                                else:
                                    # lookfor snow and pickup if no one else will?
                                    sx, sy = look_for_powdered_snow(c)
                                    if sx >= 0:
                                        pickup_if_no_one_else_will(c, 2, cList, sx, sy, m)
                                    else:
                                        moveToward( c, c.target, m )
                    else:
                        if not c.standing:
                            m.action = "stand"
                        else:
                            sx,sy = can_run_to(c, almost_snowman)
                            if sx >= 0:
                                moveToward(c, Point(sx,sy), m)
                            else:
                                if c.completed_circuit:
                                    # Now look for any blue snowmen or almost snowmen!
                                    snowmen = []
                                    for sm in smb_list:
                                        dx = sm[0] - c.pos.x
                                        dy = sm[1] - c.pos.y                    
                                        snowmen.append((dx*dx+dy*dy, sm[0], sm[1]))

                                    if len(snowmen) > 1:
                                        snowmen.sort(lambda x,y:cmp(x[0],y[0])) # sort by the distances 

                                    if len(snowmen) > 0:
                                        moveToward(c, Point(snowmen[0][1], snowmen[0][2]), m)
                                    else:
                                        if c.dazed == 0:
                                            moveToward( c, c.target, m )
                                else:
                                    if c.dazed == 0:
                                        
                                        # If I'm within one of the target and can't move to it anyway,
                                        #  then let's just say we reached it.
                                        dx = c.target.x - c.pos.x
                                        dy = c.target.y - c.pos.y
                                        if ((dx == 1 or dx == -1) and (dy == 1 or dy == -1) and
                                            not can_move(c.target.x, c.target.y)):
                                            reached_target_now_what(c, smb_seen, m)
                                        else:
                                            moveToward( c, c.target, m )
        else:
            reached_target_now_what(c, smb_seen, m)

########################################################################################

# Source of randomness
rnd = random.Random()

# Current game score for self (red) and opponent (blue).
score = [ 0, 0 ]

# Keep track of how many blue snowmen we've seen.
smb_seen = 0

# Current snow height in each cell.
height = []

# Contents of each cell.
ground = []

# locations of children by x,y coordinates, for faster lookup.
child_at = {}

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

    smb_list = []   # list of known blue snowmen, or potential snowmen.
    
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
                if (ground[i][j] == GROUND_SMB or
                    (ground[i][j] == GROUND_LM and height < 9)):  # ignore if we can't finish
                    smb_list.append((i, j))
                    if ground[i][j] == GROUND_SMB:
                        smb_seen += 1
                
    # Read the states of all the children.
    child_at.clear()
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

            child_at[(c.pos.x, c.pos.y)] = i

            if i >= CCOUNT:
                c.last_known.set(c.pos.x, c.pos.y)
                c.targeted_by = -1

            # Read the stance, what the child is holding and how much
            # longer he's dazed.
            c.standing = ( tokens[ 2 ] == "S" )
            
            c.holding = string.find( string.ascii_lowercase, tokens[ 3 ] )

            c.dazed = string.atoi( tokens[ 4 ] )

    # Mark all the children in the map, so they are easy to look up.
    for i in range( 2 * CCOUNT ):
        c = cList[ i ]
        if c.pos.x >= 0:
            if i < CCOUNT:
                ground[ c.pos.x ][ c.pos.y ] = GROUND_CHILD_RED
            else:
                ground[ c.pos.x ][ c.pos.y ] = GROUND_CHILD_BLUE


    # TODO: come up with a list of targets?
    # try to make it so that two children don't just have the same target.
    # because there is no point in both hitting a child at the same time.

    # Decide what each child should do
    for i in range( CCOUNT ):
        c = cList[ i ]
        m = Move()

        if i != 2:
            determine_action_for_child(c, i, cList, smb_list, m)
        else:
            #sys.stderr.write( "%d %d\n" % ( c.got_four_targets, len(smb_list) ) )
            if c.got_four_targets and smb_seen == 0:   # len(smb_list) == 0:
                # got all the way around, and haven't seen any blue snowmen.
                determine_action_for_child(c, i, cList, smb_list, m)
            else:
                determine_special_action(c, cList, smb_list, m)
                #sys.stderr.write( "%d %d\n" % ( c.target.x, c.target.y ) )

        # avoid an attempt to move into the same space during this turn.
        # avoid drop attempts to the same location!  one has to idle!!
        if i > 0:
            for prev_c_index in range(0, i):
                if ((m.action == "crawl" or m.action == "run" or m.action == "drop") and
                     m.dest == cList[prev_c_index].last_dest):
                    m.action = "idle"
                    m.dest = None

        if ((c.last_action == "crawl" or c.last_action == "run") and
            c.last_action == m.action and
            c.last_dest == m.dest and
            c.pos == c.last_pos and
            c.dazed == 0):
            m.action = "idle"
            m.dest = None

        c.last_action = m.action
        c.last_pos = c.pos

        # Write out the child's move
        if m.dest == None:
            sys.stdout.write( "%s\n" % m.action )
            c.last_dest.set(-1,-1)
        else:
            sys.stdout.write( "%s %d %d\n" % ( m.action, m.dest.x, m.dest.y ) )
            c.last_dest.set(m.dest.x, m.dest.y)

    sys.stdout.flush()
    turnNum = string.atoi( sys.stdin.readline() )
