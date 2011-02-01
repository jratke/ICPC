// A simple player that just tries to plant snowmen in interesting
// places.
//
// Feel free to use this as a starting point for your own player.
//
// ICPC Challenge
// Sturgill, Baylor University

import java.util.ArrayList;
import java.util.Scanner;
import java.util.Random;
import java.awt.Point;

public class Planter {
  // Constant used to mark child locations in the map.
  public static final int GROUND_CHILD = 10;

  /** Current game score for self (red) and opponent (blue). */
  private int[] score = new int [ 2 ];

  /** Current snow height in each cell. */
  private int[][] height = new int [ Const.SIZE ][ Const.SIZE ];

  /** Contents of each cell. */
  private int[][] ground = new int [ Const.SIZE ][ Const.SIZE ];

  /** List of children on the field, half for each team. */
  private Child[] cList = new Child [ 2 * Const.CCOUNT ];

  /** Source of randomness for this player. */
  static Random rnd = new Random();

  /** Return the value of x, clamped to the [ a, b ] range. */
  static int clamp( int x, int a, int b ) {
    if ( x < a )
      return a;
    if ( x > b )
      return b;
    return x;
  }

  // Simple representation for a child's action
  static class Move {
    /** Make an idel move. */
    Move() {
      action = "idle";
    }

    /** Make a move for the given action. */
    Move( String act ) {
      action = act;
    }

    /** Make a move for the given action and destination. */
    Move( String act, int x, int y ) {
      action = act;
      dest = new Point( x, y );
    }

    // Action the child is making.
    String action = "idle";

    // Destiantion of this action (or null, if it doesn't need one) */
    Point dest = null;
  }

  // Simple representation for a child in the game.  Subclasses of
  // child can implement their own behavior.
  public class Child {
    // Location of the child.
    Point pos = new Point();

    // True if  the child is standing.
    boolean standing;

    // Side the child is on.
    int color;

    // What's the child holding.
    int holding;

    // How many more turns this child is dazed.
    int dazed;

    /** The child object provides both behavior and representation.
        We don't need the behavior part for snowmen on the opposing
        team, so we just make instances of the superclass for them. */
    public Move chooseMove() {
      return new Move();
    }
  }

  /** sequence of moves templates to build a to the right of the player.
      For the first one, we're just looking for a place to build. */
  static final Move[] instructions = {
    new Move( "idle" ),
    new Move( "crouch" ),
    new Move( "pickup", 1, 0 ),
    new Move( "pickup", 1, 0 ),
    new Move( "pickup", 1, 0 ),
    new Move( "crush" ),
    new Move( "drop", 1, 0 ),
    new Move( "pickup", 1, 1 ),
    new Move( "pickup", 1, 1 ),
    new Move( "crush" ),
    new Move( "drop", 1, 0 ),
    new Move( "pickup", 1, 1 ),
    new Move( "crush" ),
    new Move( "drop", 1, 0 ),
    new Move( "stand" ),
  };

  // Child that moves away from other children and
  // then builds a snowman.
  public class SnowmanMaker extends Child {
    /** Current instruction this child is executing. */
    int state = 0;

    /** Current destination of this child. */
    Point runTarget = new Point();

    /** How many more turns is this child going to run toward
        the target. */
    int runTimer;

    /** Return a move to get this child closer to target. */
    Move moveToward( Point target ) {
      if ( standing ) {
        // Run to the destination
        if ( pos.x != target.x ) {
          if ( pos.y != target.y ) {
            // Run diagonally.
            return new Move( "run",
                             pos.x + clamp( target.x - pos.x, -1, 1 ),
                             pos.y + clamp( target.y - pos.y, -1, 1 ) );
          }
          // Run left or right
          return new Move( "run",
                           pos.x + clamp( target.x - pos.x, -2, 2 ), 
                           pos.y );
        }

        if ( pos.y != target.y )
          // Run up or down.
          return new Move( "run",
                           pos.x, 
                           pos.y + clamp( target.y - pos.y, -2, 2 ) );
      } else {
        // Crawl to the destination
        if ( pos.x != target.x )
          // crawl left or right
          return new Move( "crawl",
                           pos.x + clamp( target.x - pos.x, -1, 1 ), 
                           pos.y );
       
        if ( pos.y != target.y )
          // crawl up or down.
          return new Move( "crawl",
                           pos.x, 
                           pos.y + clamp( target.y - pos.y, -1, 1 ) );
      }

      // Nowhere to move, just reutrn the idle move.
      return new Move();
    }

