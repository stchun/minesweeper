import pygame
import sys

from board import Board
from renderer import Renderer

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
    screen = pygame.display.set_mode((400, 360))
    pygame.display.set_caption("지뢰찾기 - 난이도 선택")

    font_title = _korean_font(34, bold=True)
    font_hint = _korean_font(15)
    font_name = _korean_font(22, bold=True)
    font_sub = _korean_font(14)

    btn_w, btn_h, gap = 260, 58, 14
    total_h = len(DIFFICULTY_ORDER) * btn_h + (len(DIFFICULTY_ORDER) - 1) * gap
    start_y = 360 // 2 - total_h // 2 + 24

    buttons = []
    for i, name in enumerate(DIFFICULTY_ORDER):
        rows, cols, mines = DIFFICULTIES[name]
        x = 400 // 2 - btn_w // 2
        y = start_y + i * (btn_h + gap)
        rect = pygame.Rect(x, y, btn_w, btn_h)
        desc = f"{cols}열 × {rows}행  /  지뢰 {mines}개"
        buttons.append((name, rect, desc))

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
            screen.blit(sub_surf, (rect.x + 18, rect.y + 34))

        pygame.display.flip()
        clock.tick(60)


def handle_click(event, board, renderer):
    # Difficulty buttons
    for name, rect in renderer.difficulty_button_rects.items():
        if rect.collidepoint(event.pos):
            return ("change_difficulty", name)

    # Reset button
    if renderer.reset_button_rect and renderer.reset_button_rect.collidepoint(event.pos):
        board.reset()
        return None

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

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                result = handle_click(event, board, renderer)
                if result and result[0] == "change_difficulty":
                    difficulty = result[1]
                    screen, board, renderer = start_game(difficulty)

        renderer.draw()
        clock.tick(60)


if __name__ == "__main__":
    main()
