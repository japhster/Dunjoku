
Requirements:
 - Python
 - Pygame


## Building the game board:
A single hexagon with two straight edges in the vertical plane (a cell) is surrounded by 6 hexagons joned by their straight edges. This will be refered to as a "subhexagon". Place a subhexagon in the center of the board and then surround the subhexagon with 6 more subhexagons connected by the edge hexagons. This is the game board.


## Game board filling rules:
 - The numbers 1 to 7 must be placed in the cells of each subhexagon such that the two diagonals and one horizontal row from each cell do not have duplicate values and each subhexagon does not have repeating values. Note: rows and diagonals vary in length (2, 5, or 7 cells) depending on their position in the board — the constraint is no duplicates within the line, not that every value 1-7 must appear.
 - these values 1 to 7 should be replaced with monster names in this way (with brackets denoting the letter that indicates the monster when placed in the grid):
  - 1 becomes a Fighter (F)
  - 2 becomes a Goblin (G)
  - 3 becomes a Skeleton (S)
  - 4 becomes a Warlock (W)
  - 5 becomes a Gelatinous Cube (C)
  - 6 becomes a Troll (T)
  - 7 becomes a Dragon (D)


## Generating the game:

The grid should be filled using a back-tracking algorithm following the above game board filling rules where the cell that has the fewest possible values is filled in first - randomly selected from the set of cells with the fewest possible values when there is a tie. If a game board state is reached where any cell has no possible values: backtrack until a point at which there are other possibilities. Keep track of the cases where filling a cell with a value causes an incompletable board and do not follow these paths again.

A Player can follow these rules to play the game:
 - Inspect any given cell to see if there is only one possible value according to the grid filling rules (all other possible values for the cell are contained within the two diagonals, one horizontal row and the subhexagon in which the cell sits).

To create a playable board, remove cells from the grid randomly until a state has been achieved where remove any other single cell makes it impossible for a player to recomplete the grid using the rules described for playing the game. Keep a record of both the playable grid and the complete grid.


## Playing the game

Display a white pygame window fullscreen. Display the playable grid to the user in this window using black for the hexagon outlines. Place the letters in the cells that are prefilled for the player based on the playable grid in black text. The monsters that can be used to fill the grid should be placed in the window in a list layout with the top most item being the lowest value monster and the bottom most being the highest value. Each line laid out as:
"[grid letter representation] - [name of monster]"

Allow the player to drag the monster representing letters onto the grid. Figure out which cell the letter is dragged to based on which cell has the majority of the monster icon on it. Check the monster goes in that cell based on the complete grid and if it does reveal that letter in that cell. If it doesn't go there make the background flash red and the grid shake slightly and do not reveal the correct cell value.

Once the full grid is complete display a message in the window saying "Congratulations! You have completed a Dunjoku grid. Would you like to play again?" with two buttons "Yes" and "No" below. If the player clicks "Yes" generate a new game and start again. If the player clicks "No" close the application.
