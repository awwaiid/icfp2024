import math
from pathlib import Path
import sys
import time
from astar import AStar

# Append the root directory to the sys.path
# expanded_path = os.expandPath(__file__)
BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(BASE_DIR))

from icfp_client import ICFPClient


WALL_CHAR = "#"
PILL_CHAR = "."
VISITED_CHAR = "o"
PLAYER_CHAR = "L"
UP_MOVE = "U"
DOWN_MOVE = "D"
LEFT_MOVE = "L"
RIGHT_MOVE = "R"


class LambdaSolver(AStar):
    def __init__(self, board):
        self.board = board
        self.lines = board
        self.width = len(self.lines[0])
        self.height = len(self.lines)

    def heuristic_cost_estimate(self, n1, n2):
        """computes the 'direct' distance between two (x,y) tuples"""
        (x1, y1) = n1
        (x2, y2) = n2

        return math.hypot(x2 - x1, y2 - y1)

    def distance_between(self, n1, n2):
        """this method always returns 1, as two 'neighbors' are always adajcent"""
        return 1

    def neighbors(self, node):
        """for a given coordinate in the maze, returns up to 4 adjacent(north,east,south,west)
        nodes that can be reached (=any adjacent coordinate that is not a wall)
        """
        row, col = node
        board = self.board

        neighbors = [(row - 1, col), (row + 1, col), (row, col - 1), (row, col + 1)]
        valid_neighbors = [
            (nrow, ncol)
            for nrow, ncol in neighbors
            if 0 <= nrow < len(board)
            and 0 <= ncol < len(board[0])
            and board[nrow][ncol] != WALL_CHAR
        ]
        return valid_neighbors


# EXAMPLE
# python courses/lambdaman/solver.py  courses/lambdaman/lambdaman3.txt
def get_neighbors(board, position):
    row, col = position

    neighbors = [
        (row - 1, col),
        (row + 1, col),
        (row, col - 1),
        (row, col + 1),
    ]
    valid_neighbors = [
        (nrow, ncol)
        for nrow, ncol in neighbors
        if 0 <= nrow < len(board)
        and 0 <= ncol < len(board[0])
        and board[nrow][ncol] != WALL_CHAR
    ]
    return valid_neighbors


def heuristic_cost_estimate(positionA, positionB):
    return abs(positionA[0] - positionB[0]) + abs(positionA[1] - positionB[1])


def sorted_positions(positions, current):
    return positions


def a_star_pathfinding(board, start):
    solver = LambdaSolver(board)
    moves = []
    visited = set()
    last_position = start
    valid_pos = set(
        [
            (i, j)
            for i in range(len(board))
            for j in range(len(board[0]))
            if board[i][j] != WALL_CHAR
        ]
    )
    visited.add(start)
    forks = set()

    while remaining := valid_pos - visited:
        neighbors = get_neighbors(board, last_position)
        remaining_neighbors = set(neighbors) & remaining

        if len(list(remaining_neighbors)) > 1:
            next_position = sorted_positions(neighbors, last_position).pop()
            # Add all the other neighbors to the forks
            for neighbor in neighbors:
                if neighbor != next_position:
                    forks.add(neighbor)
        elif len(remaining_neighbors) == 1:
            next_position = remaining_neighbors.pop()
        # If there are no remaining neighbors, go back to the last fork
        elif forks:
            next_position = forks.pop()

            # remove all forks of the same value
            # forks = [fork for fork in forks if fork != next_position]
        else:
            next_position = remaining.pop()

        # print("Starting Astar at:", last_position, next_position)
        path = solver.astar(last_position, next_position)
        for i, step in enumerate(path):
            x1, y1 = last_position
            x2, y2 = step
            if x2 > x1:
                moves.append(DOWN_MOVE)
            elif x2 < x1:
                moves.append(UP_MOVE)
            elif y2 > y1:
                moves.append(RIGHT_MOVE)
            elif y2 < y1:
                moves.append(LEFT_MOVE)
            last_position = step
            visited.add(step)

    return [], "".join(moves)


def bfs_pathfinding(board, start):
    # List to store the moves
    moves = []

    def bfs(board, x, y, move=None):
        if move:
            moves.append(move)

        # Base cases
        if x < 0 or x >= len(board) or y < 0 or y >= len(board[0]):
            return False
        if board[x][y] == WALL_CHAR or board[x][y] == VISITED_CHAR:
            return False

        # Mark the current cell as visited
        board[x][y] = VISITED_CHAR

        # Move in all four directions
        if bfs(board, x - 1, y, UP_MOVE):
            return True  # Up
        if bfs(board, x + 1, y, DOWN_MOVE):
            return True  # Down
        if bfs(board, x, y - 1, LEFT_MOVE):
            return True  # Left
        if bfs(board, x, y + 1, RIGHT_MOVE):
            return True  # Right

        # If all directions are blocked, backtrack
        board[x][y] = PILL_CHAR
        return False

    # Start BFS from the player's initial position
    start_x, start_y = start
    bfs(board, start_x, start_y)

    # Print the moves
    # moves.reverse()  # Reverse the moves list to get the correct order

    return [], "".join(moves)


