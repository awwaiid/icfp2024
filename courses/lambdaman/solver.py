from functools import cached_property
import heapq
import math
from pathlib import Path
import random
import curses
import time
import sys
import time
from astar import AStar

# Append the root directory to the sys.path
# expanded_path = os.expandPath(__file__)
BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(BASE_DIR))

from icfp_client import ICFPClient


class bcolors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


WALL_CHAR = "#"
PILL_CHAR = "."
VISITED_CHAR = "o"
PLAYER_CHAR = "L"
UP_MOVE = "U"
DOWN_MOVE = "D"
LEFT_MOVE = "L"
RIGHT_MOVE = "R"


class Board:
    def __init__(self, board, start_position, number=0):
        self.board = board
        self.width = len(board[0])
        self.height = len(board)
        self.number = number

        self.recompute()
        self.start_position = self.node_at(start_position)
        self.current_pos = self.start_position
        self.visited = set()
        self.visited.add(start_position)
        self.moves = []

    def node_at(self, position):
        if position not in self._board:
            return Node(WALL_CHAR, position, self)
        return self._board[position]

    def get_nodes(self):
        return self._board.values()

    def remaining(self):
        return set(self._board.keys()) - self.visited

    def remaining_nodes(self) -> set["Node"]:
        return {
            self.node_at(position)
            for position in self.remaining()
            if self.node_at(position).valid()
        }

    def move(self, direction):
        if direction == UP_MOVE:
            new_position = (
                self.current_pos.position[0] - 1,
                self.current_pos.position[1],
            )
        elif direction == DOWN_MOVE:
            new_position = (
                self.current_pos.position[0] + 1,
                self.current_pos.position[1],
            )
        elif direction == LEFT_MOVE:
            new_position = (
                self.current_pos.position[0],
                self.current_pos.position[1] - 1,
            )
        elif direction == RIGHT_MOVE:
            new_position = (
                self.current_pos.position[0],
                self.current_pos.position[1] + 1,
            )
        else:
            return False

        if self.node_at(new_position).valid():
            self.current_pos = self.node_at(new_position)
            self.visited.add(self.current_pos.position)
            self.moves.append(direction)
            return True

        return False

    def recompute(self):
        self._board = {
            (i, j): Node(self.board[i][j], (i, j), self)
            for i in range(self.height)
            for j in range(self.width)
        }

    def visited_nodes(self):
        return {self.node_at(position) for position in self.visited}

    def __len__(self):
        return len(self.board)

    def display(self):
        for i in range(self.height):
            for j in range(self.width):
                self.node_at((i, j)).display()
            print()
        print("Number:", self.number)
        print("Moves:", "".join(self.moves))
        print("Remaining nodes:", len(self.remaining_nodes()))

    def __repr__(self):
        return f"Board(#{self.number} {self.height}, {self.width})"

    def submit(self):
        client = ICFPClient()

        # grep the number from the file name
        moves = "".join(self.moves)
        response, decoded = client.call(f"solve lambdaman{self.number} {moves}")

        print(f"Response: {decoded}")


class Node:
    def __init__(
        self,
        char: str,
        position: tuple[int, int],
        board: Board,
    ):
        self.char = char
        self.position = position
        self.board = board

    def __eq__(self, other):
        if isinstance(other, Node):
            return self.position == other.position
        if isinstance(other, tuple) and len(other) == 2:
            return self.position == other
        return False

    def __hash__(self):
        return hash(self.position)

    def __repr__(self):
        return f"Node({self.position}, {self.char})"

    def valid(self):
        row, col = self.position
        return (
            self.char != WALL_CHAR
            and row >= 0
            and col >= 0
            and row < self.board.height
            and col < self.board.width
        )

    def visited(self):
        return self.board.visited(self.position)

    @cached_property
    def adjacent(self):
        row, col = self.position
        neighbors = [
            (row - 1, col),
            (row + 1, col),
            (row, col - 1),
            (row, col + 1),
        ]
        nodes = [self.board.node_at(neighbor) for neighbor in neighbors]
        valid_neighbors = [node for node in nodes if node.valid()]
        return valid_neighbors

    def to_position(self, node):
        return node.position

    def display(self):
        if self.position == self.board.current_pos.position:
            print(f"{bcolors.OKGREEN}{PLAYER_CHAR}{bcolors.ENDC}", end="")
        elif self.position in self.board.visited:
            print(VISITED_CHAR, end="")
        elif self.char == WALL_CHAR:
            print(f"{bcolors.WARNING}{WALL_CHAR}{bcolors.ENDC}", end="")
        else:
            print(self.char, end="")


class LambdaSolver(AStar):
    def __init__(self, board: Board):
        self.board = board
        self.lines = board.board
        self.width = board.width
        self.height = board.height

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
        return [n.position for n in self.board.node_at(node).adjacent]


def heuristic_cost_estimate(positionA, positionB):
    return abs(positionA[0] - positionB[0]) + abs(positionA[1] - positionB[1])


