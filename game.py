import itertools
import random
import pygame
import time
from typing import List, Tuple

from pygame.font import Font
from pygame.surface import Surface

pygame.font.init()


class Board:
    """The Sudoku board."""

    def __init__(self, row: int, col: int, width: int, height: int, grid: List[List[int]],
                 solution_board: List[List[int]], screen: Surface) -> None:
        """
        Initialize the Board with row, col, width, height, the grid which is the board being displayed, the solution
        board, and the screen that the board is displayed on.
        """
        self.row = row
        self.col = col
        self.width = width
        self.height = height
        self.board = grid
        self.sol_board = solution_board
        self.gap_x = (screen.get_width() - self.width) // 2
        self.gap_y = (screen.get_height() - self.height) // 2
        self.x_max = self.row * 50 + self.gap_x
        self.y_max = self.col * 50 + self.gap_y
        self.squares = [[Square(self.board[i][j], i, j, self.gap_x, self.gap_y) for i in range(row)]
                        for j in range(col)]
        self.selected = None

    def draw_board(self, screen: Surface, current_time: int, fnt: Font) -> None:
        """
        Draw everything that needs to be on the screen. In the middle is the 9x9 grid and the number in each square.
        Centered above the grid is the current_time with size fnt. Below the bottom left of the grid is the check box
        to check the solution.
        """
        window.fill((255, 255, 255))
        black = (0, 0, 0)
        self.add_text(screen, current_time, fnt)
        n = 0
        # draw the board
        while n < 10:
            if n % 3 == 0:
                # bold line to indicate separate 3x3 subgrid
                thickness = 3
            else:
                thickness = 1
            pygame.draw.line(screen, black, (self.gap_x, self.gap_y + n * 50), (self.x_max, self.gap_y + n * 50),
                             thickness)
            pygame.draw.line(screen, black, (self.gap_x + n * 50, self.gap_y), (self.gap_x + n * 50, self.y_max),
                             thickness)
            n += 1
        # draw the numbers
        for i, j in itertools.product(range(self.row), range(self.col)):
            self.squares[i][j].draw_squares(screen, fnt)
        pygame.display.update()

    def add_text(self, screen: Surface, current_time: int, fnt: Font) -> None:
        """
        Add the current_time to screen to be displayed above the game board. Add a box for a button to check
        the solution below the bottom left of the board. Both texts will be displayed using the font fnt.
        """
        black = (0, 0, 0)
        text = fnt.render("Time: " + format_time(current_time), 1, black)
        window.blit(text, ((window.get_width() - text.get_width()) / 2, (self.gap_y - text.get_height()) / 2))
        text = fnt.render("Check", 1, black)
        rect_width = text.get_width() + 20
        rect_height = text.get_height() + 10
        x = self.gap_x + (50 * 3 - rect_width) // 2
        y = self.y_max + (self.gap_y - rect_height) // 2
        pygame.draw.rect(screen, (255, 204, 204), (x, y, rect_width, rect_height))
        window.blit(text, (x + (rect_width - text.get_width()) / 2, y + (rect_height - text.get_height()) / 2))

    def get_square(self, pos: Tuple[int], fnt: Font) -> bool:
        """
        Return True if the check button was selected and False otherwise. Rewrite the check box using font fnt. If
        the player selected a part of the screen that is not within the 9x9 grid then set selected to None, otherwise
        set selected to a list containing the row and column of the selected square. The selected position is given
        by pos where the first index is the x position and the second is the y position.
        """
        text = fnt.render("Check", 1, (0, 0, 0))
        rect_width = text.get_width() + 20
        rect_height = text.get_height() + 10
        x = self.gap_x + (50 * 3 - rect_width) // 2
        y = self.y_max + (self.gap_y - rect_height) // 2
        if x < pos[0] < x + rect_width and y < pos[1] < y + rect_height:
            # check button selected
            self.selected = None
            return True
        if pos[0] <= self.gap_x or pos[0] >= self.x_max or pos[1] <= self.gap_y or pos[1] >= self.y_max:
            # player clicked outside the grid
            self.selected = None
            return False
        # get the coordinates of the selected square
        row = (pos[0] - self.gap_x) // 50
        col = (pos[1] - self.gap_y) // 50
        self.selected = [row, col]
        return False

    def check(self) -> None:
        """
        Check which numbers are in the correct position. If the number is correct then set the value that number
        and change temp to -1 so that the number cannot be changed again.
        """
        for i, j in itertools.product(range(self.row), range(self.col)):
            cur_val = self.squares[i][j].temp
            if cur_val != -1:
                # number not confirmed to be correct yet
                self.board[j][i] = cur_val
                if cur_val == self.sol_board[j][i]:
                    self.squares[i][j].value = cur_val
                    # set to -1 to indicate the number is correct
                    self.squares[i][j].temp = -1

    def is_over(self) -> bool:
        """
        Return True if the game is over and False otherwise.
        """
        if check_solution(self.board):
            return True
        return False

    def select(self, row: int, col: int) -> None:
        """
        Mark the square at row row and column col as selected.
        """
        self.reset_selected()
        self.squares[row][col].selected = True

    def reset_selected(self) -> None:
        """
        Mark all squares in the grid is not selected.
        """
        for i, j in itertools.product(range(self.row), range(self.col)):
            self.squares[i][j].selected = False


