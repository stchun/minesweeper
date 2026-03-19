from dataclasses import dataclass
from collections import deque
import random
import time


@dataclass
class Cell:
    has_mine: bool = False
    is_revealed: bool = False
    is_flagged: bool = False
    adjacent_mines: int = 0


class Board:
    def __init__(self, rows, cols, num_mines):
        self.rows = rows
        self.cols = cols
        self.num_mines = num_mines
        self.reset()

    def reset(self):
        self.game_state = "playing"  # "playing", "won", "lost"
        self.first_click = True
        self.triggered_mine = None
        self.start_time = None
        self.elapsed_time = 0.0
        self.grid = self._init_grid()

    def _init_grid(self):
        return [[Cell() for _ in range(self.cols)] for _ in range(self.rows)]

    def _place_mines(self, safe_r, safe_c):
        safe_cells = set()
        for dr in range(-1, 2):
            for dc in range(-1, 2):
                nr, nc = safe_r + dr, safe_c + dc
                if 0 <= nr < self.rows and 0 <= nc < self.cols:
                    safe_cells.add((nr, nc))

        candidates = [
            (r, c)
            for r in range(self.rows)
            for c in range(self.cols)
            if (r, c) not in safe_cells
        ]
        mine_positions = random.sample(candidates, self.num_mines)
        for r, c in mine_positions:
            self.grid[r][c].has_mine = True

        self._calc_adjacency()

    def _calc_adjacency(self):
        for r in range(self.rows):
            for c in range(self.cols):
                if not self.grid[r][c].has_mine:
                    self.grid[r][c].adjacent_mines = sum(
                        1 for nr, nc in self._neighbors(r, c)
                        if self.grid[nr][nc].has_mine
                    )

    def _neighbors(self, r, c):
        for dr in range(-1, 2):
            for dc in range(-1, 2):
                if dr == 0 and dc == 0:
                    continue
                nr, nc = r + dr, c + dc
                if 0 <= nr < self.rows and 0 <= nc < self.cols:
                    yield nr, nc

    def reveal(self, r, c):
        if self.game_state != "playing":
            return
        if not (0 <= r < self.rows and 0 <= c < self.cols):
            return

        cell = self.grid[r][c]
        if cell.is_revealed or cell.is_flagged:
            return

        if self.first_click:
            self.first_click = False
            self.start_time = time.time()
            self._place_mines(r, c)

        if cell.has_mine:
            cell.is_revealed = True
            self.triggered_mine = (r, c)
            self._stop_timer()
            self.game_state = "lost"
            self._reveal_all_mines()
            return

        if cell.adjacent_mines == 0:
            self._flood_fill(r, c)
        else:
            cell.is_revealed = True

        if self.check_win():
            self._stop_timer()
            self.game_state = "won"

    def _flood_fill(self, r, c):
        queue = deque()
        queue.append((r, c))
        self.grid[r][c].is_revealed = True

        while queue:
            cr, cc = queue.popleft()
            for nr, nc in self._neighbors(cr, cc):
                neighbor = self.grid[nr][nc]
                if not neighbor.is_revealed and not neighbor.is_flagged:
                    neighbor.is_revealed = True
                    if neighbor.adjacent_mines == 0:
                        queue.append((nr, nc))

    def _stop_timer(self):
        if self.start_time is not None:
            self.elapsed_time = time.time() - self.start_time

    def get_elapsed(self):
        if self.start_time is None:
            return 0.0
        if self.game_state == "playing":
            return time.time() - self.start_time
        return self.elapsed_time

    def _reveal_all_mines(self):
        for r in range(self.rows):
            for c in range(self.cols):
                cell = self.grid[r][c]
                if cell.has_mine:
                    cell.is_revealed = True

    def chord(self, r, c):
        """좌+우 동시 클릭: 공개된 숫자 셀의 깃발 수 == 숫자이면 나머지 이웃 전부 공개."""
        if self.game_state != "playing":
            return
        if not (0 <= r < self.rows and 0 <= c < self.cols):
            return

        cell = self.grid[r][c]
        if not cell.is_revealed or cell.adjacent_mines == 0:
            return

        flag_count = sum(
            1 for nr, nc in self._neighbors(r, c)
            if self.grid[nr][nc].is_flagged
        )
        if flag_count != cell.adjacent_mines:
            return

        for nr, nc in self._neighbors(r, c):
            neighbor = self.grid[nr][nc]
            if not neighbor.is_revealed and not neighbor.is_flagged:
                self.reveal(nr, nc)
                if self.game_state == "lost":
                    return

    def toggle_flag(self, r, c):
        if self.game_state != "playing":
            return
        if not (0 <= r < self.rows and 0 <= c < self.cols):
            return
        cell = self.grid[r][c]
        if not cell.is_revealed:
            cell.is_flagged = not cell.is_flagged

    def check_win(self):
        for r in range(self.rows):
            for c in range(self.cols):
                cell = self.grid[r][c]
                if not cell.has_mine and not cell.is_revealed:
                    return False
        return True

    def flag_count(self):
        return sum(
            self.grid[r][c].is_flagged
            for r in range(self.rows)
            for c in range(self.cols)
        )
