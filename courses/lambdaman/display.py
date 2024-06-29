import time


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


def simulate_moves(board, moves, repl=False):
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

    # Simulate each move

    if repl:
        moves = ""
        move = ""
        while move != "exit":
            move = input("Enter moves: ")
            moves += move
            lambda_position = move_lambda(board, lambda_position, move)
            visited.add(lambda_position)
            display_board(board, lambda_position, visited)
        print(moves)
        return
    clear_display()
    for move in moves:
        lambda_position = move_lambda(board, lambda_position, move)
        visited.add(lambda_position)
        display_board(board, lambda_position, visited)
        time.sleep(1)
        # Clear the display
        clear_display()


def clear_display():
    # Use appropriate method to clear the display based on your environment
    # For example, in a terminal, you can use:
    print("\033c", end="")
    # In Jupyter Notebook, you can use:
    # from IPython.display import clear_output
    # clear_output(wait=True)


if __name__ == "__main__":
    # take in a file path as input
    # read the file, treating each line as a row in the board
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("file_path", type=str)
    # parser.add_argument("moves", type=str, default="")
    parser.add_argument("--repl", action="store_true")

    args = parser.parse_args()

    file_path = args.file_path
    # moves = args.moves

    with open(file_path) as f:
        board = f.readlines()
        board = [list(row.strip()) for row in board]

    # Simulate the moves
    if args.repl:
        simulate_moves(board, "", repl=True)

    else:
        pass
        # simulate_moves(board, moves)
