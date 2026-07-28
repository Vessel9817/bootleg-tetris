#!/usr/bin/python3

from random import randint

import pygame

from .block import Block


class Grid:
    """
    The game board, a coloured grid of square cells.

    Static attributes:
        - COLS : The number of columns in the grid
        - ROWS : The number of rows in the grid
        - GRIDS : A list of each grid instance
        - BLOCKS : A list of the possible block types
        - NEXT_BLOCKS : The block queue
        - LEVEL : The game's current level, which affects block drop speed
        - SPEED : The game's current soft drop rate
        - __SCORE : The scoring increments, based on the quantity of lines immediately cleared

    Attributes:
        - __x : The x-coordinate of the grid on the surface
        - __y : The y-coordinate of the grid on the surface
        - __width : The width of the grid in pixels
        - __height : The height of the grid in pixels
        - __cellLength : The length of each square cell in pixels
        - __surface : The surface that the grid will be drawn on
        - __grid_index : The index of this grid object in the static list `GRIDS`
        - block : The controllable block of this grid
        - hold : The block type of the block being held
        - __block_index : The The index of the current block in the static list NEXT_BLOCKS
        - timer_running : The boolean indicator of wether the timer is running
        - timer : The countdown timer for the block locking mechanism
        - drop_counter : A counter used to slow down the block's automatic drop rate
        - flag : An indicator for whether a method has been called at least once or not
        - lose : The boolean value signifying the defeat of the player in control of this grid
        - win : A boolean indicator of whether the player has won or not
        - __is_held : The boolean value used to disable block holding more than once before a block locks into place
        - __lines_cleared : The quantity of lines cleared by the player
        - lines_received : The quantity of lines awaiting receival into the grid  
        - score : This player's current score
        - __grid_colours : 
        - __grid : A matrix of rectangles representing the grid
    """

    COLS = 10
    ROWS = 20
    GRIDS: list['Grid'] = []
    BLOCKS = ['i', 'j', 'l', 's', 'z', 't', 'o']
    NEXT_BLOCKS: list[str] = []
    LEVEL = 0
    SPEED = 35
    __SCORE: dict[int, int] = {
        0 : 0, # Just in case
        1 : 40,
        2 : 100,
        3 : 300,
        4 : 1200
    }

    block: Block
    hold: Block
    timer_running: bool
    timer: int
    drop_counter: int
    next_block_flag: bool
    lose: bool
    win: bool
    score: int
    lines_received: int
    __surface: pygame.surface.Surface
    __width: int
    __height: int
    __cell_length: int
    __grid_index: int
    __x: int
    __y: int
    __block_index: int
    __is_held: bool
    __lines_cleared: int
    __grid_colours: list[list[tuple[int, int, int]]]
    __grid: list[list[pygame.Rect]]

    def __init__(
        self,
        x: int,
        y: int,
        height: int,
        surface: pygame.surface.Surface
    ) -> None:
        '''The constructor/initialization method of the grid and its attributes

        Parameters:
            - x : The x-coordinate of where the grid's top-left corner should be drawn
            - y : The y-coordinate of where the grid's top-left corner should be drawn
            - height : The drawn grid's height in pixels
            - surface : The surface to draw the grid on
        '''
        self.__surface = surface
        self.__width = height // 2
        self.__height = height
        self.__cell_length = height // Grid.ROWS
        self.__grid_index = len(Grid.GRIDS)
        self.x = x
        self.y = y

        Grid.GRIDS.append(self)

        # Temporary initialization
        self.block = Block('?', self)
        self.hold = Block('?', self)
        self.__block_index = 0

        # Full initialization
        self.reset_grid()

    def reset_grid(self) -> None:
        '''Resets the Grid attributes, excluding unchanged attributes, such as __surface'''
        # Temporarily reinitializing block 
        self.block.reset_block('?')
        self.hold.reset_block('?')
        self.__block_index = 0

        # Resetting timers
        self.timer_running = False
        self.timer = 0
        self.drop_counter = 0

        # Resetting win/loss flags
        self.next_block_flag = False
        self.lose = False
        self.win = False

        # Resetting statistics
        self.__is_held = False
        self.__lines_cleared = 0
        self.lines_received = 0
        self.score = 0

        # Resetting grid cell colours
        self.__grid_colours = [
            [Block.BLACK for _ in range(Grid.COLS)]
            for _ in range(Grid.ROWS)
        ]

        # Resetting grid cells
        self.__grid = [
            [
                pygame.Rect(
                    self.x + j * self.__cell_length,
                    self.y + i * self.__cell_length,
                    self.__cell_length,
                    self.__cell_length
                )
                for j in range(Grid.COLS)
            ]
            for i in range(Grid.ROWS)
        ]

        Grid.LEVEL = 0
        Grid.SPEED = 35

        # Resetting drawn statistics
        self.draw_level()
        self.draw_hold()
        self.draw_score()
        self.draw_lines_cleared()

        # Generating new block if there are none
        if len(Grid.NEXT_BLOCKS) > len(Grid.GRIDS):
            Grid.NEXT_BLOCKS = [Grid.BLOCKS[randint(0, len(Grid.BLOCKS) - 1)]] # NOSONAR python:S2245 This is not a security context

        self.__get_next_block()

    def draw_hold(self) -> None:
        '''Draws text displaying the player's currently held block'''
        pygame.draw.rect(self.__surface, Block.BLACK, pygame.Rect(self.x - 100, self.y, 100, 100))
        font = pygame.font.SysFont(None, 20)
        hold_text = font.render(f'Holding {self.hold.get_block_type()}-block' if self.hold.get_block_type() != '?' else 'Holding nothing', False, Block.WHITE)
        self.__surface.blit(hold_text, (self.x - 100, self.y))

    def draw_level(self) -> None:
        '''Draws text displaying the current level'''
        pygame.draw.rect(self.__surface, Block.BLACK, pygame.Rect(self.x - 100, self.y + self.height // 1.5, 100, 30))
        font = pygame.font.SysFont(None, 20)
        level_text = font.render(f'level {Grid.LEVEL + 1}', False, Block.WHITE)
        self.__surface.blit(level_text, (self.x - 100, self.y + self.height // 1.5))

    def draw_lines_cleared(self) -> None:
        '''Draws text displaying the player's current quantity of cleared lines'''
        pygame.draw.rect(self.__surface, Block.BLACK, pygame.Rect(self.x - 100, self.y + self.height - 40, 100, 30))
        font = pygame.font.SysFont(None, 20)
        lines_text = font.render('Lines:', False, Block.WHITE)
        lines_value = font.render(str(self.__lines_cleared), False, Block.WHITE)
        self.__surface.blit(lines_text, (self.x - 100, self.y + self.height - 40))
        self.__surface.blit(lines_value, (self.x - 100, self.y + self.height - 20))

    def draw_score(self) -> None:
        '''Draws text displaying the player's current score'''
        pygame.draw.rect(self.__surface, Block.BLACK, pygame.Rect(self.x - 100, self.y + self.height // 1.25, 100, 30))
        font = pygame.font.SysFont(None, 20)
        score_text = font.render('Score:', False, Block.WHITE)
        score_value = font.render(str(self.score), False, Block.WHITE)
        self.__surface.blit(score_text, (self.x - 100, self.y + self.height // 1.25))
        self.__surface.blit(score_value, (self.x - 100, self.y + self.height // 1.25 + 20))

    def swap_hold(self) -> None:
        '''Swaps the current block with the currently held block; a process called holding. Can only occur once before this player locks a block'''
        if not self.__is_held:
            self.__is_held = True
            self.block.erase_block()

            if self.hold.get_block_type() == '?':
                self.next_block_flag = False
                self.hold.reset_block(self.block.get_block_type())
                self.__get_next_block()
            else:
                temp = self.hold.get_block_type()
                self.hold.reset_block(self.block.get_block_type())
                self.block.reset_block(temp)

            self.draw_hold()

    @property
    def x(self) -> int:
        '''The grid's x cooridnate '''
        return self.__x

    @x.setter
    def x(self, x: int) -> None:
        '''Sets the grid's x coordinate to *x* if x is within the bounds of the surface'''
        if 0 <= x <= self.__surface.get_width() - self.width:
            self.__x = x
        else:
            raise ValueError(f'X coordinate out of bounds: {x}')

    @property
    def y(self) -> int:
        '''The grid's y coordinate'''
        return self.__y

    @y.setter
    def y(self, y: int) -> None:
        '''Sets the grid's y coordiante to *y* if y is within the bounds of the surface'''
        if 0 <= y <= self.__surface.get_height() - self.height:
            self.__y = y
        else:
            raise ValueError(f'Y coordinate out of bounds: {y}')

    @property
    def width(self) -> int:
        '''The grid's width in pixels'''
        return self.__width

    @property
    def height(self) -> int:
        '''The grid's height in pixels'''
        return self.__height

    def draw_grid(self) -> None:
        '''If the the player has not won or lost, it draws the matrice of rectangles called __grid and draws the grid lines. If the player has lost, draws a big red rectangle with a label on it saying "You Lose". If the player has won, draws a big green rectangle with a label on it saying "You Win". '''
        if not self.lose and not self.win:
            # Checking if the game is still in progress
            for row in range(len(self.__grid)):
                for col in range(len(self.__grid[row])):
                    pygame.draw.rect(self.__surface, self.__grid_colours[row][col], self.__grid[row][col])

            for row in range(len(self.__grid) + 1):
                pygame.draw.rect(self.__surface, Block.WHITE, pygame.Rect(self.x, self.y + row * self.__cell_length, self.width, 1))

            for col in range(len(self.__grid[0]) + 1):
                pygame.draw.rect(self.__surface, Block.WHITE, pygame.Rect(int(self.x + col * self.__cell_length), self.y, 1, self.height))
        elif self.lose:
            # Checking if this player lost
            pygame.draw.rect(self.__surface, Block.RED, pygame.Rect(self.x, self.y, self.width, self.height))
            font = pygame.font.SysFont(None, 65)
            loss_text = font.render('You Lose', True, Block.WHITE)
            self.__surface.blit(loss_text, (self.x , self.y + self.height // 2))
        elif self.win:
            # Checking if this player won
            pygame.draw.rect(self.__surface, Block.GREEN, pygame.Rect(self.x, self.y, self.width, self.height))
            font = pygame.font.SysFont(None, 65)
            win_text = font.render('You Win', True, Block.WHITE)
            self.__surface.blit(win_text, (self.x , self.y + self.height // 2))

        # Updating window
        pygame.display.update()

    def get_cell(
        self,
        row: int,
        col: int
    ) -> tuple[pygame.Rect, tuple[int, int, int]]:
        '''
        Returns the grid's indexed cell and colour

        Parameters:
            - row : The row index of the cell
            - col : The column index of the cell

        Returns:
            tuple : The grid's indexed cell followed by its colour
        '''
        return self.__grid[row][col], self.__grid_colours[row][col]

    def set_cell(
        self,
        row: int,
        col: int,
        colour: tuple[int, int, int]
    ) -> None:
        '''Sets the grid's indexed cell colour to *colour*

        Parameters:
            - row : The row index of the cell
            - col : The column index of the cell
            - colour : The colour the cell is to be coloured
        '''
        self.__grid_colours[row][col] = colour

    def draw_block(self) -> None:
        '''Draws the current block on the grid'''
        for coords in self.block.get_coords():
            self.set_cell(coords[0], coords[1], self.block.colour)

    def lock(self) -> None:
        '''Manages a timer for when the current block should be either moveable or unmoveable when on the ground. Generates a new block if this block is locked (i.e., made unmovable)'''
        if self.timer >= Grid.SPEED * 3 and not self.block.detect_collision(r_off=-1):
            # Clearing lines and generating block
            self.__get_next_block()
            self.__clear_lines()

            # Resetting affected attributes
            self.timer_running = False
            self.__is_held = False
            self.timer = 0
        else:
            # Starting lock timer
            self.timer_running = True

    def instant_lock(self) -> None:
        '''Instantly locks the current block to the grid, clears and sends any complete lines. Generates a new block if this block is locked (i.e., made unmovable)'''
        self.__get_next_block()
        self.__clear_lines()

        # Resetting affected attributes
        self.timer_running = False
        self.__is_held = False
        self.timer = 0

    def __receive_lines(self) -> None:
        '''Detects and collects which rows in the grid will be moved and moves them up by the number of line sent. The empty space will be replaced by gray blocks which represent garbage lines. There will be a randomly selected column in which there will be no garbage lines to represent messiness. If the number of rows moved + the number of lines received exeeds or equals the number of rows on the grid, the player loses.'''
        top_row = None

        for i in range(Grid.ROWS):
            moveable = False

            for cell in self.__grid_colours[i]:
                if cell != Block.BLACK:
                    moveable = True
                    break

            if moveable:
                top_row = i
                break

        if top_row is not None:
            random_col = randint(0, Grid.COLS - 1) # NOSONAR python:S2245 This is not a security context

            if self.lines_received > top_row:
                self.lose = True
            else:
                # Moving rows up
                for row in range(top_row, Grid.ROWS):
                    for col in range(Grid.COLS):
                        self.set_cell(row - self.lines_received, col, self.__grid_colours[row][col])

                # Filling in garbage rows
                for row in range(Grid.ROWS - self.lines_received, Grid.ROWS):
                    for col in range(Grid.COLS):
                        self.set_cell(row, col, Block.GRAY if col != random_col else Block.BLACK)

    def __clear_lines(self) -> None:
        '''Finds and stores the rows which can be cleared and clears them while moving the rows above them down by the number of rows cleared. If rows were cleared, the __lines_cleared, score, LEVEL, and SPEED increase and visually update accordingly. Finally, reduces the lines received by the number of lines cleared. If the lines received attribute becomes negative, it sends lines back to the other grid using the GRIDS static list. If the lines received are still positive, it calls the receiveLines method to receive the lines and resets the lines received attribute'''
        cleared_rows: list[int] = []

        for i in range(Grid.ROWS):
            clearable = True

            # Checking if row is clearable
            for cell in self.__grid_colours[i]:
                if cell == Block.BLACK:
                    clearable = False

            if clearable:
                cleared_rows.append(i)

        if cleared_rows:
            # Changing scoring attributes
            self.__lines_cleared += len(cleared_rows)
            Grid.LEVEL = self.__lines_cleared // 10

            # len(cleared_rows) <= 4, but similarly to tetr.io, we're protected if not
            self.score += (len(cleared_rows) // 5) * Grid.__SCORE[4] + Grid.__SCORE[len(cleared_rows) % 5]

            # Changing speed; capped at 1 fps
            if Grid.LEVEL <= 17:
                Grid.SPEED = 35 - 2 * Grid.LEVEL

            if cleared_rows[0] > 0:
                for row in range(cleared_rows[0] - 1, -1, -1):
                    for col in range (Block.COLS):
                        self.set_cell(row + len(cleared_rows), col, self.__grid_colours[row][col])
                        self.set_cell(row, col, Block.BLACK)

            # Visually updating scoring attributes
            self.draw_level()
            self.draw_score()
            self.draw_lines_cleared()

            # Reducing incoming lines
            self.lines_received -= len(cleared_rows)

            # Sending lines to other grid
            if self.lines_received < -1:
                Grid.GRIDS[1 - self.__grid_index].lines_received -= self.lines_received # Lines received is negative, remember

            self.lines_received = 0
        elif self.lines_received > 0:
            self.__receive_lines()
            self.lines_received = 0

    def __get_next_block(self) -> None:
        '''Replaces the current block with next block in NEXT_BLOCKS static list. If there are no blocks ahead in queue generates no blocks using the generateBlock method. Increases the block index attribute by 1.'''
        if self.next_block_flag:
            self.draw_block()

        self.next_block_flag = True

        # Generating new block if necessary
        if self.__block_index == len(Grid.NEXT_BLOCKS):
            Grid.__generate_block()

        # Setting block
        self.block.reset_block(Grid.NEXT_BLOCKS[self.__block_index])

        for coords in self.block.get_coords():
            if self.__grid_colours[coords[0]][coords[1]] != Block.BLACK:
                self.lose = True

        self.__block_index += 1

    @staticmethod
    def __generate_block() -> None:
        '''Based on certain conditions involving previously generated blocks, generates a new block and appends it to the static list BLOCKS'''
        blocks = Grid.BLOCKS.copy()

        try:
            # Allowing no 5 same blocks to be queued consecutively
            if len({Grid.NEXT_BLOCKS[i] for i in range(-4, 0)}) == 1:
                blocks.remove(Grid.NEXT_BLOCKS[-1])

            # Forcing at least one I-block within 12 queues of one another
            if [Grid.NEXT_BLOCKS[i] for i in range(-11, 0)].count('i') == 0:
                blocks = ['i']
        except IndexError:
            # Haven't generated enough blocks for these rules to apply yet
            pass

        # Appending generated block to queue
        Grid.NEXT_BLOCKS.append(blocks[randint(0, len(blocks) - 1)]) # NOSONAR python:S2245 This is not a security context

    def __repr__(self) -> str:
        '''repr override'''
        return f'Grid({self.x}, {self.y}, {self.height}, {repr(self.__surface)})'
