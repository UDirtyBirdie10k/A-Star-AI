""" 
NETIDs:
William Tran: WHT12
Yash Patel: ydp11
Dylan Jay: drj74
"""

import numpy as np
import sys
import random
import matplotlib.pyplot as plt
import os
from itertools import product  # Add this import statement
import time





class BinaryHeap:
    def __init__(self):
        self.heap = []

    def push(self, fscore, gscore, item):
        """Add item to the heap, maintaining the heap invariant."""
        # We push (fscore, -gscore, item) so that Python's min-heap will handle ties by preferring higher gscore
        self.heap.append((fscore, -gscore, item))
        self._sift_up(len(self.heap) - 1)

    def pop(self):
        """Remove and return the item with the smallest fscore and highest gscore in case of a tie."""
        if len(self.heap) == 1:
            return self.heap.pop()[2]  # Return the item (third element in tuple)
        root = self.heap[0][2]  # Store the item (third element in tuple)
        self.heap[0] = self.heap.pop()  # Move the last item to the root
        self._sift_down(0)
        return root

    def _sift_up(self, index):
        """Move the item at index up to its proper position in the heap."""
        item = self.heap[index]
        while index > 0:
            parent_index = (index - 1) >> 1
            parent = self.heap[parent_index]
            # Compare by fscore first, and if tied, by -gscore
            if item < parent:
                self.heap[index] = parent
                index = parent_index
                continue
            break
        self.heap[index] = item

    def _sift_down(self, index):
        """Move the item at index down to its proper position in the heap."""
        item = self.heap[index]
        end_index = len(self.heap)
        child_index = 2 * index + 1  # Left child index
        while child_index < end_index:
            right_child_index = child_index + 1
            # Compare left and right child; choose the smaller fscore, then higher gscore in ties
            if right_child_index < end_index and not self.heap[child_index] < self.heap[right_child_index]:
                child_index = right_child_index
            # Compare with the current item
            if self.heap[child_index] < item:
                self.heap[index] = self.heap[child_index]
                index = child_index
                child_index = 2 * index + 1
            else:
                break
        self.heap[index] = item

    def __len__(self):
        return len(self.heap)

    def __repr__(self):
        return f'{self.heap}'


def load_grid(path):
    return np.load(path)

# Constants
GRID_SIZE = 101
NUM_ENVIRONMENTS = 50
BLOCK_PROBABILITY = 0.3
UNBLOCK_PROBABILITY = 0.7

# Directions for movement (up, down, left, right)
DIRECTIONS = [(-1, 0), (1, 0), (0, -1), (0, 1)]


def generate_grid():
    # Initialize the grid where 1 = blocked, 0 = unblocked
    grid = np.ones((GRID_SIZE, GRID_SIZE), dtype=int)
    visited = np.zeros((GRID_SIZE, GRID_SIZE), dtype=bool)

    # Start from a random cell
    stack = []
    start_row, start_col = random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1)
    stack.append((start_row, start_col))
    visited[start_row, start_col] = True
    grid[start_row, start_col] = 0  # Mark as unblocked

    while stack:
        # Get the current position
        row, col = stack[-1]

        # Find all unvisited neighbors
        neighbors = []
        for dr, dc in DIRECTIONS:
            r, c = row + dr, col + dc
            if 0 <= r < GRID_SIZE and 0 <= c < GRID_SIZE and not visited[r, c]:
                neighbors.append((r, c))

        if neighbors:
            # Randomly select a neighbor to visit
            next_row, next_col = random.choice(neighbors)

            # With 30% probability, mark as blocked, otherwise unblocked
            if random.random() < BLOCK_PROBABILITY:
                grid[next_row, next_col] = 1  # Block the cell
            else:
                grid[next_row, next_col] = 0  # Unblock the cell
                stack.append((next_row, next_col))

            # Mark the neighbor as visited
            visited[next_row, next_col] = True
        else:
            # Dead-end: backtrack
            stack.pop()

    return grid

def load_grid(filename):
    try:
        # Assuming the grid is saved as a NumPy array text file
        return np.loadtxt(filename)
    except Exception as e:
        print(f"Error loading the grid from {filename}: {e}")
        return None

def visualize_grid(grid):
    if grid is not None:
        plt.imshow(grid, cmap='binary', interpolation='none')
        plt.title('Gridworld')
        plt.show()
    else:
        print("No grid to display.")

    
