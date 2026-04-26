"""
loadscreen.py — Controls screen shown between the main menu and game.
Press any key to begin.
"""
import pygame
import sys

from mainmenu import apply_crt, load_bg, make_props, draw_background
from hud import draw_panel

SCREEN_W  = 1280
SCREEN_H  = 720
FONT_PATH = "assets/fonts/AeogoPxltdNext-5y27B.ttf"

TEXT = (200, 220, 255)
CYAN = (100, 200, 255)
DIM  = (130, 150, 190)

CONTROLS = [
    ("ARROW KEYS", "Move"),
    ("G",          "Pick Up Item"),
    ("TAB",        "Cycle Selected Item"),
    ("D",          "Drop Item"),
    ("SPACE",      "Examine"),
    ("U",          "Use Item"),
    ("ESC",        "Quit"),
]

WAIT_MS = 2200


def run(screen, clock):
    layers = [
        {"img": load_bg("blue-back.png"),  "scroll": 0, "speed": 0.4},
        {"img": load_bg("blue-stars.png"), "scroll": 0, "speed": 1.0},
    ]
    props = make_props()

    font_title = pygame.font.Font(FONT_PATH, 68)
    font_key   = pygame.font.Font(FONT_PATH, 26)
    font_desc  = pygame.font.Font(FONT_PATH, 22)

    PANEL_W = 960
    PANEL_H = 480
    PANEL_X = (SCREEN_W - PANEL_W) // 2
    PANEL_Y = (SCREEN_H - PANEL_H) // 2

    key_col_w = max(font_key.size(k)[0] for k, _ in CONTROLS)
    INNER_PAD = 60
    DIV_EXTRA = 40
    KEY_X     = PANEL_X + INNER_PAD
    DESC_X    = KEY_X + key_col_w + DIV_EXTRA
    LINE_H    = 46

    elapsed = 0

    while True:
        dt = clock.tick(60)
        elapsed += dt

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if elapsed >= WAIT_MS:
                    return
            if event.type == pygame.MOUSEBUTTONDOWN and elapsed >= WAIT_MS:
                return

        draw_background(screen, layers, props)
        draw_panel(screen, PANEL_X, PANEL_Y, PANEL_W, PANEL_H)

        # Title
        title_surf = font_title.render("CONTROLS", True, TEXT)
        screen.blit(title_surf, (SCREEN_W // 2 - title_surf.get_width() // 2, PANEL_Y + 30))

        # Divider
        div_y = PANEL_Y + 30 + title_surf.get_height() + 16
        pygame.draw.line(screen, (40, 60, 130),
                         (PANEL_X + 36, div_y), (PANEL_X + PANEL_W - 36, div_y), 2)

        # Controls list
        row_y = div_y + 24
        for key_str, desc_str in CONTROLS:
            key_surf  = font_key.render(key_str,  True, CYAN)
            desc_surf = font_desc.render(desc_str, True, DIM)
            mid = row_y + key_surf.get_height() // 2
            screen.blit(key_surf,  (KEY_X,  row_y))
            screen.blit(desc_surf, (DESC_X, mid - desc_surf.get_height() // 2))
            row_y += LINE_H

        # Vertical separator
        sep_x = KEY_X + key_col_w + DIV_EXTRA // 2
        pygame.draw.line(screen, (30, 50, 110),
                         (sep_x, div_y + 24),
                         (sep_x, div_y + 24 + LINE_H * len(CONTROLS) - 8), 1)

        apply_crt(screen)
        pygame.display.flip()