class Square:
    """A square in the Sudoku board."""

    def __init__(self, value: int, row: int, col: int, gap_x: int, gap_y: int) -> None:
        """
        Initialize the Square with a value, row, col, gap_x between the sides of the screen and where the board is,
        and gap_y between the top and bottom fo the screen and where the board is.
        """
        self.value = value
        self.row = row
        self.col = col
        self.gap_x = gap_x
        self.gap_y = gap_y
        self.temp = -1
        self.selected = False

    def draw_squares(self, screen: Surface, fnt: Font) -> None:
        """
        Draw the number in the current square on the screen using the font fnt. If the square is selected
        then shade it yellow.
        """
        text = fnt.render(str(self.value), 1, (0, 0, 0))
        x_pos = self.gap_x + 50 * self.col
        y_pos = self.gap_y + 50 * self.row

        if self.value != -1:
            # number is confirmed to be correct so draw it in black
            screen.blit(text, (x_pos + (50 - text.get_width()) / 2, y_pos + (50 - text.get_height()) / 2))
            return
        elif self.selected:
            # make the square yellow if it is selected
            pygame.draw.rect(screen, (255, 255, 204), (x_pos + 1, y_pos + 1, 48, 48))
        if self.temp != -1:
            # number not confirmed yet so draw it in blue
            text = font.render(str(self.temp), 1, (0, 0, 255))
            screen.blit(text, (x_pos + (50 - text.get_width()) / 2, y_pos + (50 - text.get_height()) / 2))
        return


def create_board() -> List[List[int]]:
    """
    Return a nested list of the 9x9 grid with 0s in every position.
    """
    grid = []
    for num in range(9):
        grid.append([0, 0, 0, 0, 0, 0, 0, 0, 0])
    return grid


def fill_board(grid: List[List[int]]) -> None:
    """
    Fill the starting grid grid going 1 row at a time.
    """
    for row in range(len(grid)):
        fill_row(row, grid)


def fill_row(row: int, grid: List[List[int]]) -> None:
    """
    Randomly add numbers in the given row row of the grid grid. If no number fits in a certain position then
    reset the entire row and try again.
    """
    numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9]
    for col in range(len(grid[row])):
        # check if a number has been set at this position and try to set one if not
        if grid[row][col] == 0 or grid[row][col] == -1:
            random.shuffle(numbers)
            for number in numbers:
                if check_conditions(grid, number, row, col):
                    # number works at this position so no need to check other numbers
                    grid[row][col] = number
                    break
    if 0 in grid[row]:
        # a number did not fit somewhere in the row so reset the entire row
        refill_row(row, grid)


def check_conditions(grid: List[List[int]], number, row, col) -> bool:
    """
    Return True if the number number can be a valid solution of the grid grid at the current row row and column col.
    Return False otherwise.
    """
    if number not in grid[row]:
        if number not in (grid[n][col] for n in range(len(grid))):
            if not check_square(row, col, number, grid):
                return True
    return False


