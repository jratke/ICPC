// Constants supporting a player in the icypc challenge game.  Feel
// free to use this and extend it for your own implementation.
//
// ICPC Challenge
// Sturgill, Baylor University

/** Collection of constants from the game. */
public class Const {
  /** Width and height of the playing field. */
  public static final int SIZE = 31;
  
  /** Number of children on each team. */
  public static final int CCOUNT = 4;

  /** Constants for the objects in each cell of the field */
  public static final int GROUND_EMPTY = 0;  // Just powdered snow in this space.
  public static final int GROUND_TREE = 1;   // A tree in this space
  public static final int GROUND_S = 2;      // A small snowball in this space
  public static final int GROUND_M = 3;      // A medium snowball in this space
  public static final int GROUND_MS = 4;     // A small snowball on a medium one
  public static final int GROUND_L = 5;      // A large snowball in this space
  public static final int GROUND_LM = 6;     // A medium snowball on a large one.
  public static final int GROUND_LS = 7;     // A small snowball on a large one.
  public static final int GROUND_SMR = 8;    // A red Snowman in this space
  public static final int GROUND_SMB = 9;    // A blue Snowman in this space
  
  /** Constants for the things a child can be holding */
  public static final int HOLD_EMPTY = 0;    // Child is holding nothing
  public static final int HOLD_P1 = 1;       // Child is holding one unit of powdered snow
  public static final int HOLD_P2 = 2;       // Child is holding two units of powdered snow
  public static final int HOLD_P3 = 3;       // Child is holding three units of powdered snow
  public static final int HOLD_S1 = 4;       // Child is holding one small snowball.
  public static final int HOLD_S2 = 5;       // Child is holding two small snowballs.
  public static final int HOLD_S3 = 6;       // Child is holding three small snowballs.
  public static final int HOLD_M = 7;        // Child is holding one medium snowball.
  public static final int HOLD_L = 8;        // Child is holding one large snowball.

  /** Constant for the red player color */
  public static final int RED = 0;

  /** Constant for the blue player color */
  public static final int BLUE = 1;

  /** Height for a standing child. */
  public static final int STANDING_HEIGHT = 9;
  
  /** Height for a crouching child. */
  public static final int CROUCHING_HEIGHT = 6;

  /** Maximum Euclidean distance a child can throw. */
  public static final int THROW_LIMIT = 24;

  /** Snow capacity limit for a space. */
  public static final int MAX_PILE = 9;

  /** Snow that's too deep to move through. */
  public static final int OBSTACLE_HEIGHT = 6;
}
