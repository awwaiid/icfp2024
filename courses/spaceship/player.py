import math

class PositionTracker:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y
        self.v = [0,0]
        self.velocity_history = []
        self.move_history = []

    def get_current_pos(self):
        return (self.x, self.y)

    def update_velocity(self, dx, dy):
        #print(f"Updating Velocity by {dx}, {dy}")
        self.v = [self.v[0] + dx, self.v[1] + dy]
        #print(f"New Velocity: {self.v}")

        self.move(self.v[0], self.v[1])
        self.velocity_history.append(self.v)
        #self.print_velocity()

    def move(self, dx, dy):
        self.x += dx
        self.y += dy
        self.move_history.append((dx, dy))
        #self.print_position()
        #self.print_move_history()

    def apply_vel_to_pos(pos, vel):
        return (pos[0] + vel[0], pos[1] + vel[1])

    def print_status(self):
        cur = self.get_current_pos()
        vel = self.v
        next_pos = PositionTracker.apply_vel_to_pos(cur, vel)
        print(f"Current pos: ({self.x}, {self.y}) Current vel: ({self.v}) Next Neutral Pos: ({next_pos})")
    
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

    def get_direction_to_position(self, destination):
        next_pos = PositionTracker.apply_vel_to_pos(self.get_current_pos(), self.v)
        if destination[0] < next_pos[0]:
            #slow down x
            new_v_x =  [7,4,1]
        elif destination[0] > next_pos[0]:
            new_v_x = [9,6,3]
        else:
            new_v_x = [8,5,2] 
        if destination[1] < next_pos[1]:
            #slow down y
            new_v_y = [1,2,3]
        elif destination[1] > next_pos[1]:
            new_v_y = [7,8,9]
        else:
            new_v_y = [4,5,6]

        set1 = set(new_v_x)
        set2 = set(new_v_y)
        common_values = set1 & set2
        return next(iter(common_values))




class PositionMap:
    def __init__(self):
        self.visited = []
        self.pending = []
    
    def import_positions(self, positions):
        self.visited = []
        self.pending = []
        lines = positions.strip().splitlines()  # Split the string into lines
        for line in lines:
            line = line.strip()  # Remove any leading/trailing whitespace
            if line:  # Ensure the line is not empty
                split = line.split(' ')
                x = int(split[0]) 
                y = int(split[1])  # Split and convert to integers
                self.pending.append((x, y))  # Append the tuple (x, y) to the list

    def remove_all_occurrences(lst, value):
        # Use list comprehension to filter out all occurrences of `value`
        return [item for item in lst if item != value]

    def visit(self, pos):
        if pos in self.pending:
            self.pending = PositionMap.remove_all_occurrences(self.pending, pos)
            self.visited.append(pos)
    
    def all_visited(self):
        return not self.pending
    

    def get_closest(self, pos):
        if not self.pending:
            return None
    
        #print(self.pending)
        nearest_position = self.pending[0]
        #print(nearest_position)
        min_distance = math.dist(pos, nearest_position)
        
        for position in self.pending[1:]:
            distance = math.dist(pos, position)
            if distance < min_distance:
                nearest_position = position
                min_distance = distance

        return nearest_position
    
    def print_status(self):
        print(f"Visited: {len(self.visited)}, Pending: {len(self.pending)}")

    
    #def get_next_direction(pos):

    
class Player:
    def __init__(self, tracker, grid):
        self.tracker = tracker
        self.grid = grid
        self.map_data = """1 -1
1 -3
2 -5
2 -8
3 -10
"""         
        grid.import_positions(self.map_data)
        self.keylookup = {
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

        self.key_history = []
        self.all_clear = False

    def import_map_data(self, data):
        self.map_data = data
        self.grid.import_positions(data)

    def get_map_data(self):
        return self.map_data
    
    def get_key_history(self):
        history_out = []
        for i, move in enumerate(self.key_history, start=1):
            history_out.append(move)
        return history_out

    def move(self, move):
        if 1 <= move <= 9:
            dx, dy = map(int, self.keylookup[move])
            self.tracker.update_velocity(dx, dy)
            self.key_history.append(move)
            self.grid.visit(self.tracker.get_current_pos())
            if (self.grid.all_visited()):
                self.all_clear = True


if __name__ == "__main__":
    tracker = PositionTracker()
    print("Starting position and velocity: (0, 0)")
    pos_map = PositionMap()
    player = Player(tracker, pos_map)

    while True:
        current = tracker.get_current_pos()
        closest = pos_map.get_closest(current)

        print (f"Current: {current}, Closest: {closest}")
        suggested = tracker.get_direction_to_position(closest)
        print (f"Suggested {suggested}")
        
        move_input = input("Enter your velocity as a number key (or 'quit' to exit) (0 for the suggested move): ")
        if move_input.lower() == 'quit':
            print("Key history:")
            print(player.get_key_history())
            print()
            break

        if move_input == '':
            move_input = suggested
        try:
            
            print(move_input)
            move = int(move_input)
            if 0 <= move <= 9:
                if move == 0:
                    move = suggested
                player.move(move)
                if player.all_clear:
                    print("Success!")
                    print("Key history:")
                    result = ''.join(map(str, player.get_key_history()))
                    print(result)
                    break
                tracker.print_status()
                pos_map.print_status()
            else:
                raise ValueError
            
        except ValueError as e:
            print("Invalid input. Please us an integer between 0 and 9.")
            print(e)
            