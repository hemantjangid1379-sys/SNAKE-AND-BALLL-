import tkinter as tk
import random
from collections import deque
import heapq

# ---------------------- GRID SETUP ---------------------- #
N = 10
CELL_SIZE = 50

# Random start and goal
snake = (random.randint(0, N - 1), random.randint(0, N - 1))
ball = (random.randint(0, N - 1), random.randint(0, N - 1))
while ball == snake:
    ball = (random.randint(0, N - 1), random.randint(0, N - 1))

# ---------------------- HELPER FUNCTIONS ---------------------- #
def heuristic(a, b):
    """Manhattan distance"""
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def neighbors(node):
    """Valid 4-directional neighbors"""
    (x, y) = node
    for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
        nx, ny = x + dx, y + dy
        if 0 <= nx < N and 0 <= ny < N:
            yield (nx, ny)

# ---------------------- SEARCH ALGORITHMS ---------------------- #
def hill_climb(start, goal):
    current = start
    path = [current]
    visited = {current}
    while current != goal:
        neigh = list(neighbors(current))
        next_pos = min(neigh, key=lambda x: heuristic(x, goal))
        if heuristic(next_pos, goal) >= heuristic(current, goal):
            break
        current = next_pos
        path.append(current)
        visited.add(current)
    return path, visited

def bfs(start, goal):
    queue = deque([(start, [start])])
    visited = {start}
    while queue:
        pos, path = queue.popleft()
        if pos == goal:
            return path, visited
        for n in neighbors(pos):
            if n not in visited:
                visited.add(n)
                queue.append((n, path + [n]))
    return [], visited

def dfs(start, goal):
    stack = [(start, [start])]
    visited = {start}
    while stack:
        pos, path = stack.pop()
        if pos == goal:
            return path, visited
        for n in neighbors(pos):
            if n not in visited:
                visited.add(n)
                stack.append((n, path + [n]))
    return [], visited

def best_first(start, goal):
    pq = [(heuristic(start, goal), start, [start])]
    visited = set()
    while pq:
        _, pos, path = heapq.heappop(pq)
        if pos == goal:
            return path, visited
        if pos in visited:
            continue
        visited.add(pos)
        for n in neighbors(pos):
            if n not in visited:
                heapq.heappush(pq, (heuristic(n, goal), n, path + [n]))
    return [], visited

def dijkstra(start, goal):
    pq = [(0, start, [start])]
    visited = set()
    while pq:
        cost, pos, path = heapq.heappop(pq)
        if pos == goal:
            return path, visited
        if pos in visited:
            continue
        visited.add(pos)
        for n in neighbors(pos):
            if n not in visited:
                heapq.heappush(pq, (cost + 1, n, path + [n]))
    return [], visited

def a_star(start, goal):
    pq = [(heuristic(start, goal), 0, start, [start])]
    visited = set()
    while pq:
        f, g, pos, path = heapq.heappop(pq)
        if pos == goal:
            return path, visited
        if pos in visited:
            continue
        visited.add(pos)
        for n in neighbors(pos):
            if n not in visited:
                new_g = g + 1
                heapq.heappush(pq, (new_g + heuristic(n, goal), new_g, n, path + [n]))
    return [], visited

def ao_star(start, goal):
    current = start
    path = [current]
    visited = {current}
    while current != goal:
        neighs = list(neighbors(current))
        scored = [
            (
                heuristic(n, goal)
                + min((heuristic(n2, goal) for n2 in neighbors(n)), default=0),
                n,
            )
            for n in neighs
        ]
        next_pos = min(scored, key=lambda x: x[0])[1]
        if heuristic(next_pos, goal) >= heuristic(current, goal):
            break
        current = next_pos
        path.append(current)
        visited.add(current)
    return path, visited

