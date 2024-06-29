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
    
    def get_current_velocity(self):
        return self.v

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
        #print(next_pos)
        #print(destination)
        #print(self.v)
        #print( destination[0] < next_pos[0])
        #print(-1 * next_pos[0] - destination[0])

        def calc_v_offset(pos,des):
            return (pos - des)/2 




        if destination[0] < next_pos[0] and self.v[0] > -2:
            new_v_x =  [7,4,1]
        elif destination[0] > next_pos[0] and self.v[0] < 2:
            new_v_x = [9,6,3]
        else:
            new_v_x = [8,5,2] 

        #print('--')
        #print(destination[1])
        #print(next_pos[1])
        #print(self.v[1] > -1 * (next_pos[1] - destination[1]))
        if destination[1] < next_pos[1] and self.v[1] > -2:
            new_v_y = [1,2,3]
        elif destination[1] > next_pos[1] and self.v[1] < 2:
            new_v_y = [7,8,9]
        else:
            new_v_y = [4,5,6]

        
        set1 = set(new_v_x)
        set2 = set(new_v_y)
        #print(set1)
        #print(set2)
        common_values = set1 & set2
        #print(common_values)
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
    
    def vel_multiplier(v):  
        return (v) / 2

    def get_closest(self, pos, vel=[0,0]):
        if not self.pending:
            return None
        vx_mult = PositionMap.vel_multiplier(vel[0])
        vy_mult = PositionMap.vel_multiplier(vel[1])
        vx_mult = vy_mult = 0
        pos = (pos[0] + vx_mult, pos[1] + vy_mult)
        nearest_position = self.pending[0]
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
        self.map_data = """-3 2
-5 4
-7 5
-8 6
-9 6
-10 7
-10 7
-11 8
-13 9
-14 11
-14 14
-14 17
-13 19
-12 22
-12 25
-11 28
-10 30
-10 33
-9 37
-7 41
-5 46
-3 50
0 54
3 57
7 59
10 62
12 64
13 66
14 67
16 67
18 68
19 68
20 67
22 67
23 66
25 64
28 63
32 63
37 64
41 64
44 64
48 64
53 63
59 63
64 63
70 62
76 62
83 62
89 62
95 61
102 60
108 60
113 59
118 59
123 59
129 60
135 60
140 59
144 59
148 59
152 58
157 58
161 57
164 55
166 54
169 53
172 51
174 48
176 45
178 43
181 42
182 43
182 44
182 44
182 44
182 45
181 47
179 48
177 50
176 51
175 51
175 52
174 53
172 53
171 54
170 55
170 57
171 59
173 61
174 63
176 64
179 64
182 65
184 66
187 68
190 70
194 72
201 75
205 77
208 80
210 84
211 88
212 93
214 97
216 102
217 108
217 114
217 120
216 126
216 132
217 139
219 145
220 150
221 155
221 161
220 166
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


def read_positions_from_file(filename):    
    with open(filename, 'r') as file:
        content = file.read()
    return content

if __name__ == "__main__":
    tracker = PositionTracker()
    print("Starting position and velocity: (0, 0)")
    pos_map = PositionMap()
    player = Player(tracker, pos_map)
    problem = input("what problem?")
    if (int(problem)):
        problem_map = read_positions_from_file(f"./courses/spaceship/problems/{problem}.txt")
        player.import_map_data(problem_map)

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
            