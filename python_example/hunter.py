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
GROUND_CHILD = 10

# Representation of a 2D point, used for playing field locations.
class Point:
    def __init__( self, xv, yv ):
        self.x = xv
        self.y = yv

    def set( self, vx, vy ):
        self.x = vx
        self.y = vy


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


# Fill in move m to move the child c twoard the given target location, either
# crawling or running.
def moveToward( c, target, m ):
    if c.standing:
        # Run to the destination
        if c.pos.x != target.x:
            if c.pos.y != target.y:
                # Run diagonally.
                m.action = "run"
                m.dest = Point( c.pos.x + clamp( target.x - c.pos.x, -1, 1 ),
                                c.pos.y + clamp( target.y - c.pos.y, -1, 1 ) )
            else:
                # Run left or right
                m.action = "run"
                m.dest = Point( c.pos.x + clamp( target.x - c.pos.x, -2, 2 ), 
                                c.pos.y )
        elif c.pos.y != target.y:
            # Run up or down.
            m.action = "run"
            m.dest = Point( c.pos.x, 
                            c.pos.y + clamp( target.y - c.pos.y, -2, 2 ) )
    else:
        # Crawl to the destination
        if c.pos.x != target.x:
            # crawl left or right
            m.action = "crawl"
            m.dest = Point( c.pos.x + clamp( target.x - c.pos.x, -1, 1 ), 
                            c.pos.y )
        elif c.pos.y != target.y:
            # crawl up or down.
            m.action = "crawl"
            m.dest = Point( c.pos.x, 
                            c.pos.y + clamp( target.y - c.pos.y, -1, 1 ) )



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

            # Compute child color based on it's index.
            if i < CCOUNT:
                c.color = RED
            else:
                c.color = BLUE
        
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
            ground[ c.pos.x ][ c.pos.y ] = GROUND_CHILD

    # Decide what each child should do
    for i in range( CCOUNT ):
        c = cList[ i ]
        m = Move()

        if c.dazed == 0:
            # See if the child needs a new destination.
            while runTimer[ i ] <= 0 or runTarget[ i ] == c.pos:
                runTarget[ i ].set( rnd.randint( 0, SIZE - 1 ),
                                    rnd.randint( 0, SIZE - 1 ) )
                runTimer[ i ] = rnd.uniform( 1, 14 )

        # Try to acquire a snowball if we need one.
        if c.holding != HOLD_S1:
            # Crush into a snowball, if we have snow.
            if c.holding == HOLD_P1:
                m.action = "crush"
            else:
                # We don't have snow, see if there is some nearby.
                sx = -1
                sy = -1
                for ox in range( c.pos.x - 1, c.pos.x + 2 ):
                    for oy in range( c.pos.y - 1, c.pos.y + 2 ):
                        # Is there snow to pick up?
                        if ( ox >= 0 and ox < SIZE and
                             oy >= 0 and oy < SIZE and
                             ( ox != c.pos.x or oy != c.pos.y ) and
                             ground[ ox ][ oy ] == GROUND_EMPTY and
                             height[ ox ][ oy ] > 0 ) :
                           sx = ox
                           sy = oy
                               
                # If there is snow, try to get it.
                if sx >= 0:
                    if c.standing:
                        m.action = "crouch"
                    else:
                        m.action = "pickup"
                        m.dest = Point( sx, sy )

        else:
            # Stand up if the child is armed.
            if not c.standing:
                m.action = "stand"
            else:
                # Try to find a victim.
                victimFound = 0
                j = CCOUNT
                while j < CCOUNT * 2 and not victimFound:
                    if cList[ j ].pos.x >= 0:
                        # We know where this child is, see if it's not too far away.
                        dx = cList[ j ].pos.x - c.pos.x
                        dy = cList[ j ].pos.y - c.pos.y
                        dsq = dx * dx + dy * dy
                        if dsq < 8 * 8:
                            victimFound = 1
                            m.action = "throw"
                            # throw past the victim, so we will probably hit them
                            # before the snowball falls into the snow.
                            m.dest = Point( c.pos.x + dx * 2,
                                            c.pos.y + dy * 2 )
                    j += 1

            # Try to run toward the destination.
            if m.action == "idle":
                moveToward( c, runTarget[ i ], m )
                runTimer[ i ] -= 1


        # Write out the child's move
        if m.dest == None:
            sys.stdout.write( "%s\n" % m.action )
        else:
            sys.stdout.write( "%s %d %d\n" % ( m.action, m.dest.x, m.dest.y ) )

    sys.stdout.flush()
    turnNum = string.atoi( sys.stdin.readline() )
