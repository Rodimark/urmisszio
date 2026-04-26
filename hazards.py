"""
hazards.py — Moving energy-ball hazards for urmisszio
Ported from Mission Python by Sean McManus (pygame zero → pygame)

Collision uses integer grid positions (hazard_map).
Rendering uses sub-tile interpolation so movement is smooth at 60fps.
"""
from data import items_player_may_stand_on, HAZARD_DATA
import room

HAZARD_FRAME_MS = 150   # ms per hazard step (matches MissionPython's 0.15 s)

# ── Module-level state ────────────────────────────────────────────────────────

_active_hazards = []   # reference into HAZARD_DATA[current_room]
_hazard_visual  = []   # parallel list: [[prev_y, prev_x, anim_t], ...]
                       # anim_t goes 0→1 between steps for smooth lerp
_timer          = 0
_active         = False

# ── Public API ────────────────────────────────────────────────────────────────

def hazard_start(current_room):
    """
    Initialise hazards for the room just entered.
    Places hazards on hazard_map at their current positions.
    Call once after generate_map() (so hazard_map is freshly zeroed).
    """
    global _active_hazards, _hazard_visual, _timer, _active
    _active_hazards = []
    _hazard_visual  = []
    _active         = False
    _timer          = 0

    if current_room not in HAZARD_DATA:
        return

    _active_hazards = HAZARD_DATA[current_room]
    _active         = True

    for hazard in _active_hazards:
        room.hazard_map[hazard[0]][hazard[1]] = 49 + (current_room % 3)
        # Start fully arrived at current position (anim_t = 1.0)
        _hazard_visual.append([float(hazard[0]), float(hazard[1]), 1.0])


def hazard_stop():
    """Stop hazard movement (call when leaving a room)."""
    global _active
    _active = False


def get_hazard_draws(current_room):
    """
    Return interpolated draw positions for all active hazards.
    Used by room.draw_room() for smooth rendering — does NOT affect collision.
    Returns: list of (obj_id, float_y, float_x)
    """
    if not _active:
        return []
    obj_id = 49 + (current_room % 3)
    result = []
    for i, hazard in enumerate(_active_hazards):
        vis = _hazard_visual[i]
        t   = vis[2]
        # Lerp from prev position toward current grid position
        dy = vis[0] + (hazard[0] - vis[0]) * t
        dx = vis[1] + (hazard[1] - vis[1]) * t
        result.append((obj_id, dy, dx))
    return result


def update_hazards(dt, current_room, player_y, player_x,
                   from_player_y, from_player_x, player_frame, game_over):
    """
    Advance all hazards by dt milliseconds.
    Animation progress is updated every frame for smooth lerp.
    Grid positions + hazard_map only update on each 150ms step.

    Returns energy_penalty (0 or 10).
    """
    global _timer

    if not _active or game_over:
        return 0

    # Advance animation progress toward 1.0 every frame (smooth lerp)
    step_frac = dt / HAZARD_FRAME_MS
    for vis in _hazard_visual:
        vis[2] = min(1.0, vis[2] + step_frac)

    _timer += dt
    if _timer < HAZARD_FRAME_MS:
        return 0
    _timer = 0

    energy_penalty = 0

    for i, hazard in enumerate(_active_hazards):
        hazard_y         = hazard[0]
        hazard_x         = hazard[1]
        hazard_direction = hazard[2]
        old_hazard_y     = hazard_y
        old_hazard_x     = hazard_x

        # Clear old position from hazard_map
        room.hazard_map[old_hazard_y][old_hazard_x] = 0

        # Move one step in the current direction
        if hazard_direction == 1: hazard_y -= 1
        if hazard_direction == 2: hazard_x += 1
        if hazard_direction == 3: hazard_y += 1
        if hazard_direction == 4: hazard_x -= 1

        hazard_should_bounce = False

        # Player collision
        if (hazard_y == player_y and hazard_x == player_x) or \
                (hazard_y == from_player_y and hazard_x == from_player_x
                 and player_frame > 0):
            energy_penalty       = 10
            hazard_should_bounce = True

        # Room boundary
        if hazard_x == room.room_width:
            hazard_should_bounce = True; hazard_x = room.room_width - 1
        if hazard_x == -1:
            hazard_should_bounce = True; hazard_x = 0
        if hazard_y == room.room_height:
            hazard_should_bounce = True; hazard_y = room.room_height - 1
        if hazard_y == -1:
            hazard_should_bounce = True; hazard_y = 0

        # Scenery or another hazard in the way
        if (room.room_map[hazard_y][hazard_x] not in items_player_may_stand_on
                or room.hazard_map[hazard_y][hazard_x] != 0):
            hazard_should_bounce = True

        if hazard_should_bounce:
            hazard_y         = old_hazard_y
            hazard_x         = old_hazard_x
            hazard_direction += hazard[3]
            if hazard_direction > 4: hazard_direction -= 4
            if hazard_direction < 1: hazard_direction += 4
            hazard[2] = hazard_direction

        # Write new grid position
        room.hazard_map[hazard_y][hazard_x] = 49 + (current_room % 3)
        hazard[0] = hazard_y
        hazard[1] = hazard_x

        # Restart visual lerp from old position toward new grid position
        _hazard_visual[i][0] = float(old_hazard_y)
        _hazard_visual[i][1] = float(old_hazard_x)
        _hazard_visual[i][2] = 0.0

    return energy_penalty
