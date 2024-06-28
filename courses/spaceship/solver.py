#!/usr/bin/env python
import sys
import os
libs_path = os.path.join(os.path.dirname(__file__), '../../')
sys.path.append(libs_path)

from client import Client

from player import Player, PositionMap, PositionTracker

client = Client()


if __name__ == "__main__":
   
    while True:
        try:
            
            game_input = input("Enter which game to fetch: ")
            game_num = int(game_input)
            if 1 <= game_num <= 25:
                response, decoded = client.call(f"get spaceship{game_num}")
                game_map = decoded.strip()

                grid = PositionMap()
                tracker = PositionTracker()
                player = Player(tracker, grid)
                player.import_map_data(game_map)
                

                move_count = 0
                print("Move:", end="")
                while not player.all_clear:
                    print(".", end="")
                    current = tracker.get_current_pos()
                    closest = grid.get_closest(current)
                    suggested = tracker.get_direction_to_position(closest)
                    player.move(suggested)
                    move_count = move_count + 1
                    
                print()
                print(f"Key history for {game_num}:")
                result = ''.join(map(str, player.get_key_history()))
                print(result)
                print()
                print("Submitting")
                response, decoded = client.call(f"solve spaceship{game_num} {result}")

                print(decoded)


            else:
                raise ValueError
            
        except ValueError as e:
            print("Invalid input. Please us an integer between 0 and 9.")
            print(e)
            