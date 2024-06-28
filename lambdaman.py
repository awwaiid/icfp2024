def display_board(board, lambda_position):
    for i, row in enumerate(board):
        for j, cell in enumerate(row):
            if (i, j) == lambda_position:
                print('L', end='')
            else:
                print(cell, end='')
        print()
    print()

def move_lambda(board, position, move):
    x, y = position
    if move == 'U':
        new_position = (x - 1, y)
    elif move == 'D':
        new_position = (x + 1, y)
    elif move == 'L':
        new_position = (x, y - 1)
    elif move == 'R':
        new_position = (x, y + 1)
    else:
        new_position = position

    if board[new_position[0]][new_position[1]] != '#':
        return new_position
    return position

def simulate_moves(board, moves):
  # Find the initial position of Lambda-Man
  lambda_position = None
  for i, row in enumerate(board):
    for j, cell in enumerate(row):
      if cell == 'L':
        lambda_position = (i, j)
        break
    if lambda_position:
      break

  # Remove the initial 'L' from the board for accurate display
  board[lambda_position[0]][lambda_position[1]] = '.'

  # Display the initial board
  display_board(board, lambda_position)

  # Simulate each move
  for move in moves:
    lambda_position = move_lambda(board, lambda_position, move)
    display_board(board, lambda_position)
    # Clear the display
    clear_display()

def clear_display():
  # Use appropriate method to clear the display based on your environment
  # For example, in a terminal, you can use:
  print('\033c', end='')
  # In Jupyter Notebook, you can use:
  # from IPython.display import clear_output
  # clear_output(wait=True)

# Example usage
board = [
    "###.#...",
    "...L..##",
    ".#######"
]

# Convert board to list of list for mutability
board = [list(row) for row in board]

# Define the moves
moves = "LLLDURRRUDRRURR"

# Simulate the moves
simulate_moves(board, moves)