def save_grids(num_environments=NUM_ENVIRONMENTS):
    grids = []
    for i in range(num_environments):
        grid = generate_grid()
        grids.append(grid)
        # Save the grid to a .txt file
        filename = f'grid_{i}.txt'
        np.savetxt(filename, grid, fmt='%d')  # Save as integers (0s and 1s)
        print(f"Grid {i} saved as {filename}.")
    return grids

def load_grid(path):
    try:
        # Use np.loadtxt if the files are plain text files
        return np.loadtxt(path)  # Adjust this depending on your file format
    except ValueError as e:
        print(f"Error loading {path}: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error while loading {path}: {e}")
        return None

def load_grids_from_folder(folder_path):
    grids = []
    grid_files = [f for f in os.listdir(folder_path) if f.startswith('grid') and f.endswith('.txt')]

    if len(grid_files) == 0:
        print("No grid files found in the folder.")
        return None, None

    for filename in grid_files:
        grid_path = os.path.join(folder_path, filename)
        grid = load_grid(grid_path)
        if grid is not None:  # Only append if the grid was loaded successfully
            grids.append(grid)  # Append only the grid array
            print(f"Loaded grid from {filename}.")
    
    return grids, grid_files

def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def find_unblocked_cell(grid):
    while True:
        x = random.randint(0, grid.shape[0] - 1)
        y = random.randint(0, grid.shape[1] - 1)
        if grid[x][y] == 0:  # Assuming 0 represents unblocked cells
            return (x, y)
        
def initialize_visibility_grid(grid, start, goal):
    visibility_grid = np.zeros_like(grid)
    visibility_grid[start[0], start[1]] = 1  # Reveal start position
    visibility_grid[goal[0], goal[1]] = 1  # Goal is always visible

    # Initially reveal adjacent cells around the start position
    reveal_adjacent_cells(start, grid, visibility_grid)

    # Also reveal the goal's adjacent cells
    reveal_adjacent_cells(goal, grid, visibility_grid)

    return visibility_grid



def reveal_adjacent_cells(pos, grid, visibility_grid):
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # Up, down, left, right
    visibility_grid[pos[0], pos[1]] = 1  # Reveal current position

    for direction in directions:
        neighbor = (pos[0] + direction[0], pos[1] + direction[1])
        if 0 <= neighbor[0] < grid.shape[0] and 0 <= neighbor[1] < grid.shape[1]:
            visibility_grid[neighbor[0], neighbor[1]] = 1  # Mark neighbor as seen
            
            # Reveal surrounding cells for better pathfinding
            for adj_direction in directions:
                adj_neighbor = (neighbor[0] + adj_direction[0], neighbor[1] + adj_direction[1])
                if 0 <= adj_neighbor[0] < grid.shape[0] and 0 <= adj_neighbor[1] < grid.shape[1]:
                    visibility_grid[adj_neighbor[0], adj_neighbor[1]] = 1  # Reveal more around




def a_star_search_high_g(grid, visibility_grid, start, goal):
    neighbors = [(0, 1), (1, 0), (0, -1), (-1, 0)]
    close_set = set()
    came_from = {}
    gscore = {start: 0}
    fscore = {start: heuristic(start, goal)}

    open_heap = BinaryHeap()

    # Push (fscore, gscore, node)
    open_heap.push(fscore[start], gscore[start], start)

    while len(open_heap) > 0:
        current = open_heap.pop()  # Corrected to get just the item

        if current == goal:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            return path[::-1]  # Return the reversed path

        close_set.add(current)
        reveal_adjacent_cells(current, grid, visibility_grid)

        for i, j in neighbors:
            neighbor = (current[0] + i, current[1] + j)
            if 0 <= neighbor[0] < grid.shape[0] and 0 <= neighbor[1] < grid.shape[1]:
                if visibility_grid[neighbor[0]][neighbor[1]] == 1 and grid[neighbor[0]][neighbor[1]] == 0:
                    tentative_g_score = gscore[current] + 1
                    if tentative_g_score < gscore.get(neighbor, float('inf')):
                        came_from[neighbor] = current
                        gscore[neighbor] = tentative_g_score
                        fscore[neighbor] = tentative_g_score + heuristic(neighbor, goal)
                        open_heap.push(fscore[neighbor], gscore[neighbor], neighbor)  # Corrected push

    print("No path found in Repeated A* search.")
    return None  # Returning None for consistency

