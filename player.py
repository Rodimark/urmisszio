"""
player.py — Player sprite loading and drawing for urmisszio
Uses AstronautV2: separate left/right walk sheets + per-direction shadow sprites.
"""
import pygame
import os
import room

BASE_PATH = "assets/models/AstronautV2"
SCALE     = 8    # → ~46×73px, close to the robot's 90px height


# ── Image loading ─────────────────────────────────────────────────────────────

def _load(rel_path):
    img = pygame.image.load(os.path.join(BASE_PATH, rel_path)).convert_alpha()
    w = max(1, img.get_width()  // SCALE)
    h = max(1, img.get_height() // SCALE)
    return pygame.transform.scale(img, (w, h))


def _walk_set(folder, prefix, suffix="", total=8):
    """Load `total` numbered frames, return as a list."""
    return [_load(os.path.join(folder, f"{prefix}{i}{suffix}.png"))
            for i in range(1, total + 1)]


# Module-level sprite tables (populated by init_player after pygame.init)

_FRAMES         = {}   # direction → [idle, walk1 … walk8]
_SHADOW_FRAMES  = {}   # direction → [idle_shadow, walk1_shadow … walk8_shadow]
WALK_FRAMES     = 8


def init_player():
    """
    Call once after pygame.init() AND after pygame.display.set_mode().
    Loads + scales all AstronautV2 animation frames and their shadows.
    """
    global _FRAMES, _SHADOW_FRAMES

    # ── Walk frames ───────────────────────────────────────────────────────────
    walk_f     = _walk_set("Walk_f",     "Astronaut_walk_f")
    walk_b     = _walk_set("Walk_b",     "Walk_b")
    walk_left  = _walk_set("Walk_left",  "Walk_s",  "_left")
    walk_right = _walk_set("Walk_right", "Walk_s",  "_right")

    # ── Stand (idle) frames ───────────────────────────────────────────────────
    stand_f     = _load("Stand/Stand_f.png")
    stand_b     = _load("Stand/Stand_b1.png")
    stand_left  = _load("Stand/Stand_left.png")
    stand_right = _load("Stand/Stand_right.png")

    _FRAMES = {
        "down":  [stand_f]     + walk_f,
        "up":    [stand_b]     + walk_b,
        "left":  [stand_left]  + walk_left,
        "right": [stand_right] + walk_right,
    }

    # ── Shadow frames ─────────────────────────────────────────────────────────
    shad_walk_f     = _walk_set("Shadows/Walk_f",     "Walking_foward_shadow")
    shad_walk_b     = _walk_set("Shadows/Walk_b",     "Walking_back_shadow")
    shad_walk_left  = _walk_set("Shadows/Walk_left",  "Walking_left_shadow")
    shad_walk_right = _walk_set("Shadows/Walk_right", "Walking_right_shadow")

    shad_stand_f     = _load("Shadows/Stand/Stand_f_shadow.png")
    shad_stand_b     = _load("Shadows/Stand/Stand_back_shadow.png")
    shad_stand_left  = _load("Shadows/Stand/Stand_left_shadow.png")
    shad_stand_right = _load("Shadows/Stand/Stand_right_shadow.png")

    _SHADOW_FRAMES = {
        "down":  [shad_stand_f]     + shad_walk_f,
        "up":    [shad_stand_b]     + shad_walk_b,
        "left":  [shad_stand_left]  + shad_walk_left,
        "right": [shad_stand_right] + shad_walk_right,
    }


# ── Drawing ───────────────────────────────────────────────────────────────────

def get_frame(direction, frame_index):
    """Return the correct Surface for this direction + frame (0=idle, 1-8=walk)."""
    f = min(max(frame_index, 0), WALK_FRAMES)
    return _FRAMES[direction][f]


def get_shadow_frame(direction, frame_index):
    """Return the shadow Surface matching get_frame()."""
    f = min(max(frame_index, 0), WALK_FRAMES)
    return _SHADOW_FRAMES[direction][f]


def draw_player(surface, direction, frame_index, player_y, player_x,
                offset_y=0.0, offset_x=0.0):
    """
    Draw shadow then player sprite at tile (player_y, player_x).
    Uses room.draw_image for correct depth-sorting (bottom-aligned blit).
    """
    shadow = get_shadow_frame(direction, frame_index)
    sprite = get_frame(direction, frame_index)

    room.draw_image(surface, shadow, player_y + offset_y, player_x + offset_x)
    room.draw_image(surface, sprite, player_y + offset_y, player_x + offset_x)
