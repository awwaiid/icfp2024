import heapq

WALL_CHAR = '#'
PILL_CHAR = '.'

UP_MOVE = 'U'
DOWN_MOVE = 'D'
LEFT_MOVE = 'L'
RIGHT_MOVE = 'R'


def a_star_pathfinding(board, start):
    def heuristic(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def get_neighbors(position):
        x, y = position
        neighbors = [(x - 1, y, UP_MOVE), (x + 1, y, DOWN_MOVE), (x, y - 1, LEFT_MOVE), (x, y + 1, RIGHT_MOVE)]
        valid_neighbors = [
            (nx, ny, move) for nx, ny, move in neighbors
            if 0 <= nx < len(board) and 0 <= ny < len(board[0]) and board[nx][ny] != WALL_CHAR
        ]
        return valid_neighbors

    start = tuple(start)
    open_set = []
    heapq.heappush(open_set, (0, start))
    came_from = {}
    g_score = {start: 0}
    f_score = {start: heuristic(start, start)}
    visited = set()

    while open_set:
        current = heapq.heappop(open_set)[1]
        visited.add(current)

        for neighbor in get_neighbors(current):
            nx, ny, move = neighbor
            tentative_g_score = g_score[current] + 1

            if (nx, ny) in visited:
                continue

            if tentative_g_score < g_score.get((nx, ny), float('inf')):
                came_from[(nx, ny)] = (current, move)
                g_score[(nx, ny)] = tentative_g_score
                f_score[(nx, ny)] = tentative_g_score + heuristic((nx, ny), (nx, ny))
                heapq.heappush(open_set, (f_score[(nx, ny)], (nx, ny)))

    path = []
    moves = []
    current = start
    while current in came_from:
        path.append(current)
        current, move = came_from[current]
        moves.append(move)

    path.reverse()
    moves.reverse()
    return path, ''.join(moves)

def display_path_on_board(board, path):
    board_copy = [row[:] for row in board]
    for x, y in path:
        if board_copy[x][y] == '.':
            board_copy[x][y] = 'o'

    for row in board_copy:
        print(''.join(row))
    print()

if __name__ == "__main__":

    # take in a file path as input
    # read the file, treating each line as a row in the board
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("file_path", type=str)

    args = parser.parse_args()

    file_path = args.file_path

    with open(file_path) as f:
        board = f.readlines()
        board = [list(row.strip()) for row in board]

    # Find the initial position of Lambda-Man
    start = None
    for i, row in enumerate(board):
        for j, cell in enumerate(row):
            if cell == 'L':
                start = (i, j)
                break
        if start:
            break

    # Find the path using A* algorithm
    path, moves = a_star_pathfinding(board, start)

    # Display the path on the board
    display_path_on_board(board, path)

    print(f"Path length: {len(path)}")
    print(f"Moves: {moves}")