def a_star_search_low_g(grid, visibility_grid, start, goal):
    neighbors = [(0, 1), (1, 0), (0, -1), (-1, 0)]
    close_set = set()
    came_from = {}
    gscore = {start: 0}
    fscore = {start: heuristic(start, goal)}

    open_heap = BinaryHeap()

    # Push (fscore, gscore, node)
    open_heap.push(fscore[start], -(gscore[start]), start)

    while len(open_heap) > 0:
        current = open_heap.pop()  # Corrected to get just the item

        if current == goal:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            return path[::-1]  # Return the reversed path

        close_set.add(current)
        reveal_adjacent_cells(current, grid, visibility_grid)

        for i, j in neighbors:
            neighbor = (current[0] + i, current[1] + j)
            if 0 <= neighbor[0] < grid.shape[0] and 0 <= neighbor[1] < grid.shape[1]:
                if visibility_grid[neighbor[0]][neighbor[1]] == 1 and grid[neighbor[0]][neighbor[1]] == 0:
                    tentative_g_score = gscore[current] + 1
                    if tentative_g_score < gscore.get(neighbor, float('inf')):
                        came_from[neighbor] = current
                        gscore[neighbor] = tentative_g_score
                        fscore[neighbor] = tentative_g_score + heuristic(neighbor, goal)
                        open_heap.push(fscore[neighbor], gscore[neighbor], neighbor)  # Corrected push

    print("No path found in Repeated A* search.")
    return None  # Returning None for consistency

def repeated_backward_a_star_with_fog(grid, start, goal):
    global path
    full_path = [goal]
    current = goal
    current_pos = goal
    visibility_grid = initialize_visibility_grid(grid, start, goal)

    while current_pos != start:  # Search until we reach the start
        partial_path = a_star_search_high_g(grid, visibility_grid, current, start)  # Search towards the start
        if not partial_path:
            return []  # No path found

        for step in partial_path:
            if grid[step[0], step[1]] == 1:  # Blocked cell
                visibility_grid[step[0], step[1]] = 1  # Mark as seen
                print(f"Blocked cell encountered at {step}. Re-planning from {current_pos}.")
                break
            else:
                visibility_grid[step[0], step[1]] = 1  # Mark as seen
                full_path.append(step)
                current_pos = step
                
                # Reveal adjacent cells from the new position
                reveal_adjacent_cells(current_pos, grid, visibility_grid)
        
                # Check if goal is reached
                if current_pos == goal:
                    print("Goal reached!")
                    return full_path[::-1]

    return full_path[::-1]
def repeated_a_star_high_g(grid, start, goal):
    print(f"Start Position: {start}, Goal Position: {goal}")
    visibility_grid = initialize_visibility_grid(grid, start, goal)
    current_pos = start
    full_path = [start]
    '''
    #debugging output
    print("Initial Grid:")
    print(grid)
    '''
    '''
    #debugging output
    print(f"Start Position: {start}, Goal Position: {goal}")
    '''
    while current_pos != goal:


        # Perform A* search with fog of war (limited visibility)
        partial_path = a_star_search_high_g(grid, visibility_grid, current_pos, goal)

        if not partial_path:
            print(f"No path found from {current_pos} to {goal}. Checking for alternatives.")
            # You could add logic here to try other paths or backtrack
            break  # For now, just break out if no path is found

        for step in partial_path:
            if grid[step[0], step[1]] == 1:  # Blocked cell
                visibility_grid[step[0], step[1]] = 1  # Mark as seen
                print(f"Blocked cell encountered at {step}. Re-planning from {current_pos}.")
                break
            else:
                visibility_grid[step[0], step[1]] = 1  # Mark as seen
                full_path.append(step)
                current_pos = step
                
                # Reveal adjacent cells from the new position
                reveal_adjacent_cells(current_pos, grid, visibility_grid)
        
                # Check if goal is reached
                if current_pos == goal:
                    print("Goal reached!")
                    return full_path

    print("No valid path found after multiple attempts.")
    return None  # Return None if no path found

