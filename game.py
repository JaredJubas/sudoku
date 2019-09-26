import itertools
import random
import pygame
import time
from typing import List
pygame.font.init()


class Board:
    def __init__(self, row, col, width, height, grid, solution_board, screen):
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

    def add_text(self, screen, current_time, fnt):
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

    def draw_board(self, screen, current_time, fnt):
        window.fill((255, 255, 255))
        black = (0, 0, 0)
        self.add_text(screen, current_time, fnt)
        n = 0
        while n < 10:
            if n % 3 == 0:
                thickness = 3
            else:
                thickness = 1
            pygame.draw.line(screen, black, (self.gap_x, self.gap_y + n * 50), (self.x_max, self.gap_y + n * 50),
                             thickness)
            pygame.draw.line(screen, black, (self.gap_x + n * 50, self.gap_y), (self.gap_x + n * 50, self.y_max),
                             thickness)
            n += 1
        for i, j in itertools.product(range(self.row), range(self.col)):
            self.squares[i][j].draw_squares(screen, fnt)
        pygame.display.update()

    def select(self, row, col):
        self.reset_selected()
        self.squares[row][col].selected = True

    def reset_selected(self):
        for i, j in itertools.product(range(self.row), range(self.col)):
            self.squares[i][j].selected = False

    def get_square(self, pos, fnt):
        text = fnt.render("Check", 1, (0, 0, 0))
        rect_width = text.get_width() + 20
        rect_height = text.get_height() + 10
        x = self.gap_x + (50 * 3 - rect_width) // 2
        y = self.y_max + (self.gap_y - rect_height) // 2
        if x < pos[0] < x + rect_width and y < pos[1] < y + rect_height:
            self.selected = None
            return True
        if pos[0] <= self.gap_x or pos[0] >= self.x_max or pos[1] <= self.gap_y or pos[1] >= self.y_max:
            self.selected = None
            return
        row = (pos[0] - self.gap_x) // 50
        col = (pos[1] - self.gap_y) // 50
        self.selected = [row, col]

    def check(self):
        for i, j in itertools.product(range(self.row), range(self.col)):
            cur_val = self.squares[i][j].temp
            if cur_val != -1:
                self.board[j][i] = cur_val
                if cur_val == self.sol_board[j][i]:
                    self.squares[i][j].value = cur_val
                    self.squares[i][j].temp = -1

    def is_over(self):
        if check_solution(self.board):
            return True
        return False


class Square:
    def __init__(self, value, row, col, gap_x, gap_y):
        self.value = value
        self.row = row
        self.col = col
        self.gap_x = gap_x
        self.gap_y = gap_y
        self.temp = -1
        self.selected = False

    def draw_squares(self, screen, fnt):
        text = fnt.render(str(self.value), 1, (0, 0, 0))
        x_pos = self.gap_x + 50 * self.col
        y_pos = self.gap_y + 50 * self.row

        if self.value != -1:
            screen.blit(text, (x_pos + (50 - text.get_width()) / 2, y_pos + (50 - text.get_height()) / 2))
            return
        elif self.selected:
            pygame.draw.rect(screen, (255, 255, 204), (x_pos + 1, y_pos + 1, 48, 48))
        if self.temp != -1:
            text = font.render(str(self.temp), 1, (0, 0, 255))
            screen.blit(text, (x_pos + (50 - text.get_width()) / 2, y_pos + (50 - text.get_height()) / 2))


def check_full(grid: List[List[int]]) -> bool:
    for row, col in itertools.product(range(9), range(9)):
        if grid[row][col] == 0 or grid[row][col] == -1:
            return False
    return True


def check_solution(grid: List[List[int]]) -> bool:
    num_list = [1, 2, 3, 4, 5, 6, 7, 8, 9]
    for row, col in itertools.product(range(9), range(9)):
        for num in num_list:
            if num not in grid[row] or num not in (grid[n][col] for n in range(len(grid))):
                return False
            if not check_square(row, col, num, grid):
                return False
    return True


def check_square(row: int, col: int, num: int, grid: List[List[int]]) -> bool:
    first = col // 3 * 3
    second = first + 3
    first_range = row // 3 * 3
    second_range = first_range + 3
    square = [grid[i][first:second] for i in range(first_range, second_range)]

    if num in (square[0] + square[1] + square[2]):
        return True
    return False


def check_conditions(grid: List[List[int]], number, row, col) -> bool:
    if number not in grid[row]:
        if number not in (grid[n][col] for n in range(len(grid))):
            if not check_square(row, col, number, grid):
                return True
    return False


def refill_row(row: int, grid: List[List[int]]) -> List[List[int]]:
    for n in range(9):
        grid[row][n] = 0
    fill_row(row, grid)
    return grid


def fill_row(row: int, grid: List[List[int]]) -> None:
    numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9]
    for col in range(len(grid[row])):
        if grid[row][col] == 0 or grid[row][col] == -1:
            random.shuffle(numbers)
            for number in numbers:
                if check_conditions(grid, number, row, col):
                    grid[row][col] = number
                    break
    if 0 in grid[row]:
        refill_row(row, grid)


def fill_board(grid: List[List[int]]) -> None:
    for row in range(len(grid)):
        fill_row(row, grid)


def create_board() -> List[List[int]]:
    grid = []
    for num in range(9):
        grid.append([0, 0, 0, 0, 0, 0, 0, 0, 0])
    return grid


def make_starting_board(grid: List[List[int]]) -> None:
    to_remove = 40
    while to_remove > 0:
        row = random.randint(0, 8)
        col = random.randint(0, 8)
        if grid[row][col] != -1:
            grid[row][col] = -1
            to_remove -= 1


def copy_grid(grid: List[List[int]]) -> List[List[int]]:
    copy = create_board()
    for i in range(9):
        for j in range(9):
            copy[i][j] = grid[i][j]
    return copy


def format_time(seconds):
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
    copy_board = copy_grid(board)
    print(board)
    make_starting_board(board)
    grids = Board(9, 9, 450, 450, board, copy_board, window)
    grids.draw_board(window, 0, font)
    key = None
    game_running = True
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
                if grids.get_square(position, font):
                    grids.check()
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