def dfs_pathfinding(board, start):
    # List to store the moves
    moves = []

    def dfs(board, x, y, move=None):
        if move:
            moves.append(move)

        # Base cases
        if x < 0 or x >= len(board) or y < 0 or y >= len(board[0]):
            return False
        if board[x][y] == WALL_CHAR or board[x][y] == VISITED_CHAR:
            return False

        # Mark the current cell as visited
        board[x][y] = VISITED_CHAR

        # Move in all four directions
        if dfs(board, x - 1, y, UP_MOVE):
            return True  # Up
        if dfs(board, x + 1, y, DOWN_MOVE):
            return True  # Down
        if dfs(board, x, y - 1, LEFT_MOVE):
            return True  # Left
        if dfs(board, x, y + 1, RIGHT_MOVE):
            return True  # Right

        # If all directions are blocked, backtrack
        board[x][y] = PILL_CHAR
        return False

    # Start DFS from the player's initial position
    start_x, start_y = start
    dfs(board, start_x, start_y)

    # Print the moves
    # moves.reverse()  # Reverse the moves list to get the correct order

    return [], "".join(moves)


def display_board(board, lambda_position, visited):
    for i, row in enumerate(board):
        for j, cell in enumerate(row):
            if (i, j) == lambda_position:
                print("L", end="")
            elif (i, j) in visited:
                print("o", end="")
            else:
                print(cell, end="")
        print()
    print()


def move_lambda(board, position, move):
    x, y = position
    if move == "U":
        new_position = (x - 1, y)
    elif move == "D":
        new_position = (x + 1, y)
    elif move == "L":
        new_position = (x, y - 1)
    elif move == "R":
        new_position = (x, y + 1)
    else:
        new_position = position

    # Wrap around if the new position is out of bounds
    rows = len(board)
    cols = len(board[0])
    if new_position[0] < 0:
        new_position = (rows - 1, new_position[1])
    elif new_position[0] >= rows:
        new_position = (0, new_position[1])
    if new_position[1] < 0:
        new_position = (new_position[0], cols - 1)
    elif new_position[1] >= cols:
        new_position = (new_position[0], 0)

    if board[new_position[0]][new_position[1]] != "#":
        return new_position
    return position


def simulate_moves(board, moves):
    # Find the initial position of Lambda-Man
    visited = set()
    lambda_position = None
    for i, row in enumerate(board):
        for j, cell in enumerate(row):
            if cell == "L":
                lambda_position = (i, j)
                break
        if lambda_position:
            break

    # Remove the initial 'L' from the board for accurate display
    board[lambda_position[0]][lambda_position[1]] = "."

    # Display the initial board
    display_board(board, lambda_position, {})
    visited.add(lambda_position)

    time.sleep(1)
    clear_display()
    # Simulate each move
    for move in moves:
        lambda_position = move_lambda(board, lambda_position, move)
        visited.add(lambda_position)
        display_board(board, lambda_position, visited)
        time.sleep(0.01)
        # Clear the display
        clear_display()


def clear_display():
    print("\033c", end="")


if __name__ == "__main__":
    # take in a file path as input
    # read the file, treating each line as a row in the board
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("file_path", type=str)

    parser.add_argument("--display", action="store_true")
    parser.add_argument("--submit", action="store_true")

    args = parser.parse_args()

    file_path = args.file_path

    with open(file_path) as f:
        board = f.readlines()
        board = [list(row.strip()) for row in board]

    # Find the initial position of Lambda-Man
    start = None
    for i, row in enumerate(board):
        for j, cell in enumerate(row):
            if cell == PLAYER_CHAR:
                start = (i, j)
                break
        if start:
            break

    # Find the path using A* algorithm
    # path, moves = dfs_pathfinding(board, start)
    path, moves = a_star_pathfinding(board, start)
    # path, moves = bfs_pathfinding(board, start)

    if args.display:
        display_board(board, start, {})
        simulate_moves(board, moves)
    else:
        print(f"Path length: {len(path)}")
        print(f"Moves: {moves}")

    if args.submit:
        client = ICFPClient()

        # grep the number from the file name

        file_name = Path(file_path).name
        # remove lambdaman if present and .txt
        file_name = file_name.replace("lambdaman", "").replace(".txt", "")
        number = int(file_name)
        print("Number:", number)
        response, decoded = client.call(f"solve lambdaman{number} {moves}")

        print(f"Response: {decoded}")
