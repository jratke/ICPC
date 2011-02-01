// A simple player that makes a little fort and hides behind it.
//
// Feel free to use this as a starting point for your own player.
//
// ICPC Challenge
// Sturgill, UNC Greensboro
// I'm not really a C# programer

using System;

public class Camper {
  public static void Main() {
    // Make an instance of the Camper class and let it play the game.
    Camper camper = new Camper();
    camper.run();
  }

  private void run() {
    int turnNum = int.Parse( Console.ReadLine() );
    while ( turnNum >= 0 ) {
      // Read the current score.
      string[] tokens = Console.ReadLine().Split();

      score[ RED ] = int.Parse( tokens[ 0 ] );
      score[ BLUE ] = int.Parse( tokens[ 1 ] );

      // Read the state of the field.
      for ( int i = 0; i < SIZE; i++ ) {
        tokens = Console.ReadLine().Split();
        for ( int j = 0; j < SIZE; j++ ) {
          if ( tokens[ j ][ 0 ] != '*' ) {
            height[ i, j ] = tokens[ j ][ 0 ] - '0';
            ground[ i, j ] = tokens[ j ][ 1 ] - 'a';
          } else {
            height[ i, j ] = -1;
            ground[ i, j ] = -1;
          }
        }
      }

      for ( int i = 0; i < cList.Length; i++ ) {
        tokens = Console.ReadLine().Split();
        if ( tokens[ 0 ] == "*" ) {
          // Can't see this child
          cList[ i ].x = -1;
          cList[ i ].y = -1;
        } else {
          // Can see this child, read the description.
          cList[ i ].x = int.Parse( tokens[ 0 ] );
          cList[ i ].y = int.Parse( tokens[ 1 ] );

          // Fill in the child's side.
          cList[ i ].color = i / CCOUNT;

          // Read the child's stanse, what he's holding and how much
          // longer he's dazed.
          cList[ i ].standing = ( tokens[ 2 ] == "S" );
          cList[ i ].holding = ( tokens[ 3 ][ 0 ] - 'a' );
          cList[ i ].dazed = int.Parse( tokens[ 4 ] );
        }
      }

      // Mark child locations, so we can walk around them.
      for ( int i = 0; i < cList.Length; i++ ) {
        if ( cList[ i ].x >= 0 ) {
          ground[ cList[ i ].x, cList[ i ].y ] = GROUND_CHILD;
        }
      }

      // Choose an action for each child.
      for ( int i = 0; i < CCOUNT; i++ ) {
        // Try up to three times to get a useful move
        int tryCount = 0;

        while ( tryCount < 3 &&
                !chooseMove( i ) )
          tryCount++;
      
        // If we can't think of a good move, wait and see if something happens.
        if ( tryCount >= 3 )
          Console.WriteLine( "idle" );
      }
    
      turnNum = int.Parse( Console.ReadLine() );
    }
  }

  // Try to pick a next move.  Return false if the child just
  // turns in place and chooses no move.
  private bool chooseMove( int i ) {
    // If we're dazed, we have to stay idle.
    if ( cList[ i ].dazed > 0 ) {
      Console.WriteLine( "idle" );
      return true;
    }

    // Pick up some snow if there's some nearby.
    if ( cList[ i ].holding == HOLD_EMPTY ) {
      // See if there's some snow nearby.
      int sx = -1, sy = -1;
      for ( int ox = cList[ i ].x - 1; ox <= cList[ i ].x + 1; ox++ )
        for ( int oy = cList[ i ].y - 1; oy <= cList[ i ].y + 1; oy++ ) {
          // Is there snow to pick up?  Can we pick it up?  Do we want to?
          if ( ox >= 0 && ox < FORT_SIZE &&
               oy >= 0 && oy < FORT_SIZE &&
               ( ox != cList[ i ].x || oy != cList[ i ].y ) &&
               ground[ ox, oy ] == GROUND_EMPTY &&
               height[ ox, oy ] > 0 ) {
            sx = ox;
            sy = oy;
          }
        }
        
      // Try to crouch down and pick up snow if there is some.
      if ( sx >= 0 ) {
        if ( cList[ i ].standing ) {
          Console.WriteLine( "crouch" );
          return true;
        }

        // Pick up snow from the space, and mark it
        // as taken so another one of our children
        // won't try to take it also.
        Console.WriteLine( "pickup " + sx + " " + sy );
        ground[ sx, sy ] = GROUND_TAKEN;
        return true;
      }
    }

    // Crush one unit of powdered snow into a snowball.
    if ( cList[ i ].holding == HOLD_P1 ) {
      Console.WriteLine( "crush" );
      return true;
    }

    if ( cList[ i ].holding == HOLD_S1 ) {
      // We're holding a small snowball.
      if ( !cList[ i ].standing ) {
        Console.WriteLine( "stand" );
        return true;
      }

      // See if we should throw a snowball at an opponent.
      for ( int j = CCOUNT; j < CCOUNT * 2; j++ ) {
        if ( cList[ j ].x >= 0 ) {
          int dx = cList[ j ].x - cList[ i ].x;
          int dy = cList[ j ].y - cList[ i ].y;
          int dsq = dx * dx + dy * dy;
          // If we see a nearby child, throw past them.
          if ( dsq < 8 * 8 ) {
            Console.WriteLine( "throw " + ( cList[ i ].x + dx * 2 ) +
                                      " " + ( cList[ i ].y + dy * 2 ) );
            return true;
          }
        }
      }

      // Is the wall to our right?
      int r = ( walkDir[ i ] + 3 ) % 4;
      int rightX = cList[ i ].x + dispX[ r ];
      int rightY = cList[ i ].y + dispY[ r ];

      if ( rightX >= 0 && rightY >= 0 &&
           ( rightX == FORT_SIZE || rightY == FORT_SIZE ) &&
           height[ rightX, rightY ] < OBSTACLE_HEIGHT ) {
        Console.WriteLine( "drop " + rightX + " " + rightY );
        return true;
      }
    }

    // See where the child is moving.
    int newX = cList[ i ].x + dispX[ walkDir[ i ] ];
    int newY = cList[ i ].y + dispY[ walkDir[ i ] ];

    // Child may turn just because she feels like it.
    if ( rand.Next( 10 ) == 0 ) {
      walkDir[ i ] = ( walkDir[ i ] + 1 ) % 4;
      return false;
    }

    // Child must turn if she hits the edge of the fort.
    if ( newX < 0 || newY < 0 ||
         newX >= FORT_SIZE || newY >= FORT_SIZE ) {
      walkDir[ i ] = ( walkDir[ i ] + 1 ) % 4;
      return false;
    } 
  
    // Turn must turn if the walk direction is blocked.
    if ( ground[ newX, newY ] == GROUND_TREE ||
         ground[ newX, newY ] == GROUND_CHILD ||
         height[ newX, newY ] >= OBSTACLE_HEIGHT ) {
      walkDir[ i ] = ( walkDir[ i ] + 1 ) % 4;
      return false;
    }

    // Move on around the perimiter if we have nothing better
    // to do.
    if ( cList[ i ].standing ) {
      Console.Write( "run " );
    } else {
      Console.Write( "crawl " );
    }
    Console.WriteLine( newX + " " + newY );

    // Update the map, so that the next child won't try to mvoe
    // right into this one.
    ground[ cList[ i ].x, cList[ i ].y ] = GROUND_TAKEN;
    ground[ newX, newY ] = GROUND_CHILD;
  
    return true;
  }

