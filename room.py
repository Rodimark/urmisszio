"""
room.py — Room generation and drawing for urmisszio
Ported from Mission Python by Sean McManus (pygame zero → pygame)
"""
import pygame
import os

from data import (
    GAME_MAP, OBJECTS, SCENERY, PROPS, outdoor_rooms,
    items_player_may_stand_on, TILE_SIZE, MAP_WIDTH, MAP_SIZE,
    HUD_TOP_H,
)

SCREEN_W = 1280
SCREEN_H = 720
TS       = TILE_SIZE
_WIDE    = 255   # marks extra tiles of a wide object (not walkable, not drawn)

# ── Image cache ───────────────────────────────────────────────────────────────

_cache = {}

def img(name):
    if name not in _cache:
        path = os.path.join("assets", "images", name + ".png")
        _cache[name] = pygame.image.load(path).convert_alpha()
    return _cache[name]

# ── Wall transparency pillar frames (loaded after pygame.init) ────────────────

PILLARS = []

def init_pillars():
    """Call once after pygame.init() — loads the transparency pillar frames."""
    global PILLARS
    PILLARS = [
        img("pillar"),
        img("pillar_95"),
        img("pillar_80"),
        img("pillar_60"),
        img("pillar_50"),
    ]

# ── Module-level room state (mirrors MissionPython's globals) ─────────────────

room_map              = []
room_width            = 0
room_height           = 0
room_name             = ""
top_left_x            = 0
top_left_y            = 0
hazard_map            = []
wall_transparency_frame = 0

# ── Floor / edge helpers ──────────────────────────────────────────────────────

def get_floor_type(current_room):
    return 2 if current_room in outdoor_rooms else 0

def _get_edge_types(current_room):
    """Returns (bottom_edge, side_edge) tile IDs for this room type."""
    if current_room in range(1, 21):
        return 2, 2   # soil bottom, soil sides
    elif current_room in range(21, 26):
        return 1, 2   # wall bottom, soil sides
    else:
        return 1, 1   # wall bottom, wall sides

# ── Map generation ────────────────────────────────────────────────────────────

def generate_map(current_room):
    """
    Build the room grid for current_room.
    Faithful to MissionPython's generate_map() — same exit logic,
    same scenery/prop placement, same 255 wide-object markers.
    Updates module-level state (room_map, room_width, etc.).
    """
    global room_map, room_width, room_height, room_name
    global top_left_x, top_left_y, hazard_map, wall_transparency_frame

    room_data   = GAME_MAP[current_room]
    room_name   = room_data["name"]
    room_height = room_data["h"]
    room_width  = room_data["w"]

    floor_type              = get_floor_type(current_room)
    bottom_edge, side_edge  = _get_edge_types(current_room)

    # ── Build grid ────────────────────────────────────────────────────────────
    room_map = [[side_edge] * room_width]
    for _ in range(room_height - 2):
        room_map.append([side_edge] + [floor_type] * (room_width - 2) + [side_edge])
    room_map.append([bottom_edge] * room_width)

    middle_row = room_height // 2
    middle_col = room_width  // 2

    # ── Exits ─────────────────────────────────────────────────────────────────

    # Right exit
    if room_data["right"]:
        room_map[middle_row - 1][room_width - 1] = floor_type
        room_map[middle_row    ][room_width - 1] = floor_type
        room_map[middle_row + 1][room_width - 1] = floor_type

    # Left exit — derived from the left neighbour's right exit
    if current_room % MAP_WIDTH != 1:
        if GAME_MAP[current_room - 1]["right"]:
            room_map[middle_row - 1][0] = floor_type
            room_map[middle_row    ][0] = floor_type
            room_map[middle_row + 1][0] = floor_type

    # Top exit
    if room_data["top"]:
        room_map[0][middle_col - 1] = floor_type
        room_map[0][middle_col    ] = floor_type
        room_map[0][middle_col + 1] = floor_type

    # Bottom exit — derived from the room below's top exit
    if current_room <= MAP_SIZE - MAP_WIDTH:
        if GAME_MAP[current_room + MAP_WIDTH]["top"]:
            room_map[room_height - 1][middle_col - 1] = floor_type
            room_map[room_height - 1][middle_col    ] = floor_type
            room_map[room_height - 1][middle_col + 1] = floor_type

    # ── Scenery ───────────────────────────────────────────────────────────────
    for scenery_item in SCENERY.get(current_room, []):
        obj_id, sy, sx = scenery_item
        room_map[sy][sx] = obj_id
        w = img(OBJECTS[obj_id][0]).get_width() // TS
        for t in range(1, w):
            room_map[sy][sx + t] = _WIDE

    # ── Props ─────────────────────────────────────────────────────────────────
    for obj_id, info in PROPS.items():
        p_room, py, px = info
        if p_room == current_room and room_map[py][px] in [0, 39, 2]:
            room_map[py][px] = obj_id
            w = img(OBJECTS[obj_id][0]).get_width() // TS
            for t in range(1, w):
                room_map[py][px + t] = _WIDE

    # ── Position room on screen ───────────────────────────────────────────────
    top_left_x = (SCREEN_W - room_width  * TS) // 2
    top_left_y = HUD_TOP_H + (SCREEN_H - HUD_TOP_H - room_height * TS) // 2

    # ── Reset hazard map ──────────────────────────────────────────────────────
    hazard_map = [[0] * room_width for _ in range(room_height)]

    wall_transparency_frame = 0


