

class PositionTracker:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y
        self.v = [0,0]
        self.velocity_history = []
        self.move_history = []

    def updateVelocity(self, dx, dy):
        print(f"Updating Velocity by {dx}, {dy}")
        self.v = [self.v[0] + dx, self.v[1] + dy]
        print(f"New Velocity: {self.v}")

        self.move(self.v[0], self.v[1])
        self.velocity_history.append(self.v)
        self.print_velocity()

    def move(self, dx, dy):
        self.x += dx
        self.y += dy
        self.move_history.append((dx, dy))
        self.print_position()
        #self.print_move_history()

    def print_position(self):
        print(f"Current position: ({self.x}, {self.y})")

    def print_velocity(self):
        print(f"Current veloci: ({self.v})")

    def print_velocity_history(self):
        print("Velocity history:")
        for i, move in enumerate(self.velocity_history, start=1):
            print(f"Velocity {i}: dx={move[0]}, dy={move[1]}")
        print()  # Newline for better readability

    def print_move_history(self):
        print("Move history:")
        for i, move in enumerate(self.move_history, start=1):
            print(f"Move {i}: dx={move[0]}, dy={move[1]}")
        print()  # Newline for better readability



if __name__ == "__main__":
    tracker = PositionTracker()
    print("Starting position and velocity: (0, 0)")

    keylookup = {
    1: [-1,-1],
    2: [0,-1],
    3: [1,-1],
    4: [-1,0],
    5: [0,0],
    6: [1,0],
    7: [-1,1],
    8: [0,1],
    9: [1,1]
    }

    key_history = []

    while True:
        move_input = input("Enter your velocity as a number key (or 'quit' to exit): ")
        if move_input.lower() == 'quit':
            print("Key history:")
            for i, move in enumerate(key_history, start=1):
                print(move, end="")
            print()    
            break

        try:
            dx, dy = map(int, keylookup[int(move_input)])
            tracker.updateVelocity(dx, dy)
            key_history.append(move_input)

            
        except ValueError:
            print("Invalid input. Please enter two integers separated by a space.")