# ---------------------- GUI CLASS ---------------------- #
class GameGUI:
    def __init__(self, master):
        self.master = master
        master.title("Snake & Ball -Algorithm Visualizer")

        self.canvas = tk.Canvas(master, width=N * CELL_SIZE, height=N * CELL_SIZE, bg="white")
        self.canvas.grid(row=0, column=0, rowspan=20, padx=10, pady=10)

        # Algorithm Selection
        tk.Label(master, text="Choose Algorithm:").grid(row=0, column=1, sticky="w")
        self.algo_choice = tk.StringVar(value="Hill Climbing")
        algos = ["Hill Climbing", "BFS", "DFS", "Best First Search", "Dijkstra", "A*", "AO*"]
        for i, algo in enumerate(algos, start=1):
            tk.Radiobutton(master, text=algo, variable=self.algo_choice, value=algo).grid(row=i, column=1, sticky="w")

        tk.Button(master, text="Start Simulation", command=self.start_simulation, bg="lightgreen").grid(row=8, column=1, pady=5, sticky="we")
        tk.Button(master, text="Compare All Algorithms", command=self.compare_all, bg="lightblue").grid(row=9, column=1, pady=5, sticky="we")

        tk.Label(master, text="Algorithm History:").grid(row=10, column=1, sticky="w")
        self.history_box = tk.Listbox(master, height=10, width=35)
        self.history_box.grid(row=11, column=1, sticky="we")

        tk.Button(master, text="Show Selected Path", command=self.show_saved_path, bg="#ffd966").grid(row=12, column=1, pady=5, sticky="we")

        self.data = {}  # {algo_name: {'path': list, 'visited': set}}

        self.draw_grid()
        self.draw_points()

    # ---------------------- DRAWING ---------------------- #
    def draw_grid(self):
        for i in range(N + 1):
            self.canvas.create_line(0, i * CELL_SIZE, N * CELL_SIZE, i * CELL_SIZE, fill="#ddd")
            self.canvas.create_line(i * CELL_SIZE, 0, i * CELL_SIZE, N * CELL_SIZE, fill="#ddd")

    def draw_points(self):
        sx, sy = snake
        bx, by = ball
        # Start (green)
        self.canvas.create_oval(
            sx * CELL_SIZE + 10,
            sy * CELL_SIZE + 10,
            sx * CELL_SIZE + CELL_SIZE - 10,
            sy * CELL_SIZE + CELL_SIZE - 10,
            fill="green",
            outline="",
        )
        # Goal (red)
        self.canvas.create_oval(
            bx * CELL_SIZE + 10,
            by * CELL_SIZE + 10,
            bx * CELL_SIZE + CELL_SIZE - 10,
            by * CELL_SIZE + CELL_SIZE - 10,
            fill="red",
            outline="",
        )

    # ---------------------- SIMULATION ---------------------- #
    def start_simulation(self):
        self.canvas.delete("all")
        self.draw_grid()
        self.draw_points()

        algo = self.algo_choice.get()
        algo_map = {
            "Hill Climbing": (hill_climb, "green"),
            "BFS": (bfs, "blue"),
            "DFS": (dfs, "purple"),
            "Best First Search": (best_first, "orange"),
            "Dijkstra": (dijkstra, "black"),
            "A*": (a_star, "red"),
            "AO*": (ao_star, "gold"),
        }

        func, color = algo_map[algo]
        path, visited = func(snake, ball)
        self.data[algo] = {"path": path, "visited": visited}
        self.animate_path(path, visited, algo, color)
        self.update_history_listbox()

    def animate_path(self, path, visited, algo, color):
        # Highlight visited
        for (x, y) in visited:
            self.canvas.create_rectangle(
                x * CELL_SIZE + 5,
                y * CELL_SIZE + 5,
                x * CELL_SIZE + CELL_SIZE - 5,
                y * CELL_SIZE + CELL_SIZE - 5,
                fill="#f0f0f0",
                outline=""
            )
            self.canvas.update()
            self.canvas.after(15)

        # Draw final path
        if len(path) < 2:
            self.canvas.create_text(
                N * CELL_SIZE / 2,
                N * CELL_SIZE / 2,
                text="No path found!",
                fill="red",
                font=("Arial", 16, "bold"),
            )
            return

        for i in range(len(path) - 1):
            x1, y1 = path[i]
            x2, y2 = path[i + 1]
            x1c, y1c = x1 * CELL_SIZE + CELL_SIZE / 2, y1 * CELL_SIZE + CELL_SIZE / 2
            x2c, y2c = x2 * CELL_SIZE + CELL_SIZE / 2, y2 * CELL_SIZE + CELL_SIZE / 2
            self.canvas.create_line(x1c, y1c, x2c, y2c, fill=color, width=3)
            self.canvas.update()
            self.canvas.after(100)

        self.canvas.create_text(
            N * CELL_SIZE / 2,
            N * CELL_SIZE - 20,
            text=f"{algo}: {len(path)} steps, {len(visited)} visited",
            fill=color,
            font=("Arial", 12, "bold"),
        )

    # ---------------------- HISTORY ---------------------- #
    def update_history_listbox(self):
        self.history_box.delete(0, tk.END)
        for algo, info in self.data.items():
            path_len = len(info["path"])
            visited_len = len(info["visited"])
            self.history_box.insert(tk.END, f"{algo:20s} | Steps: {path_len:3d} | Visited: {visited_len:3d}")

    def show_saved_path(self):
        selection = self.history_box.curselection()
        if not selection:
            return
        selected_text = self.history_box.get(selection[0])
        algo = selected_text.split("|")[0].strip()

        if algo not in self.data:
            return

        info = self.data[algo]
        path, visited = info["path"], info["visited"]

        self.canvas.delete("all")
        self.draw_grid()
        self.draw_points()
        color_map = {
            "Hill Climbing": "green",
            "BFS": "blue",
            "DFS": "purple",
            "Best First Search": "orange",
            "Dijkstra": "black",
            "A*": "red",
            "AO*": "gold",
        }
        color = color_map.get(algo, "gray")
        self.animate_path(path, visited, algo, color)

    # ---------------------- COMPARISON ---------------------- #
    def compare_all(self):
        results = []
        algo_map = {
            "Hill Climbing": hill_climb,
            "BFS": bfs,
            "DFS": dfs,
            "Best First Search": best_first,
            "Dijkstra": dijkstra,
            "A*": a_star,
            "AO*": ao_star,
        }

        for name, func in algo_map.items():
            path, visited = func(snake, ball)
            self.data[name] = {"path": path, "visited": visited}
            results.append((name, len(path), len(visited)))

        self.update_history_listbox()

        reachable = [r for r in results if r[1] > 0]
        if not reachable:
            msg = "No algorithm reached the goal!"
        else:
            best_steps = min(reachable, key=lambda x: x[1])
            best_visited = min(reachable, key=lambda x: x[2])
            msg = (
                f"🏁 Best by Steps: {best_steps[0]} ({best_steps[1]} steps)\n"
                f"🔍 Best by Visited Nodes: {best_visited[0]} ({best_visited[2]} nodes)"
            )

        self.canvas.delete("all")
        self.draw_grid()
        self.draw_points()
        self.canvas.create_text(
            N * CELL_SIZE / 2,
            N * CELL_SIZE - 20,
            text=msg,
            fill="darkblue",
            font=("Arial", 12, "bold"),
        )

# ---------------------- RUN ---------------------- #
root = tk.Tk()
game = GameGUI(root)
root.mainloop()