def dijkstra_algorithm(board: Board, start_node):
    unvisited_nodes = list(board.get_nodes())

    # We'll use this dict to save the cost of visiting each node and update it as we move along the graph
    shortest_path = {}

    # We'll use this dict to save the shortest known path to a node found so far
    previous_nodes = {}

    # We'll use max_value to initialize the "infinity" value of the unvisited nodes
    max_value = sys.maxsize
    for node in unvisited_nodes:
        shortest_path[node] = max_value
    # However, we initialize the starting node's value with 0
    shortest_path[start_node] = 0

    # The algorithm executes until we visit all nodes
    while unvisited_nodes:
        # The code block below finds the node with the lowest score
        current_min_node = None
        for node in unvisited_nodes:  # Iterate over the nodes
            if current_min_node is None:
                current_min_node = node
            elif shortest_path[node] < shortest_path[current_min_node]:
                current_min_node = node

        # The code block below retrieves the current node's neighbors and updates their distances
        neighbors = current_min_node.adjacent
        for neighbor in neighbors:
            tentative_value = shortest_path[current_min_node] + 1
            if tentative_value < shortest_path[neighbor]:
                shortest_path[neighbor] = tentative_value
                # We also update the best path to the current node
                previous_nodes[neighbor] = current_min_node

        # After visiting its neighbors, we mark the node as "visited"
        unvisited_nodes.remove(current_min_node)

    return previous_nodes, shortest_path


def a_star_pathfinding(board):
    solver = LambdaSolver(board)
    forks = []
    last_position = board.current_pos
    while len(board.remaining_nodes()) > 0:
        neighbors = board.current_pos.adjacent
        remaining_neighbors = set(neighbors) & board.remaining_nodes()
        action = None
        if len(list(remaining_neighbors)) > 1:
            action = "fork_found"
            next_position = random.choice(list(remaining_neighbors))
            # Add all the other neighbors to the forks
            for neighbor in remaining_neighbors:
                if neighbor != next_position:
                    forks.append(neighbor)

                    # ensure forks are unique
                    forks = list(set(forks))
        elif len(remaining_neighbors) == 1:
            action = "1_neighbor"
            next_position = remaining_neighbors.pop()

        # If there are no remaining neighbors, go back to the last fork
        elif forks:
            action = "backtrack"
            # find the most recent fork, that has not been visited

            next_position = None
            for fork in reversed(forks):
                if fork in board.remaining_nodes():
                    next_position = fork
                    break

        if not next_position:
            action = "no_neighbors"

            # unvisited = dijkstra_algorithm(board, last_position)
            # if unvisited:
            #     import ipdb

            #     ipdb.set_trace()

            #     unvisited[0]
            #     print(
            #         f"Closest unvisited node is at {next_position} with a distance of {distance}"
            #     )
            # else:
            #     print("No more unvisited nodes")
            next_position = random.choice(list(board.remaining_nodes()))

        print("Starting Astar at:", action, last_position, next_position)

        path = solver.astar(last_position.position, next_position.position)

        for i, step in enumerate(path):
            x1, y1 = last_position.position
            x2, y2 = step
            if x2 > x1:
                board.move(DOWN_MOVE)
            elif x2 < x1:
                board.move(UP_MOVE)
            elif y2 > y1:
                board.move(RIGHT_MOVE)
            elif y2 < y1:
                board.move(LEFT_MOVE)
            last_position = board.current_pos

    return [], "".join(board.moves)


def simulate_moves(board, moves, stdscr=None):
    # Find the initial position of Lambda-Man
    board.display()
    time.sleep(1)
    clear_display(stdscr)
    # Simulate each move
    for move in moves:
        board.move(move)
        board.display()
        time.sleep(0.02)
        clear_display(stdscr)


def clear_display(stdscr=None):
    print("\033c", end="")


def main():
    # take in a file path as input
    # read the file, treating each line as a row in the board
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("file_path", type=str)

    parser.add_argument("--display", action="store_true")
    parser.add_argument("--submit", action="store_true")
    parser.add_argument("--repl", action="store_true")

    args = parser.parse_args()

    file_path = args.file_path
    file_name = Path(file_path).name
    # remove lambdaman if present and .txt
    file_name = file_name.replace("lambdaman", "").replace(".txt", "")
    number = int(file_name)

    with open(file_path) as f:
        board = f.readlines()
        board_strings = [list(row.strip()) for row in board]

    # Find the initial position of Lambda-Man
    start = None
    for i, row in enumerate(board_strings):
        for j, cell in enumerate(row):
            if cell == PLAYER_CHAR:
                start = (i, j)

                break
        if start:
            break

    # Find the path using A* algorithm

    board = Board(board_strings, start_position=start, number=number)

    if args.repl:
        move = None
        while True:
            board.display()
            move = input("Enter move: ")
            if move == "exit":
                break
            if move == "submit":
                break
            board.move(move.upper())
            clear_display()

        if move == "submit":
            board.submit()

        board.display()
        print("Moves:", "".join(board.moves))
        return

    path, moves = a_star_pathfinding(board)

    if args.display:
        board = Board(board_strings, start_position=start, number=number)

        simulate_moves(board, moves)
    else:
        print(f"Path length: {len(path)}")
        print(f"Moves: {moves}")

    if args.submit:
        board.submit()


if __name__ == "__main__":
    main()
