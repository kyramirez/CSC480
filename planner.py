import sys
import heapq

# directions the vacuum can go
MOVES = {
    'N': (-1, 0), # up
    'S': (1, 0), # down
    'E': (0, 1), # right
    'W': (0, -1) # left
}

# parses the world to get the grid layout and starting position. and dirty cells and blocked cells
def parse_world(file_path):
    with open(file_path, 'r') as f:
        lines = f.read().splitlines()
    
    cols = int(lines[0]) # num of columns
    rows = int(lines[1]) # num of rows in file
    grid = [list(line) for line in lines[2:]] # making it a 2d list
    
    # what the dirty and blocked cells are set to * and #
    dirty = set()
    blocked = set()
    start = None
    # start identifying the dirty and blocked cells
    for r in range(rows):
        for c in range(cols):
            cell = grid[r][c]
            if cell == '*':
                dirty.add((r, c))
            elif cell == '#':
                blocked.add((r, c))
            elif cell == '@':
                start = (r, c)
    
    return grid, start, dirty, blocked

# returns the neighbors positions from the bots current position
def get_neighbors(pos, grid, blocked):
    neighbors = []
    for action, (dr, dc) in MOVES.items():
        nr, nc = pos[0] + dr, pos[1] + dc
        if 0 <= nr < len(grid) and 0 <= nc < len(grid[0]) and (nr, nc) not in blocked:
            neighbors.append((action, (nr, nc)))
    return neighbors

# depth first search
def dfs(start, dirty, grid, blocked):
    stack = [(start, frozenset(dirty), [])]
    visited = set()
    nodes_generated = 1
    nodes_expanded = 0

    while stack:
        pos, dirty_left, path = stack.pop()
        state = (pos, dirty_left)
        if state in visited:
            continue
        visited.add(state)
        nodes_expanded += 1
    # check if no dirty cells left, return path
        if not dirty_left:
            return path, nodes_generated, nodes_expanded

    #  if the bots current position is dirty, clean it
        if pos in dirty_left:
            new_dirty = set(dirty_left)
            new_dirty.remove(pos)
            stack.append((pos, frozenset(new_dirty), path + ['V']))
            nodes_generated += 1
    # go to neighboring positions
        for action, new_pos in get_neighbors(pos, grid, blocked):
            stack.append((new_pos, dirty_left, path + [action]))
            nodes_generated += 1

    return None, nodes_generated, nodes_expanded

# uniform cost search uses priority queue
def ucs(start, dirty, grid, blocked):
    pq = []
    heapq.heappush(pq, (0, start, frozenset(dirty), []))
    visited = set()
    nodes_generated = 1
    nodes_expanded = 0


    while pq:
        cost, pos, dirty_left, path = heapq.heappop(pq)
        state = (pos, dirty_left)
        if state in visited:
            continue
        visited.add(state)
        nodes_expanded += 1

    # if no dirty cells left return the path
        if not dirty_left:
            return path, nodes_generated, nodes_expanded

        # checks current position if dirty
        if pos in dirty_left:
            new_dirty = set(dirty_left)
            new_dirty.remove(pos)
            heapq.heappush(pq, (cost + 1, pos, frozenset(new_dirty), path + ['V'])) # cost + 1
            nodes_generated += 1
    # checks neighbors cost + 1
        for action, new_pos in get_neighbors(pos, grid, blocked):
            heapq.heappush(pq, (cost + 1, new_pos, dirty_left, path + [action])) 
            nodes_generated += 1 

    return None, nodes_generated, nodes_expanded

def main():
    if len(sys.argv) != 3:
        print("python3 planner.py [uniform-cost|depth-first] [world-file]")
        sys.exit(1)
    
    algorithm = sys.argv[1]
    world_file = sys.argv[2]
    grid, start, dirty, blocked = parse_world(world_file)

    if algorithm == "depth-first":
        plan, nodes_generated, nodes_expanded = dfs(start, dirty, grid, blocked)
    elif algorithm == "uniform-cost":
        plan, nodes_generated, nodes_expanded = ucs(start, dirty, grid, blocked)
    else:
        print("unknown algorithm:", algorithm)
        sys.exit(1)

    if plan is not None:
        for action in plan:
            print(action)
        print(f"{nodes_generated} nodes generated")
        print(f"{nodes_expanded} nodes expanded")
    else:
        print("No solution found.")

if __name__ == "__main__":
    main()