# ── Collision ─────────────────────────────────────────────────────────────────

def get_wall_rects():
    """Return solid pygame.Rect list — everything the player can't walk on."""
    rects = []
    for row in range(room_height):
        for col in range(room_width):
            tile = room_map[row][col]
            if tile not in items_player_may_stand_on and tile != _WIDE:
                rects.append(pygame.Rect(
                    top_left_x + col * TS,
                    top_left_y + row * TS,
                    TS, TS
                ))
    return rects


# ── Drawing helpers ───────────────────────────────────────────────────────────

def draw_image(surface, image, y, x):
    """Bottom-aligned blit — tall objects rise upward from their tile."""
    surface.blit(image, (
        top_left_x + x * TS,
        top_left_y + y * TS - image.get_height()
    ))

def draw_shadow(surface, image, y, x):
    surface.blit(image, (
        top_left_x + x * TS,
        top_left_y + y * TS
    ))


# ── Main draw ─────────────────────────────────────────────────────────────────

def draw_room(surface, current_room, player_y, draw_player_fn, hazard_draws=None):
    """
    Two-pass draw — faithful to MissionPython's draw().
    draw_player_fn(surface) is called when row == player_y so the
    player renders at the correct depth between rows.
    hazard_draws: list of (obj_id, float_y, float_x) from hazards.get_hazard_draws()
                  — used for smooth sub-tile interpolation.
    """
    floor_type = get_floor_type(current_room)
    floor_img  = img(OBJECTS[floor_type][0])

    # Clip to the game area so nothing bleeds over the HUD
    clip = pygame.Rect(0, 0, SCREEN_W, top_left_y + (room_height - 1) * TS)
    surface.set_clip(clip)

    # ── Pass 1: floor tiles + items the player can stand on ──────────────────
    for y in range(room_height):
        for x in range(room_width):
            draw_image(surface, floor_img, y, x)
            tile = room_map[y][x]
            if tile in items_player_may_stand_on:
                draw_image(surface, img(OBJECTS[tile][0]), y, x)

    # Room 26 pressure pad (drawn separately so props can sit on top)
    if current_room == 26:
        draw_image(surface, img(OBJECTS[39][0]), 8, 2)
        pad_item = room_map[8][2]
        if pad_item > 0:
            draw_image(surface, img(OBJECTS[pad_item][0]), 8, 2)

    # ── Pass 2: tall objects + shadows + hazards + player at correct row ──────
    for y in range(room_height):

        # Draw hazards at this depth row using interpolated float positions
        if hazard_draws:
            for obj_id, hy, hx in hazard_draws:
                if round(hy) == y:
                    draw_image(surface, img(OBJECTS[obj_id][0]), hy, hx)

        for x in range(room_width):
            tile = room_map[y][x]
            if tile in items_player_may_stand_on or tile in (0, 2, _WIDE):
                continue
            if tile not in OBJECTS:
                continue

            obj   = OBJECTS[tile]
            image = img(obj[0])

            # Front-row wall transparency when player is near it
            if y == room_height - 1 and tile == 1:
                if current_room in outdoor_rooms or (0 < x < room_width - 1):
                    if PILLARS:
                        image = PILLARS[wall_transparency_frame]

            draw_image(surface, image, y, x)

            # Shadow
            if obj[1]:
                shad   = img(obj[1])
                tile_w = img(obj[0]).get_width() // TS
                if obj[1] in ("half_shadow", "full_shadow"):
                    for z in range(tile_w):
                        draw_shadow(surface, shad, y, x + z)
                else:
                    draw_shadow(surface, shad, y, x)

        if y == player_y:
            draw_player_fn(surface)

    surface.set_clip(None)


# ── Wall transparency ─────────────────────────────────────────────────────────

def adjust_wall_transparency(player_y, player_x):
    global wall_transparency_frame
    near_front = (
        player_y == room_height - 2
        and room_map[room_height - 1][player_x] == 1
    )
    if near_front and wall_transparency_frame < 4:
        wall_transparency_frame += 1
    if not near_front and wall_transparency_frame > 0:
        wall_transparency_frame -= 1