def repeated_a_star_low_g(grid, start, goal):
    print(f"Start Position: {start}, Goal Position: {goal}")
    visibility_grid = initialize_visibility_grid(grid, start, goal)
    current_pos = start
    full_path = [start]
    '''
    #debugging output
    print("Initial Grid:")
    print(grid)
    '''
    '''
    #debugging output
    print(f"Start Position: {start}, Goal Position: {goal}")
    '''
    while current_pos != goal:


        # Perform A* search with fog of war (limited visibility)
        partial_path = a_star_search_low_g(grid, visibility_grid, current_pos, goal)

        if not partial_path:
            print(f"No path found from {current_pos} to {goal}. Checking for alternatives.")
            # You could add logic here to try other paths or backtrack
            break  # For now, just break out if no path is found

        for step in partial_path:
            if grid[step[0], step[1]] == 1:  # Blocked cell
                visibility_grid[step[0], step[1]] = 1  # Mark as seen
                print(f"Blocked cell encountered at {step}. Re-planning from {current_pos}.")
                break
            else:
                visibility_grid[step[0], step[1]] = 1  # Mark as seen
                full_path.append(step)
                current_pos = step
                
                # Reveal adjacent cells from the new position
                reveal_adjacent_cells(current_pos, grid, visibility_grid)
        
                # Check if goal is reached
                if current_pos == goal:
                    print("Goal reached!")
                    return full_path

    print("No valid path found after multiple attempts.")
    return None  # Return None if no path found


# Global dictionary to store updated heuristic values
updated_heuristics = {}

def adaptive_heuristic(state, goal):
    # If state has an updated heuristic value, use it
    if state in updated_heuristics:
        return updated_heuristics[state]
    else:
        # Use the standard heuristic (e.g., Manhattan distance) if no updated value
        return heuristic(state, goal)

def adaptive_a_star_with_fog(grid, start, goal):
    print(f"Start Position: {start}, Goal Position: {goal}")
    visibility_grid = initialize_visibility_grid(grid, start, goal)
    current_pos = start
    full_path = [start]

    # First run of the adaptive A* search
    partial_path = adaptive_a_star_search_with_fog(grid, visibility_grid, current_pos, goal)

    if not partial_path:
        print(f"No path found from {current_pos} to {goal}.")
        return None  # Return None if no path found

    # Now run the adaptive A* search again with updated heuristics
    print("Re-running adaptive A* search with updated heuristics...")
    current_pos = start  # Reset current position
    full_path = [start]  # Reset full path

    while current_pos != goal:
        # Perform A* search with fog of war using updated heuristics
        partial_path = adaptive_a_star_search_with_fog(grid, visibility_grid, current_pos, goal)

        if not partial_path:
            print(f"No path found from {current_pos} to {goal}. Checking for alternatives.")
            break  # For now, just break out if no path is found

        for step in partial_path:
            if grid[step[0], step[1]] == 1:  # Blocked cell
                visibility_grid[step[0], step[1]] = 1  # Mark as seen
                print(f"Blocked cell encountered at {step}. Re-planning from {current_pos}.")
                break
            else:
                visibility_grid[step[0], step[1]] = 1  # Mark as seen
                full_path.append(step)
                current_pos = step
                
                # Reveal adjacent cells from the new position
                reveal_adjacent_cells(current_pos, grid, visibility_grid)

                # Check if goal is reached
                if current_pos == goal:
                    print("Goal reached!")
                    return full_path

    print("No valid path found after multiple attempts.")
    return None  # Return None if no path found


def adaptive_a_star_search_with_fog(grid, visibility_grid, start, goal):
    neighbors = [(0, 1), (1, 0), (0, -1), (-1, 0)]
    close_set = set()
    came_from = {}
    gscore = {start: 0}
    fscore = {start: adaptive_heuristic(start, goal)}
    open_heap = BinaryHeap()

    # Push (fscore, gscore, node)
    open_heap.push(fscore[start], gscore[start], start)

    while len(open_heap) > 0:
        current = open_heap.pop()  # Corrected to get just the item

        if current == goal:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.reverse()  # Reverse the path for correct order
            
            # After finding the path, update heuristics for all explored nodes
            g_goal = gscore[goal]  # g(s_goal)
            for node in close_set:
                # Update heuristic: 
                updated_heuristics[node] = g_goal - gscore[node]

            return path  # Return the found path

        close_set.add(current)
        reveal_adjacent_cells(current, grid, visibility_grid)

        for i, j in neighbors:
            neighbor = (current[0] + i, current[1] + j)
            if 0 <= neighbor[0] < grid.shape[0] and 0 <= neighbor[1] < grid.shape[1]:
                if visibility_grid[neighbor[0]][neighbor[1]] == 1 and grid[neighbor[0]][neighbor[1]] == 0:
                    tentative_g_score = gscore[current] + 1
                    if tentative_g_score < gscore.get(neighbor, float('inf')):
                        came_from[neighbor] = current
                        gscore[neighbor] = tentative_g_score
                        fscore[neighbor] = tentative_g_score + adaptive_heuristic(neighbor, goal)
                        open_heap.push(fscore[neighbor], gscore[neighbor], neighbor)  # Corrected push