def check_square(row: int, col: int, num: int, grid: List[List[int]]) -> bool:
    """
    Return True if num exists in the current 3x3 square in grid indicated by the current row row and column col.
    Return False otherwise.
    """
    first = col // 3 * 3
    second = first + 3
    first_range = row // 3 * 3
    second_range = first_range + 3
    square = [grid[i][first:second] for i in range(first_range, second_range)]

    if num in (square[0] + square[1] + square[2]):
        return True
    return False


def refill_row(row: int, grid: List[List[int]]) -> List[List[int]]:
    """
    Return a version of the grid grid where all the numbers in the row row are set to 0.
    """
    for n in range(9):
        grid[row][n] = 0
    fill_row(row, grid)
    return grid


def copy_grid(grid: List[List[int]]) -> List[List[int]]:
    """
    Return a copy of the current grid given by grid.
    """
    copy = create_board()
    for i in range(9):
        for j in range(9):
            copy[i][j] = grid[i][j]
    return copy


def make_starting_board(grid: List[List[int]], to_remove: int) -> None:
    """
    Remove to_remove number of numbers from grid.
    """
    while to_remove > 0:
        # pick a random row and column and if that number has not been removed then remove it
        row = random.randint(0, 8)
        col = random.randint(0, 8)
        if grid[row][col] != -1:
            # change to -1 to indicate the number has been removed
            grid[row][col] = -1
            to_remove -= 1


def check_solution(grid: List[List[int]]) -> bool:
    """
    Return True if the solution in grid is correct and False otherwise.
    """
    num_list = [1, 2, 3, 4, 5, 6, 7, 8, 9]
    for row, col in itertools.product(range(9), range(9)):
        for num in num_list:
            # check if num is in both the current row and column
            if num not in grid[row] or num not in (grid[n][col] for n in range(len(grid))):
                return False
            # check if num is in the current 3x3 square
            if not check_square(row, col, num, grid):
                return False
    return True


def format_time(seconds: float) -> str:
    """
    Return a string version of the current time given by seconds.
    """
    second = seconds % 60
    minute = seconds // 60
    hour = minute // 60

    time_to_return = str(hour) + ":" + str(minute) + ":" + str(second)
    return time_to_return


if __name__ == "__main__":
    board = create_board()
    window = pygame.display.set_mode((540, 600))
    font = pygame.font.SysFont('timesnewroman', 40)
    fill_board(board)
    copy_board = copy_grid(board)  # copy of the solution board that should not be modified as the game is played
    remove = 40  # this variable controls how many numbers get removed
    make_starting_board(board, remove)
    grids = Board(9, 9, 450, 450, board, copy_board, window)
    grids.draw_board(window, 0, font)
    # current key pressed
    key = None
    game_running = True
    # keep track of how many moves the player makes
    num_moves = 0
    start = time.time()

    while game_running:
        events = pygame.event.get()
        end = time.time()
        for event in events:
            if event.type == pygame.QUIT:
                game_running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    key = 1
                if event.key == pygame.K_2:
                    key = 2
                if event.key == pygame.K_3:
                    key = 3
                if event.key == pygame.K_4:
                    key = 4
                if event.key == pygame.K_5:
                    key = 5
                if event.key == pygame.K_6:
                    key = 6
                if event.key == pygame.K_7:
                    key = 7
                if event.key == pygame.K_8:
                    key = 8
                if event.key == pygame.K_9:
                    key = 9
                if event.key == pygame.K_BACKSPACE:
                    key = -1
            if event.type == pygame.MOUSEBUTTONDOWN:
                position = pygame.mouse.get_pos()
                # check what was pressed
                if grids.get_square(position, font):
                    grids.check()
                    # check button pushed so check if game is over
                    if grids.is_over():
                        game_running = False
                        print("Game over. You won in " + str(format_time(round(end - start))) + " and " +
                              str(num_moves) + " moves.")
                if grids.selected is not None:
                    square_to_shade = grids.selected
                    grids.select(square_to_shade[0], square_to_shade[1])
                else:
                    grids.reset_selected()
        selected = grids.selected
        if selected is not None and key is not None:
            grids.squares[selected[0]][selected[1]].temp = key
            key = None
            num_moves += 1
        else:
            key = None
        cur_time = round(end - start)
        grids.draw_board(window, cur_time, font)
        pygame.display.update()
    pygame.quit()
