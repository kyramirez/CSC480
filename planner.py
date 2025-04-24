import sys
import heapq

# directions: (row_offset, col_offset)
MOVES = {
    'N': (-1, 0),
    'S': (1, 0),
    'E': (0, 1),
    'W': (0, -1)
}

def parse_world(file_path):
    with open(file_path, 'r') as f:
        lines = f.read().splitlines()
    
    cols = int(lines[0])
    rows = int(lines[1])
    grid = [list(line) for line in lines[2:]]
    
    dirty = set()
    blocked = set()
    start = None
    
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

def get_neighbors(pos, grid, blocked):
    neighbors = []
    for action, (dr, dc) in MOVES.items():
        nr, nc = pos[0] + dr, pos[1] + dc
        if 0 <= nr < len(grid) and 0 <= nc < len(grid[0]) and (nr, nc) not in blocked:
            neighbors.append((action, (nr, nc)))
    return neighbors

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

        if not dirty_left:
            return path, nodes_generated, nodes_expanded

        # Vacuum if dirty
        if pos in dirty_left:
            new_dirty = set(dirty_left)
            new_dirty.remove(pos)
            stack.append((pos, frozenset(new_dirty), path + ['V']))
            nodes_generated += 1

        for action, new_pos in get_neighbors(pos, grid, blocked):
            stack.append((new_pos, dirty_left, path + [action]))
            nodes_generated += 1

    return None, nodes_generated, nodes_expanded

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

        if not dirty_left:
            return path, nodes_generated, nodes_expanded

        # Vacuum if dirty
        if pos in dirty_left:
            new_dirty = set(dirty_left)
            new_dirty.remove(pos)
            heapq.heappush(pq, (cost + 1, pos, frozenset(new_dirty), path + ['V']))
            nodes_generated += 1

        for action, new_pos in get_neighbors(pos, grid, blocked):
            heapq.heappush(pq, (cost + 1, new_pos, dirty_left, path + [action]))
            nodes_generated += 1

    return None, nodes_generated, nodes_expanded

def main():
    if len(sys.argv) != 3:
        print("Usage: python3 planner.py [uniform-cost|depth-first] [world-file]")
        sys.exit(1)
    
    algorithm = sys.argv[1]
    world_file = sys.argv[2]
    grid, start, dirty, blocked = parse_world(world_file)

    if algorithm == "depth-first":
        plan, nodes_generated, nodes_expanded = dfs(start, dirty, grid, blocked)
    elif algorithm == "uniform-cost":
        plan, nodes_generated, nodes_expanded = ucs(start, dirty, grid, blocked)
    else:
        print("Unknown algorithm:", algorithm)
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
