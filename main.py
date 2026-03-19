import pygame
import sys

from board import Board
from renderer import Renderer

ROWS, COLS = 9, 9
NUM_MINES = 10
CELL_SIZE = 40
TOP_BAR_HEIGHT = 60
WINDOW_WIDTH = COLS * CELL_SIZE        # 360
WINDOW_HEIGHT = ROWS * CELL_SIZE + TOP_BAR_HEIGHT  # 420


def handle_click(event, board, renderer):
    if renderer.reset_button_rect and renderer.reset_button_rect.collidepoint(event.pos):
        board.reset()
        return

    if board.game_state != "playing":
        return

    mx, my = event.pos
    if my < TOP_BAR_HEIGHT:
        return

    col = mx // CELL_SIZE
    row = (my - TOP_BAR_HEIGHT) // CELL_SIZE

    if not (0 <= row < ROWS and 0 <= col < COLS):
        return

    if event.button == 1:
        board.reveal(row, col)
    elif event.button == 3:
        board.toggle_flag(row, col)


def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Minesweeper")
    clock = pygame.time.Clock()

    board = Board(ROWS, COLS, NUM_MINES)
    renderer = Renderer(screen, board, CELL_SIZE, TOP_BAR_HEIGHT)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                handle_click(event, board, renderer)

        renderer.draw()
        clock.tick(60)


if __name__ == "__main__":
    main()