  /** Simple representation for a child in the Game. */
  struct Child {
    // Location of the child.
    public int x, y;

    // True if  the child is standing.
    public bool standing;

    // Side the child is on.
    public int color;

    // What's the child holding.
    public int holding;

    // How many more turns this child is dazed.
    public int dazed;
  };

  // X displacement for each walk direction.
  int[] dispX = {
    1,
    0,
    -1,
    0,
  };

  // Y displacement for each walk direction.
  int[] dispY = {
    0,
    1,
    0,
    -1,
  };


  /** Width and height of the playing field. */
  const int SIZE = 31;
  
  /** Number of children on each team. */
  const int CCOUNT = 4;

  /** Constants for the objects in each cell of the field */
  const int GROUND_EMPTY = 0;  // Just powdered snow in this space.
  const int GROUND_TREE = 1;   // A tree in this space
  const int GROUND_S = 2;      // A small snowball in this space
  const int GROUND_M = 3;      // A medium snowball in this space
  const int GROUND_MS = 4;     // A small snowball on a medium one
  const int GROUND_L = 5;      // A large snowball in this space
  const int GROUND_LM = 6;     // A medium snowball on a large one.
  const int GROUND_LS = 7;     // A small snowball on a large one.
  const int GROUND_SMR = 8;    // A red Snowman in this space
  const int GROUND_SMB = 9;    // A blue Snowman in this space
  
  /** Extra constant to mark child locations on the map. */
  const int GROUND_CHILD = 10;

  /** Constants for the things a child can be holding */
  const int HOLD_EMPTY = 0;    // Child is holding nothing
  const int HOLD_P1 = 1;       // Child is holding one unit of powdered snow
  const int HOLD_P2 = 2;       // Child is holding two units of powdered snow
  const int HOLD_P3 = 3;       // Child is holding three units of powdered snow
  const int HOLD_S1 = 4;       // Child is holding one small snowball.
  const int HOLD_S2 = 5;       // Child is holding two small snowballs.
  const int HOLD_S3 = 6;       // Child is holding three small snowballs.
  const int HOLD_M = 7;        // Child is holding one medium snowball.
  const int HOLD_L = 8;        // Child is holding one large snowball.

  /** Constant for the red player (self) color */
  const int RED = 0;

  /** Constant for the blue player (opponent) color */
  const int BLUE = 1;

  /** Height for a standing child. */
  const int STANDING_HEIGHT = 9;
  
  /** Height for a crouching child. */
  const int CROUCHING_HEIGHT = 6;

  /** Maximum Euclidean distance a child can throw. */
  const int THROW_LIMIT = 24;

  /** Snow capacity limit for a space. */
  const int MAX_PILE = 9;

  /** Snow that's too deep to move through. */
  const int OBSTACLE_HEIGHT = 6;

  /** Another extra constant to mark spaces we should not pick
      up from. */
  const int GROUND_TAKEN = 11;

  /** How big of a fort do we want to try to build. */
  const int FORT_SIZE = 6;

  // Current walk direction for each child.
  int[] walkDir = {
    1,
    0,
    2,
    3
  };

  // Current game score, for red and blue
  private int[] score = new int [ 2 ];

  // Current snow height in each cell.
  private int[,] height = new int [ SIZE, SIZE ];

  // Contents of each cell.
  private int[,] ground = new int [ SIZE, SIZE ];
  
  // List of current information about each child.
  private Child[] cList = new Child [ CCOUNT * 2 ];

  // Source of randomness
  private Random rand = new Random();
}
