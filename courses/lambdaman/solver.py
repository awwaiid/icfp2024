from functools import cached_property
import heapq
import math
from pathlib import Path

import time
import sys
from astar import AStar


# Append the root directory to the sys.path
# expanded_path = os.expandPath(__file__)
BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(BASE_DIR))

from client import Client as ICFPClient

sys.setrecursionlimit(1000)

DISPLAY_SPEED = 0.05


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
    def __init__(self, board, start_position, number=0, display=False):
        self.board = board
        self.width = len(board[0])
        self.height = len(board)
        self.number = number
        self.graph = {}
        self.recompute()
        self.start_position = self.node_at(start_position)
        self.current_pos = self.start_position
        self.visited = set()
        self.visited.add(start_position)
        self.moves = []
        self.wall_positions = set(
            (i, j)
            for i in range(self.height)
            for j in range(self.width)
            if self.board[i][j] == WALL_CHAR
        )
        self.display_moves = display

    def add_edge(self, node1, node2, weight):
        if node1 not in self.graph:  # Check if the node is already added
            self.graph[node1] = {}  # If not, create the node
        self.graph[node1][node2] = weight  # Else, add a connection to its neighbor

    def node_at(self, position):
        return self._board.get(position)

    @cached_property
    def get_nodes(self):
        return self._board.values()

    def remaining(self):
        return set(self._board.keys()) - self.visited - self.wall_positions

    def remaining_nodes(self) -> set["Node"]:
        return {self.node_at(position) for position in self.remaining()}

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

        node = self.node_at(new_position)
        if node and node.valid:
            self.current_pos = self.node_at(new_position)
            self.visited.add(self.current_pos.position)
            node.visits += 1
            self.moves.append(direction)
            return True

        return False

    def move_to_node(self, node):
        if node.position == self.current_pos.position:
            return True

        if node in self.current_pos.adjacent:
            return self.move_to_node_adjacent(node)

        return self.move_to_node_with_astar(node)

    def move_to_node_adjacent(self, node):
        if node.position == self.current_pos.position:
            return True
        x1, y1 = self.current_pos.position
        x2, y2 = node.position
        if x2 > x1:
            self.move(DOWN_MOVE)
        elif x2 < x1:
            self.move(UP_MOVE)
        elif y2 > y1:
            self.move(RIGHT_MOVE)
        elif y2 < y1:
            self.move(LEFT_MOVE)

            if self.display_moves:
                clear_display()
                self.display()
                # time.sleep(DISPLAY_SPEED)

    def move_to_node_with_astar(self, node):
        solver = LambdaSolver(self)
        path = solver.astar(self.current_pos.position, node.position)
        for i, step in enumerate(path):
            x1, y1 = self.current_pos.position
            x2, y2 = step
            if x2 > x1:
                self.move(DOWN_MOVE)
            elif x2 < x1:
                self.move(UP_MOVE)
            elif y2 > y1:
                self.move(RIGHT_MOVE)
            elif y2 < y1:
                self.move(LEFT_MOVE)

            if self.display_moves:
                clear_display()
                self.display()
                time.sleep(DISPLAY_SPEED)
        return True

    def recompute(self):
        self._board = {
            (i, j): Node(self.board[i][j], (i, j), self)
            for i in range(self.height)
            for j in range(self.width)
        }

        for i in range(self.height):
            for j in range(self.width):
                node = self.node_at((i, j))
                if node.valid:
                    for neighbor in node.adjacent:
                        self.add_edge(node, neighbor, 1)

    def shortest_distances(self, source: str):
        # Initialize the values of all nodes with infinity
        distances = {node: float("inf") for node in self.graph}
        distances[source] = 0  # Set the source value to 0

        # Initialize a priority queue
        pq = [(0, source)]
        heapq.heapify(pq)

        # Create a set to hold visited nodes
        visited = set()

        while pq:  # While the priority queue isn't empty
            current_distance, current_node = heapq.heappop(pq)

            if current_node in visited:
                continue
            visited.add(current_node)

            for neighbor, weight in self.graph[current_node].items():
                # Calculate the distance from current_node to the neighbor
                tentative_distance = current_distance + weight
                if tentative_distance < distances[neighbor]:
                    distances[neighbor] = tentative_distance
                    heapq.heappush(pq, (tentative_distance, neighbor))

        predecessors = {node: None for node in self.graph}

        for node, distance in distances.items():
            for neighbor, weight in self.graph[node].items():
                if distances[neighbor] == distance + weight:
                    predecessors[neighbor] = node

        return distances, predecessors

    def nearest_unvisited(self, source: str) -> tuple["Node", int]:
        distances, pre = source.costs
        unvisited = self.remaining()
        nearest = min(unvisited, key=lambda node: distances[node])
        return nearest, distances[nearest], (distances, pre)

    def count_branchs(self, source: str, count=0):
        visited = set([source])

        def dfs(node):
            nonlocal count
            visited.add(node)
            for neighbor in node.adjacent:
                if neighbor not in visited:
                    count += 1
                    dfs(neighbor)

        dfs(source)
        return count

    def next_optimal_node_by_branch(self, source: "Node") -> tuple["Node", int, tuple]:
        neighbors = source.adjacent

        best_node = None
        for neighbor in neighbors:
            if best_node is None:
                best_node = neighbor
                continue

            if neighbor.total_branch_count() < best_node.total_branch_count():
                best_node = neighbor

        return best_node, best_node.total_cost, best_node.costs

    @cached_property
    def start_costs(self):
        return self.start_position.costs

    @cached_property
    def max_costs(self):
        shortest_distances, _ = self.start_costs

        inverted_distances = max(shortest_distances, key=shortest_distances.get)

        print("Inverted Distances", inverted_distances)
        return inverted_distances.costs

    def next_optimal_node(self, source: "Node") -> tuple["Node", int, tuple]:
        current_costs, _ = source.costs

        # fine the node that is the highest distance
        # from the current node

        inverted_distances, pre = self.max_costs

        # distances, pre = source.costs
        unvisited = self.remaining()
        nearest = max(
            unvisited,
            key=lambda node: current_costs[node] / (inverted_distances[node] or 1),
        )
        return nearest, inverted_distances[nearest], (inverted_distances, pre)

    def shortest_path(
        self, source: str, target: str, distances=None, predecessors=None
    ):
        # Generate the predecessors dict
        if distances is None or predecessors is None:
            distances, predecessors = source.costs
        else:
            distances = distances
            predecessors = predecessors

        path = []
        current_node = target

        # Backtrack from the target node using predecessors
        while current_node:
            path.append(current_node)
            current_node = predecessors[current_node]

        # Reverse the path and return it
        path.reverse()

        return path

    def __len__(self):
        return len(self.board)

    def display(self):
        for i in range(self.height):
            for j in range(self.width):
                print(self.node_at((i, j)).display(), end="")
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

    def next_move(self):
        current = self.current_pos
        neighbors = current.adjacent
        remaining_neighbors = set(neighbors) & self.remaining_nodes()
        # action = None
        next_position = None
        if len(list(remaining_neighbors)) > 1:
            # action = "fork_found"
            next_position = self.next_optimal_node(current)[0]

        elif len(remaining_neighbors) == 1:
            # action = "1_neighbor"
            next_position = remaining_neighbors.pop()

        if not next_position:
            # action = "no_optimal"
            next_position = self.nearest_unvisited(current)[0]
        if current.position == next_position:
            # action = "no_neighbors"

            next_position = self.nearest_unvisited(current)[0]
        if not next_position:
            # action = "no_next"
            exit(0)

        # print(f"Action: {action}", next_position)
        if type(next_position) == tuple:
            next_position = self.node_at(next_position)

        return next_position

    def determine_via_shortest_dist_tsp_path(self):
        shortest_distances, _ = self.current_pos.costs

        # fine the node that is the highest distance
        # from the current node

        inverted_distances, _ = max(
            shortest_distances, key=shortest_distances.get
        ).costs

        # sort the remaining nodes by the shortest distance

        tsp_graph = {}
        path = []
        # Build a graph where all nodes are connected to the start node
        for node in self.remaining_nodes():
            tsp_graph[node] = shortest_distances[node] / (inverted_distances[node] or 1)

        # Preform a Travelling Salesman Problem
        # Find the minimum path that visits all the nodes
        # Find the nearest node to the start node
        current = self.current_pos
        # Local TSP graph limit
        LIMIT = 15
        while len(tsp_graph) > 0 and len(path) < LIMIT:
            nearest = min(tsp_graph, key=tsp_graph.get)
            path.append((nearest, tsp_graph[nearest]))
            del tsp_graph[nearest]
            current = nearest
            for node in tsp_graph:
                if node == current:
                    continue
                tsp_graph[node] = min(
                    tsp_graph[node],
                    shortest_distances[current]
                    + shortest_distances[node]
                    - shortest_distances[current],
                )

        return path

    def solve(self):
        path = self.determine_via_shortest_dist_tsp_path()

        while len(self.remaining_nodes()) > 0:
            # Remove the first node from the path
            step, dist = path.pop(0)
            print(f"Step {len(self.moves)}:", step, dist)
            if step in self.visited:
                continue
            self.move_to_node(step)

            # Recalculate the path
            path = self.determine_via_shortest_dist_tsp_path()

    # def solve(self):
    #     while len(self.remaining_nodes()) > 0:
    #         next_position = self.next_move()
    #         self.move_to_node(next_position)


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

        self.display()

        self.visits = 0

    def __eq__(self, other):
        if isinstance(other, Node):
            return self.position == other.position
        if isinstance(other, tuple) and len(other) == 2:
            return self.position == other
        return False

    def __hash__(self):
        return hash(self.position)

    def __repr__(self):
        return f"N({self.position}, v{self.visits} {self.total_cost}) "

    def __lt__(self, other):
        return self.position < other.position

    def __gt__(self, other):
        return self.position > other.position

    def __le__(self, other):
        return self.position <= other.position

    def __ge__(self, other):
        return self.position >= other.position

    def total_branch_count(self):
        return self.board.count_branchs(self)

    @cached_property
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
    def raw_costs(self):
        return self.board.shortest_distances(self)

    @property
    def costs(self):
        """Return the shortest distances and predecessors from this node to all other nodes in the graph BUT adds weight to previously visited nodes"""
        distances, predecessors = self.raw_costs
        for node in self.board.visited:
            distances[node] += self.board.node_at(node).visits
        return distances, predecessors

    @property
    def total_cost(self):
        return sum(self.costs[0].values())

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
        valid_neighbors = [node for node in nodes if node is not None and node.valid]
        return valid_neighbors

    @cached_property
    def to_position(self, node):
        return node.position

    def display(self):
        if (
            self.board
            and hasattr(self.board, "current_pos")
            and self.position == self.board.current_pos.position
        ):
            return f"{bcolors.OKGREEN}{PLAYER_CHAR}{bcolors.ENDC}"
        elif hasattr(self.board, "visited") and self.position in self.board.visited:
            return VISITED_CHAR
        elif self.char == WALL_CHAR:
            return f"{bcolors.WARNING}{WALL_CHAR}{bcolors.ENDC}"
        else:
            return self.char


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


