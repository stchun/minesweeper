import pygame

NUMBER_COLORS = {
    1: (0, 0, 255),
    2: (0, 128, 0),
    3: (255, 0, 0),
    4: (0, 0, 128),
    5: (128, 0, 0),
    6: (0, 128, 128),
    7: (0, 0, 0),
    8: (128, 128, 128),
}

COLOR_BG = (192, 192, 192)
COLOR_UNREVEALED = (192, 192, 192)
COLOR_REVEALED = (160, 160, 160)
COLOR_BORDER_LIGHT = (255, 255, 255)
COLOR_BORDER_DARK = (128, 128, 128)
COLOR_MINE_TRIGGERED = (255, 0, 0)


DIFFICULTY_ORDER = ["초급", "중급", "고급"]


def _korean_font(size, bold=False):
    for name in ["applegothic", "apple sd gothic neo", "malgun gothic"]:
        f = pygame.font.SysFont(name, size, bold=bold)
        if f:
            return f
    return pygame.font.SysFont(None, size, bold=bold)


class Renderer:
    def __init__(self, screen, board, cell_size, top_bar_height, current_difficulty="초급"):
        self.screen = screen
        self.board = board
        self.cell_size = cell_size
        self.top_bar_height = top_bar_height
        self.current_difficulty = current_difficulty
        self.font = pygame.font.SysFont("Arial", cell_size // 2, bold=True)
        self.font_large = pygame.font.SysFont("Arial", top_bar_height // 2, bold=True)
        self.font_diff = _korean_font(12, bold=True)
        self.reset_button_rect = None
        self.difficulty_button_rects = {}
        self.records_button_rect = None

    def draw(self):
        self.screen.fill(COLOR_BG)
        self._draw_top_bar()
        self._draw_grid()
        pygame.display.flip()

    def _draw_top_bar(self):
        bar_rect = pygame.Rect(0, 0, self.screen.get_width(), self.top_bar_height)
        pygame.draw.rect(self.screen, COLOR_BG, bar_rect)

        # 3D bevel for top bar
        pygame.draw.line(self.screen, COLOR_BORDER_LIGHT, (0, 0), (self.screen.get_width(), 0), 2)
        pygame.draw.line(self.screen, COLOR_BORDER_LIGHT, (0, 0), (0, self.top_bar_height), 2)
        pygame.draw.line(self.screen, COLOR_BORDER_DARK,
                         (0, self.top_bar_height - 1), (self.screen.get_width(), self.top_bar_height - 1), 2)
        pygame.draw.line(self.screen, COLOR_BORDER_DARK,
                         (self.screen.get_width() - 1, 0), (self.screen.get_width() - 1, self.top_bar_height), 2)

        # Mine counter
        remaining = self.board.num_mines - self.board.flag_count()
        mine_text = self.font_large.render(f"{remaining:03d}", True, (255, 0, 0), (0, 0, 0))
        mine_y = self.top_bar_height // 2 - mine_text.get_height() // 2
        self.screen.blit(mine_text, (10, mine_y))

        # Timer
        elapsed = int(min(self.board.get_elapsed(), 999))
        timer_surf = self.font_large.render(f"{elapsed:03d}", True, (255, 0, 0), (0, 0, 0))
        timer_x = 10 + mine_text.get_width() + 10
        self.screen.blit(timer_surf, (timer_x, mine_y))

        # Reset button
        btn_size = self.top_bar_height - 16
        btn_x = self.screen.get_width() // 2 - btn_size // 2
        btn_y = 8
        self.reset_button_rect = pygame.Rect(btn_x, btn_y, btn_size, btn_size)
        pygame.draw.rect(self.screen, COLOR_UNREVEALED, self.reset_button_rect)
        self._draw_bevel(self.reset_button_rect, 3)

        state = self.board.game_state
        if state == "won":
            label = "😎" if False else "W"
            color = (0, 180, 0)
        elif state == "lost":
            label = "X"
            color = (200, 0, 0)
        else:
            label = ":)"
            color = (0, 0, 0)

        btn_font = pygame.font.SysFont("Arial", btn_size - 10, bold=True)
        text_surf = btn_font.render(label, True, color)
        tx = btn_x + btn_size // 2 - text_surf.get_width() // 2
        ty = btn_y + btn_size // 2 - text_surf.get_height() // 2
        self.screen.blit(text_surf, (tx, ty))

        self._draw_difficulty_buttons()

    def _draw_difficulty_buttons(self):
        btn_w, btn_h, gap = 30, 28, 4
        right_margin = 8
        rec_btn_w = 30
        rec_gap = 8
        diff_total_w = len(DIFFICULTY_ORDER) * btn_w + (len(DIFFICULTY_ORDER) - 1) * gap
        total_w = rec_btn_w + rec_gap + diff_total_w
        start_x = self.screen.get_width() - right_margin - total_w
        btn_y = self.top_bar_height // 2 - btn_h // 2

        # Records button
        rec_rect = pygame.Rect(start_x, btn_y, rec_btn_w, btn_h)
        self.records_button_rect = rec_rect
        pygame.draw.rect(self.screen, (192, 192, 192), rec_rect)
        self._draw_bevel(rec_rect, 2)
        rec_label = self.font_diff.render("기", True, (0, 0, 150))
        self.screen.blit(rec_label, (rec_rect.centerx - rec_label.get_width() // 2,
                                     rec_rect.centery - rec_label.get_height() // 2))

        # Difficulty buttons
        diff_start_x = start_x + rec_btn_w + rec_gap
        self.difficulty_button_rects = {}
        for i, name in enumerate(DIFFICULTY_ORDER):
            x = diff_start_x + i * (btn_w + gap)
            rect = pygame.Rect(x, btn_y, btn_w, btn_h)
            self.difficulty_button_rects[name] = rect

            is_current = (name == self.current_difficulty)
            color = (155, 155, 155) if is_current else (192, 192, 192)
            pygame.draw.rect(self.screen, color, rect)

            if is_current:
                # Depressed (inverted bevel)
                pygame.draw.line(self.screen, COLOR_BORDER_DARK, rect.topleft, (rect.right - 1, rect.top), 2)
                pygame.draw.line(self.screen, COLOR_BORDER_DARK, rect.topleft, (rect.left, rect.bottom - 1), 2)
                pygame.draw.line(self.screen, COLOR_BORDER_LIGHT, (rect.left, rect.bottom - 1), (rect.right - 1, rect.bottom - 1), 2)
                pygame.draw.line(self.screen, COLOR_BORDER_LIGHT, (rect.right - 1, rect.top), (rect.right - 1, rect.bottom - 1), 2)
            else:
                self._draw_bevel(rect, 2)

            label = name[0]  # 초, 중, 고
            text = self.font_diff.render(label, True, (0, 0, 0))
            self.screen.blit(text, (x + btn_w // 2 - text.get_width() // 2,
                                    btn_y + btn_h // 2 - text.get_height() // 2))

    def _draw_grid(self):
        for r in range(self.board.rows):
            for c in range(self.board.cols):
                self._draw_cell(r, c)

    def _draw_cell(self, row, col):
        x = col * self.cell_size
        y = self.top_bar_height + row * self.cell_size
        rect = pygame.Rect(x, y, self.cell_size, self.cell_size)
        cell = self.board.grid[row][col]

        if cell.is_revealed:
            self._draw_revealed(rect, cell, row, col)
        else:
            self._draw_unrevealed(rect, cell)

    def _draw_revealed(self, rect, cell, row, col):
        if cell.has_mine and self.board.triggered_mine == (row, col):
            pygame.draw.rect(self.screen, COLOR_MINE_TRIGGERED, rect)
        else:
            pygame.draw.rect(self.screen, COLOR_REVEALED, rect)

        pygame.draw.rect(self.screen, COLOR_BORDER_DARK, rect, 1)

        if cell.has_mine:
            self._draw_mine(rect)
        elif cell.adjacent_mines > 0:
            color = NUMBER_COLORS.get(cell.adjacent_mines, (0, 0, 0))
            text = self.font.render(str(cell.adjacent_mines), True, color)
            tx = rect.x + self.cell_size // 2 - text.get_width() // 2
            ty = rect.y + self.cell_size // 2 - text.get_height() // 2
            self.screen.blit(text, (tx, ty))

    def _draw_unrevealed(self, rect, cell):
        pygame.draw.rect(self.screen, COLOR_UNREVEALED, rect)
        self._draw_bevel(rect, 2)
        if cell.is_flagged:
            self._draw_flag(rect)

    def _draw_bevel(self, rect, width):
        # Light edges (top, left)
        pygame.draw.line(self.screen, COLOR_BORDER_LIGHT,
                         rect.topleft, (rect.right - 1, rect.top), width)
        pygame.draw.line(self.screen, COLOR_BORDER_LIGHT,
                         rect.topleft, (rect.left, rect.bottom - 1), width)
        # Dark edges (bottom, right)
        pygame.draw.line(self.screen, COLOR_BORDER_DARK,
                         (rect.left, rect.bottom - 1), (rect.right - 1, rect.bottom - 1), width)
        pygame.draw.line(self.screen, COLOR_BORDER_DARK,
                         (rect.right - 1, rect.top), (rect.right - 1, rect.bottom - 1), width)

    def _draw_flag(self, rect):
        cx = rect.x + self.cell_size // 2
        cy = rect.y + self.cell_size // 2
        pole_x = cx - 2
        pole_top = cy - self.cell_size // 3
        pole_bottom = cy + self.cell_size // 3

        # Vertical pole
        pygame.draw.line(self.screen, (0, 0, 0), (pole_x, pole_top), (pole_x, pole_bottom), 2)

        # Red triangle flag
        flag_points = [
            (pole_x, pole_top),
            (pole_x + self.cell_size // 3, pole_top + self.cell_size // 6),
            (pole_x, pole_top + self.cell_size // 3),
        ]
        pygame.draw.polygon(self.screen, (255, 0, 0), flag_points)

        # Base
        base_y = pole_bottom
        pygame.draw.line(self.screen, (0, 0, 0),
                         (pole_x - self.cell_size // 5, base_y),
                         (pole_x + self.cell_size // 5, base_y), 2)

    def _draw_mine(self, rect):
        import math
        cx = rect.centerx
        cy = rect.centery
        radius = self.cell_size // 4

        pygame.draw.circle(self.screen, (0, 0, 0), (cx, cy), radius)

        # 8 radial spikes
        for i in range(8):
            angle = math.radians(i * 45)
            x1 = cx + int(math.cos(angle) * (radius - 1))
            y1 = cy + int(math.sin(angle) * (radius - 1))
            x2 = cx + int(math.cos(angle) * (radius + 4))
            y2 = cy + int(math.sin(angle) * (radius + 4))
            pygame.draw.line(self.screen, (0, 0, 0), (x1, y1), (x2, y2), 2)

        # Highlight
        pygame.draw.circle(self.screen, (255, 255, 255), (cx - radius // 3, cy - radius // 3), radius // 4)