    public Move chooseMove() {
      if ( dazed > 0 )
        return new Move();

      if ( state == 0 ) {
        // Not building a snowman.
        
        // If we didn't get to finish the last snowman, maybe we're holding shomething.
        // We should drop it.
        if ( holding != Const.HOLD_EMPTY &&
             pos.y < Const.SIZE - 1 &&
             height[ pos.x ][ pos.y + 1 ] <= Const.MAX_PILE - 3 )
          return new Move( "drop", pos.x, pos.y + 1 );

        // Find the nearest neighbor.
        int nearDist = 1000;
        for ( int i = 0; i < Const.SIZE; i++ )
          for ( int j = 0; j < Const.SIZE; j++ )
            if ( ( i != pos.x || j != pos.y ) &&
                 ( ground[ i ][ j ] == GROUND_CHILD || 
                   ground[ i ][ j ] == Const.GROUND_SMR ) ) {

              int dx = ( pos.x - i );
              int dy = ( pos.y - j );

              if ( dx * dx + dy * dy < nearDist )
                nearDist = dx * dx + dy * dy;
            }

        // See if we should start running our build script.
        // Are we far from other things, is the ground empty
        // and do we have enough snow to build a snowman.
        if ( nearDist > 5 * 5 && 
             pos.x < Const.SIZE - 1 &&
             pos.y < Const.SIZE - 1 &&
             ground[ pos.x + 1 ][ pos.y ] == Const.GROUND_EMPTY &&
             ground[ pos.x + 1 ][ pos.y + 1 ] == Const.GROUND_EMPTY &&
             height[ pos.x + 1 ][ pos.y ] >= 3 &&
             height[ pos.x + 1 ][ pos.y + 1 ] >= 3 &&
             holding == Const.HOLD_EMPTY ) {
          // Start trying to build a snowman.
          state = 1;
        }
      }

      // Are we building a snowman?
      if ( state > 0 )  {
        // Stamp out a move from our instruction template and return it.
        Move m = new Move( instructions[ state ].action );
        if ( instructions[ state ].dest != null )
          m.dest = new Point( pos.x + instructions[ state ].dest.x,
                              pos.y + instructions[ state ].dest.y );
        state = ( state + 1 ) % instructions.length;

        return m;
      }

      // Run around looking for a good place to build

      // See if the child needs a new, random destination.
      while ( runTimer <= 0 ||
              runTarget.equals( pos ) ) {
        // Pick somewhere to run, omit the top and righmost edges.
        runTarget.setLocation( rnd.nextInt( Const.SIZE - 1 ),
                               rnd.nextInt( Const.SIZE - 1 ) );
        runTimer = 1 + rnd.nextInt( 14 );
      }

      runTimer--;
      return moveToward( runTarget );
    }
  }

  public void run() {
    for ( int i = 0; i < cList.length; i++ )
      if ( i < Const.CCOUNT ) 
        cList[ i ] = new SnowmanMaker();
      else
        cList[ i ] = new Child();

    // Scanner to parse input from the game engine.
    Scanner in = new Scanner( System.in );

    // Random destination for each player.
    Point[] runTarget = new Point [ Const.CCOUNT ];
    for ( int i = 0; i < runTarget.length; i++ )
      runTarget[ i ] = new Point();
    
    // How long the child has left to run toward its destination.
    int[] runTimer = new int [ Const.CCOUNT ];

    // Keep reading states until the game ends.
    int turnNum = in.nextInt();
    while ( turnNum >= 0 ) {
      String token;

      // Read current game score.
      score[ Const.RED ] = in.nextInt();
      score[ Const.BLUE ] = in.nextInt();

      // Parse the current map.
      for ( int i = 0; i < Const.SIZE; i++ ) {
        for ( int j = 0; j < Const.SIZE; j++ ) {
          // Can we see this cell?
          token = in.next();
          if ( token.charAt( 0 ) == '*' ) {
            height[ i ][ j ] = -1;
            ground[ i ][ j ] = -1;
          } else {
            height[ i ][ j ] = token.charAt( 0 ) - '0';
            ground[ i ][ j ] = token.charAt( 1 ) - 'a';
          }
        }
      }

      // Read the states of all the children.
      for ( int i = 0; i < Const.CCOUNT * 2; i++ ) {
        Child c = cList[ i ];
        
        // Can we see this child?        
        token = in.next();
        if ( token.equals( "*" ) ) {
          c.pos.x = -1;
          c.pos.y = -1;
        } else {
          // Record the child's location.
          c.pos.x = Integer.parseInt( token );
          c.pos.y = in.nextInt();

          // Compute child color based on it's index.
          c.color = ( i < Const.CCOUNT ? Const.RED : Const.BLUE );
        
          // Read the stance, what the child is holding and how much
          // longer he's dazed.
          token = in.next();
          c.standing = token.equals( "S" );
        
          token = in.next();
          c.holding = token.charAt( 0 ) - 'a';

          c.dazed = in.nextInt();
        }
      }
      
      // Mark all the children in the map, so they are easy to
      // look up.
      for ( int i = 0; i < Const.CCOUNT * 2; i++ ) {
        Child c = cList[ i ];
        if ( c.pos.x >= 0 ) {
          ground[ c.pos.x ][ c.pos.y ] = GROUND_CHILD;
        }
      }
      
      // Decide what each child should do
      for ( int i = 0; i < Const.CCOUNT; i++ ) {
        Move m = cList[ i ].chooseMove();

        /** Write out the child's move */
        if ( m.dest == null ) {
          System.out.println( m.action );
        } else {
          System.out.println( m.action + " " + m.dest.x + " " + m.dest.y );
        }
      }
      
      turnNum = in.nextInt();
    }
  }

  public static void main( String[] args ) {
    Planter planter = new Planter();
    planter.run();
  }
}