def dijkstra_pathfinding(board: Board):
    # Find the initial

    while len(board.remaining_nodes()) > 0:
        # Find the nearest unvisited node
        node, distance, shortest_distances = board.next_optimal_node(board.current_pos)[
            0
        ]
        path = board.shortest_path(
            board.current_pos,
            node,
            distances=shortest_distances[0],
            predecessors=shortest_distances[1],
        )
        for i, step in enumerate(path):
            x1, y1 = board.current_pos.position

            x2, y2 = board.node_at(step).position
            if x2 > x1:
                board.move(DOWN_MOVE)
            elif x2 < x1:
                board.move(UP_MOVE)
            elif y2 > y1:
                board.move(RIGHT_MOVE)
            elif y2 < y1:
                board.move(LEFT_MOVE)

    return [], "".join(board.moves)


def a_star_pathfinding(board):
    while len(board.remaining_nodes()) > 0:
        current = board.current_pos
        neighbors = current.adjacent
        remaining_neighbors = set(neighbors) & board.remaining_nodes()
        # action = None
        if len(list(remaining_neighbors)) > 1:
            action = "fork_found"
            next_position = board.next_optimal_node(current)[0]

        elif len(remaining_neighbors) == 1:
            action = "1_neighbor"
            next_position = remaining_neighbors.pop()

        if current.position == next_position:
            action = "no_neighbors"

            next_position = board.nearest_unvisited(current)[0]

        if not next_position:
            action = "no_optimal"
            next_position = board.nearest_unvisited(current)[0]

        if not next_position:
            action = "no_next"

            exit(0)

        if board.current_pos.position == next_position:
            continue

        print(f"Action: {action}", next_position)
        if type(next_position) == tuple:
            next_position = board.node_at(next_position)
        board.move_to_node(next_position)

    return [], "".join(board.moves)


