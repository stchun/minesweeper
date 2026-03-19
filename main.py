import pygame
import sys

from board import Board
from renderer import Renderer
import records as rec

CELL_SIZE = 40
TOP_BAR_HEIGHT = 60

# (rows, cols, mines)
DIFFICULTIES = {
    "초급": (9, 9, 10),
    "중급": (16, 16, 40),
    "고급": (16, 30, 99),
}
DIFFICULTY_ORDER = ["초급", "중급", "고급"]


def _korean_font(size, bold=False):
    for name in ["applegothic", "apple sd gothic neo", "malgun gothic"]:
        f = pygame.font.SysFont(name, size, bold=bold)
        if f:
            return f
    return pygame.font.SysFont(None, size, bold=bold)


def show_difficulty_screen():
    screen = pygame.display.set_mode((400, 380))
    pygame.display.set_caption("지뢰찾기 - 난이도 선택")

    font_title = _korean_font(34, bold=True)
    font_hint = _korean_font(15)
    font_name = _korean_font(22, bold=True)
    font_sub = _korean_font(14)
    font_best = _korean_font(13)

    btn_w, btn_h, gap = 260, 70, 14
    total_h = len(DIFFICULTY_ORDER) * btn_h + (len(DIFFICULTY_ORDER) - 1) * gap
    start_y = 380 // 2 - total_h // 2 + 24

    buttons = []
    for i, name in enumerate(DIFFICULTY_ORDER):
        rows, cols, mines = DIFFICULTIES[name]
        x = 400 // 2 - btn_w // 2
        y = start_y + i * (btn_h + gap)
        rect = pygame.Rect(x, y, btn_w, btn_h)
        desc = f"{cols}열 × {rows}행  /  지뢰 {mines}개"
        buttons.append((name, rect, desc))

    records_data = rec.load_records()
    clock = pygame.time.Clock()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for name, rect, _ in buttons:
                    if rect.collidepoint(event.pos):
                        return name

        screen.fill((192, 192, 192))

        title = font_title.render("지뢰찾기", True, (0, 0, 0))
        screen.blit(title, (400 // 2 - title.get_width() // 2, start_y - 66))

        hint = font_hint.render("난이도를 선택하세요", True, (64, 64, 64))
        screen.blit(hint, (400 // 2 - hint.get_width() // 2, start_y - 34))
        mx, my = pygame.mouse.get_pos()
        for name, rect, desc in buttons:
            hovered = rect.collidepoint(mx, my)
            pygame.draw.rect(screen, (210, 210, 210) if hovered else (192, 192, 192), rect)
            lw = 3
            pygame.draw.line(screen, (255, 255, 255), rect.topleft, (rect.right - 1, rect.top), lw)
            pygame.draw.line(screen, (255, 255, 255), rect.topleft, (rect.left, rect.bottom - 1), lw)
            pygame.draw.line(screen, (128, 128, 128), (rect.left, rect.bottom - 1), (rect.right - 1, rect.bottom - 1), lw)
            pygame.draw.line(screen, (128, 128, 128), (rect.right - 1, rect.top), (rect.right - 1, rect.bottom - 1), lw)

            name_surf = font_name.render(name, True, (0, 0, 0))
            sub_surf = font_sub.render(desc, True, (80, 80, 80))
            screen.blit(name_surf, (rect.x + 18, rect.y + 8))
            screen.blit(sub_surf, (rect.x + 18, rect.y + 30))

            best_list = records_data.get(name, [])
            if best_list:
                best_str = f"최고 기록: {rec.format_time(best_list[0])}"
                best_color = (0, 80, 180)
            else:
                best_str = "기록 없음"
                best_color = (140, 140, 140)
            best_surf = font_best.render(best_str, True, best_color)
            screen.blit(best_surf, (rect.x + 18, rect.y + 50))

        pygame.display.flip()
        clock.tick(60)


def handle_click(event, board, renderer):
    # Records button
    if renderer.records_button_rect and renderer.records_button_rect.collidepoint(event.pos):
        return ("show_leaderboard", None)

    # Difficulty buttons
    for name, rect in renderer.difficulty_button_rects.items():
        if rect.collidepoint(event.pos):
            return ("change_difficulty", name)

    # Reset button
    if renderer.reset_button_rect and renderer.reset_button_rect.collidepoint(event.pos):
        board.reset()
        return ("reset", None)

    if board.game_state != "playing":
        return None

    mx, my = event.pos
    if my < TOP_BAR_HEIGHT:
        return None

    col = mx // CELL_SIZE
    row = (my - TOP_BAR_HEIGHT) // CELL_SIZE

    if not (0 <= row < board.rows and 0 <= col < board.cols):
        return None

    buttons = pygame.mouse.get_pressed()

    if buttons[0] and buttons[2]:
        board.chord(row, col)
    elif event.button == 1:
        board.reveal(row, col)
    elif event.button == 3:
        board.toggle_flag(row, col)

    return None


def show_leaderboard_overlay(screen, current_difficulty):
    bg = screen.copy()
    clock = pygame.time.Clock()

    font_title = _korean_font(24, bold=True)
    font_tab = _korean_font(15, bold=True)
    font_row = _korean_font(16)
    font_btn = _korean_font(18, bold=True)

    selected = current_difficulty
    records_data = rec.load_records()

    panel_w = 280
    panel_h = 300
    sw, sh = screen.get_size()
    panel_x = sw // 2 - panel_w // 2
    panel_y = sh // 2 - panel_h // 2
    panel_rect = pygame.Rect(panel_x, panel_y, panel_w, panel_h)

    tab_w, tab_h, tab_gap = 72, 28, 6
    tab_total_w = len(DIFFICULTY_ORDER) * tab_w + (len(DIFFICULTY_ORDER) - 1) * tab_gap
    tab_start_x = panel_x + panel_w // 2 - tab_total_w // 2
    tab_y = panel_y + 46
    tab_rects = {name: pygame.Rect(tab_start_x + i * (tab_w + tab_gap), tab_y, tab_w, tab_h)
                 for i, name in enumerate(DIFFICULTY_ORDER)}

    btn_w, btn_h = 100, 36
    btn_rect = pygame.Rect(
        panel_x + panel_w // 2 - btn_w // 2,
        panel_y + panel_h - btn_h - 14,
        btn_w, btn_h
    )

    overlay = pygame.Surface((sw, sh), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 140))

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for name, rect in tab_rects.items():
                    if rect.collidepoint(event.pos):
                        selected = name
                if btn_rect.collidepoint(event.pos):
                    running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_SPACE):
                    running = False

        screen.blit(bg, (0, 0))
        screen.blit(overlay, (0, 0))

        # Panel
        pygame.draw.rect(screen, (192, 192, 192), panel_rect)
        lw = 3
        pygame.draw.line(screen, (255, 255, 255), panel_rect.topleft, (panel_rect.right - 1, panel_rect.top), lw)
        pygame.draw.line(screen, (255, 255, 255), panel_rect.topleft, (panel_rect.left, panel_rect.bottom - 1), lw)
        pygame.draw.line(screen, (128, 128, 128), (panel_rect.left, panel_rect.bottom - 1), (panel_rect.right - 1, panel_rect.bottom - 1), lw)
        pygame.draw.line(screen, (128, 128, 128), (panel_rect.right - 1, panel_rect.top), (panel_rect.right - 1, panel_rect.bottom - 1), lw)

        cx = panel_x + panel_w // 2

        # Title
        title_surf = font_title.render("순위 기록", True, (0, 0, 0))
        screen.blit(title_surf, (cx - title_surf.get_width() // 2, panel_y + 12))

        # Tabs
        for name, rect in tab_rects.items():
            is_sel = (name == selected)
            pygame.draw.rect(screen, (155, 155, 155) if is_sel else (192, 192, 192), rect)
            if is_sel:
                pygame.draw.line(screen, (128, 128, 128), rect.topleft, (rect.right - 1, rect.top), 2)
                pygame.draw.line(screen, (128, 128, 128), rect.topleft, (rect.left, rect.bottom - 1), 2)
                pygame.draw.line(screen, (255, 255, 255), (rect.left, rect.bottom - 1), (rect.right - 1, rect.bottom - 1), 2)
                pygame.draw.line(screen, (255, 255, 255), (rect.right - 1, rect.top), (rect.right - 1, rect.bottom - 1), 2)
            else:
                pygame.draw.line(screen, (255, 255, 255), rect.topleft, (rect.right - 1, rect.top), 2)
                pygame.draw.line(screen, (255, 255, 255), rect.topleft, (rect.left, rect.bottom - 1), 2)
                pygame.draw.line(screen, (128, 128, 128), (rect.left, rect.bottom - 1), (rect.right - 1, rect.bottom - 1), 2)
                pygame.draw.line(screen, (128, 128, 128), (rect.right - 1, rect.top), (rect.right - 1, rect.bottom - 1), 2)
            tab_text = font_tab.render(name, True, (0, 0, 0))
            screen.blit(tab_text, (rect.centerx - tab_text.get_width() // 2,
                                   rect.centery - tab_text.get_height() // 2))

        # Divider
        div_y = tab_y + tab_h + 8
        pygame.draw.line(screen, (128, 128, 128), (panel_x + 16, div_y), (panel_x + panel_w - 16, div_y), 1)

        # Records list
        lst = records_data.get(selected, [])
        y = div_y + 12
        if lst:
            for i, t in enumerate(lst):
                row_surf = font_row.render(f"  {i + 1}위   {rec.format_time(t)}", True, (0, 0, 0))
                screen.blit(row_surf, (panel_x + 20, y))
                y += 26
        else:
            empty_surf = font_row.render("기록이 없습니다", True, (120, 120, 120))
            screen.blit(empty_surf, (cx - empty_surf.get_width() // 2, y + 20))

        # Close button
        mx, my = pygame.mouse.get_pos()
        btn_color = (210, 210, 210) if btn_rect.collidepoint(mx, my) else (192, 192, 192)
        pygame.draw.rect(screen, btn_color, btn_rect)
        pygame.draw.line(screen, (255, 255, 255), btn_rect.topleft, (btn_rect.right - 1, btn_rect.top), 2)
        pygame.draw.line(screen, (255, 255, 255), btn_rect.topleft, (btn_rect.left, btn_rect.bottom - 1), 2)
        pygame.draw.line(screen, (128, 128, 128), (btn_rect.left, btn_rect.bottom - 1), (btn_rect.right - 1, btn_rect.bottom - 1), 2)
        pygame.draw.line(screen, (128, 128, 128), (btn_rect.right - 1, btn_rect.top), (btn_rect.right - 1, btn_rect.bottom - 1), 2)
        btn_text = font_btn.render("닫기", True, (0, 0, 0))
        screen.blit(btn_text, (btn_rect.centerx - btn_text.get_width() // 2,
                                btn_rect.centery - btn_text.get_height() // 2))

        pygame.display.flip()
        clock.tick(60)


def show_win_overlay(screen, difficulty, elapsed, rank, records_list):
    bg = screen.copy()
    clock = pygame.time.Clock()

    font_title = _korean_font(28, bold=True)
    font_body = _korean_font(18)
    font_row = _korean_font(16)
    font_btn = _korean_font(18, bold=True)

    row_h = 26
    n = len(records_list)
    panel_w = 280
    panel_h = 56 + 28 + 26 + 14 + 22 + 8 + n * row_h + 16 + 44 + 14
    sw, sh = screen.get_size()
    panel_x = sw // 2 - panel_w // 2
    panel_y = sh // 2 - panel_h // 2
    panel_rect = pygame.Rect(panel_x, panel_y, panel_w, panel_h)

    btn_w, btn_h = 100, 36
    btn_rect = pygame.Rect(
        panel_x + panel_w // 2 - btn_w // 2,
        panel_y + panel_h - btn_h - 14,
        btn_w, btn_h
    )

    overlay = pygame.Surface((sw, sh), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 140))

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if btn_rect.collidepoint(event.pos):
                    running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_ESCAPE):
                    running = False

        screen.blit(bg, (0, 0))
        screen.blit(overlay, (0, 0))

        # Panel
        pygame.draw.rect(screen, (192, 192, 192), panel_rect)
        lw = 3
        pygame.draw.line(screen, (255, 255, 255), panel_rect.topleft, (panel_rect.right - 1, panel_rect.top), lw)
        pygame.draw.line(screen, (255, 255, 255), panel_rect.topleft, (panel_rect.left, panel_rect.bottom - 1), lw)
        pygame.draw.line(screen, (128, 128, 128), (panel_rect.left, panel_rect.bottom - 1), (panel_rect.right - 1, panel_rect.bottom - 1), lw)
        pygame.draw.line(screen, (128, 128, 128), (panel_rect.right - 1, panel_rect.top), (panel_rect.right - 1, panel_rect.bottom - 1), lw)

        cx = panel_x + panel_w // 2
        y = panel_y + 16

        # Title
        title_surf = font_title.render("클리어!", True, (0, 0, 180))
        screen.blit(title_surf, (cx - title_surf.get_width() // 2, y))
        y += title_surf.get_height() + 10

        # Time
        time_surf = font_body.render(f"시간: {rec.format_time(elapsed)}", True, (0, 0, 0))
        screen.blit(time_surf, (cx - time_surf.get_width() // 2, y))
        y += time_surf.get_height() + 6

        # Rank message
        if rank is not None:
            rank_surf = font_row.render(f"★  {rank}위 기록 달성!", True, (160, 100, 0))
            screen.blit(rank_surf, (cx - rank_surf.get_width() // 2, y))
        y += 26

        # Divider
        pygame.draw.line(screen, (128, 128, 128), (panel_x + 16, y), (panel_x + panel_w - 16, y), 1)
        y += 8

        # Records header
        header_surf = font_row.render(f"─  {difficulty} 순위 기록  ─", True, (60, 60, 60))
        screen.blit(header_surf, (cx - header_surf.get_width() // 2, y))
        y += header_surf.get_height() + 8

        # Records list
        for i, t in enumerate(records_list):
            r_num = i + 1
            is_new = (rank is not None and r_num == rank)
            color = (0, 0, 200) if is_new else (0, 0, 0)
            new_marker = "  ◀" if is_new else ""
            row_str = f"  {r_num}위   {rec.format_time(t)}{new_marker}"
            row_surf = font_row.render(row_str, True, color)
            screen.blit(row_surf, (panel_x + 20, y))
            y += row_h

        # Confirm button
        mx, my = pygame.mouse.get_pos()
        btn_color = (210, 210, 210) if btn_rect.collidepoint(mx, my) else (192, 192, 192)
        pygame.draw.rect(screen, btn_color, btn_rect)
        pygame.draw.line(screen, (255, 255, 255), btn_rect.topleft, (btn_rect.right - 1, btn_rect.top), 2)
        pygame.draw.line(screen, (255, 255, 255), btn_rect.topleft, (btn_rect.left, btn_rect.bottom - 1), 2)
        pygame.draw.line(screen, (128, 128, 128), (btn_rect.left, btn_rect.bottom - 1), (btn_rect.right - 1, btn_rect.bottom - 1), 2)
        pygame.draw.line(screen, (128, 128, 128), (btn_rect.right - 1, btn_rect.top), (btn_rect.right - 1, btn_rect.bottom - 1), 2)
        btn_text = font_btn.render("확인", True, (0, 0, 0))
        screen.blit(btn_text, (btn_rect.centerx - btn_text.get_width() // 2,
                                btn_rect.centery - btn_text.get_height() // 2))

        pygame.display.flip()
        clock.tick(60)


def start_game(difficulty):
    rows, cols, num_mines = DIFFICULTIES[difficulty]
    screen = pygame.display.set_mode((cols * CELL_SIZE, rows * CELL_SIZE + TOP_BAR_HEIGHT))
    pygame.display.set_caption("지뢰찾기")
    board = Board(rows, cols, num_mines)
    renderer = Renderer(screen, board, CELL_SIZE, TOP_BAR_HEIGHT, difficulty)
    return screen, board, renderer


def main():
    pygame.init()

    difficulty = show_difficulty_screen()
    screen, board, renderer = start_game(difficulty)

    clock = pygame.time.Clock()
    records_shown = False

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                result = handle_click(event, board, renderer)
                if result:
                    if result[0] == "change_difficulty":
                        difficulty = result[1]
                        screen, board, renderer = start_game(difficulty)
                        records_shown = False
                    elif result[0] == "reset":
                        records_shown = False
                    elif result[0] == "show_leaderboard":
                        renderer.draw()
                        show_leaderboard_overlay(screen, difficulty)

        renderer.draw()

        if board.game_state == "won" and not records_shown:
            records_shown = True
            elapsed = board.get_elapsed()
            rank, records_list = rec.save_record(difficulty, elapsed)
            show_win_overlay(screen, difficulty, elapsed, rank, records_list)

        clock.tick(60)


if __name__ == "__main__":
    main()