def visualize_path(grid, path):
    plt.imshow(grid, cmap='binary')
    for (x, y) in path:
        plt.plot(y, x, 'ro')  # 'ro' to mark the path with red dots
    plt.plot(path[0][1], path[0][0], 'go')  # Start in green
    plt.plot(path[-1][1], path[-1][0], 'bo')  # Goal in blue
    plt.xlim(-0.5, grid.shape[1]-0.5)
    plt.ylim(-0.5, grid.shape[0]-0.5)
    plt.grid()
    plt.show()

def visualize_path_backward(grid, path):
    plt.imshow(grid, cmap='binary')
    for (x, y) in path:
        plt.plot(y, x, 'ro')  # 'ro' to mark the path with red dots
    plt.plot(path[0][1], path[0][0], 'bo')  # Start in green
    plt.plot(path[-1][1], path[-1][0], 'go')  # Goal in blue
    plt.xlim(-0.5, grid.shape[1]-0.5)
    plt.ylim(-0.5, grid.shape[0]-0.5)
    plt.grid()
    plt.show()

def main():
    # Generate and save grids
    save_grids(num_environments=NUM_ENVIRONMENTS)
    
    # Assuming the grids are stored in the same directory as the script
    folder_path = os.path.dirname(os.path.realpath(__file__))
    grids, grid_files = load_grids_from_folder(folder_path)
    
    if grids is not None:
        # List the grids once outside the loop
        print("\nAvailable grids:")
        for idx, filename in enumerate(grid_files):
            print(f"{idx + 1}. {filename}")
        print("Enter 0 to exit.")
        
        while True:
            # Prompt for user selection within the loop without reprinting the grid list
            try:
                selected_idx = int(input("\nEnter the number corresponding to the grid you want to use (or 0 to exit): ")) - 1
                if selected_idx == -1:
                    print("Exiting.")
                    break  # Exit if the user enters 0

                if 0 <= selected_idx < len(grids):
                    grid = grids[selected_idx]
                    print(f"You selected: {grid_files[selected_idx]}")

                    start = find_unblocked_cell(grid)
                    goal = find_unblocked_cell(grid)
                    while goal == start:
                        goal = find_unblocked_cell(grid)

                    print(f"Grid size: {grid.shape}, Start: {start}, Goal: {goal}")
                    
                    # Measure execution time for each search
                    start_time = time.time()
                    path_high_g = repeated_a_star_high_g(grid, start, goal)
                    time_high_g = time.time() - start_time
                    
                    start_time = time.time()
                    path_low_g = repeated_a_star_low_g(grid, start, goal)
                    time_low_g = time.time() - start_time
                    
                    start_time = time.time()
                    path_backward = repeated_backward_a_star_with_fog(grid, start, goal)
                    time_backward = time.time() - start_time
                    
                    start_time = time.time()
                    path_adaptive = adaptive_a_star_with_fog(grid, start, goal)
                    time_adaptive = time.time() - start_time

                    # Printing results and timings
                    print("\nSearch Results and Timings:")
                    if path_high_g:
                        visualize_path(grid, path_high_g)
                        print(f"Repeated A* High G Path Length: {len(path_high_g)}, Time: {time_high_g:.3f} seconds")
                    else:
                        print("No path found in Repeated A* High G.")
                        
                    if path_low_g:
                        visualize_path(grid, path_low_g)
                        print(f"Repeated A* Low G Path Length: {len(path_low_g)}, Time: {time_low_g:.3f} seconds")
                    else:
                        print("No path found in Repeated A* Low G.")
                    
                    if path_backward:
                        visualize_path_backward(grid, path_backward)
                        print(f"Repeated Backward A* Path Length: {len(path_backward)}, Time: {time_backward:.3f} seconds")
                    else:
                        print("No path found in Repeated Backward A*.")

                    if path_adaptive:
                        visualize_path(grid, path_adaptive)
                        print(f"Adaptive A* Path Length: {len(path_adaptive)}, Time: {time_adaptive:.3f} seconds")
                    else:
                        print("No path found in Adaptive A*.")

                else:
                    print("Invalid selection. Please select a valid grid number or enter 0 to exit.")
            except ValueError:
                print("Invalid input. Please enter a valid number.")

if __name__ == "__main__":
    main()