def clear_display(stdscr=None):
    print("\033c", end="")


def main(stdscr=None):
    # take in a file path as input
    # read the file, treating each line as a row in the board
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("file_path", type=str)

    parser.add_argument("--display", action="store_true")
    parser.add_argument("--submit", action="store_true")
    parser.add_argument("--repl", action="store_true")
    parser.add_argument("--graph", action="store_true")

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

    board = Board(
        board_strings, start_position=start, number=number, display=args.display
    )

    if args.graph:
        from graphviz import Digraph

        def generate_graphviz(graph):
            dot = Digraph()

            for node, edges in graph.items():
                for neighbor, weight in edges.items():
                    dot.edge(str(node), str(neighbor), label=str(weight))

            return dot.source

        dot = generate_graphviz(board.graph)
        print(dot)
        exit(0)

    if args.repl:
        import sys
        import termios
        import tty

        def get_key():
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setraw(fd)
                ch1 = sys.stdin.read(1)
                if ch1 == "\x1b":
                    ch2 = sys.stdin.read(1)
                    if ch2 == "[":
                        ch3 = sys.stdin.read(1)
                        return ch1 + ch2 + ch3
                    else:
                        return ch1 + ch2
                else:
                    return ch1
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

        move = None
        while True:
            board.display()
            print("Possible Moves")
            for node in board.current_pos.adjacent:
                x1, y1 = board.current_pos.position
                x2, y2 = node.position
                if node == board.next_move():
                    print(bcolors.OKGREEN)

                if x2 > x1:
                    print("Down", node)
                elif x2 < x1:
                    print("Up", node)
                elif y2 > y1:
                    print("Right", node)
                elif y2 < y1:
                    print("Left", node)

                print(bcolors.ENDC)

            key = get_key()

            if key == "\x1b[A":  # Up arrow
                move = "U"
            elif key == "\x1b[B":  # Down arrow
                move = "D"
            elif key == "\x1b[C":  # Right arrow
                move = "R"
            elif key == "\x1b[D":  # Left arrow
                move = "L"
            elif key == "a":  # auto
                board.display_moves = True
                board.solve()
                key = get_key()

            if key == "q":  # Exit on 'q'
                break

            if key == "s":
                board.submit()
                print("Moves:", "".join(board.moves))
                exit
            if move:
                board.move(move.upper())
            clear_display()

        board.display()
        print("Moves:", "".join(board.moves))
        return

    board.solve()

    if args.submit:
        board.submit()


if __name__ == "__main__":
    main()
