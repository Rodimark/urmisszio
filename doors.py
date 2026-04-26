"""
doors.py — Door animation system for urmisszio
Ported from Mission Python by Sean McManus (pygame zero → pygame)

MissionPython used clock.schedule(do_door_animation, 0.15) for timing.
Here we use delta-time accumulation — update() is called every frame.
"""
import pygame
from data import PROPS

# ms per animation frame — matches MissionPython's 0.15 s interval
DOOR_FRAME_MS = 150

# Engineering door timer — matches MissionPython's 60-second schedule
ENGINEERING_DOOR_MS = 60_000

# ── Opening / closing animation state ────────────────────────────────────────

_anim = None
# {
#   "door_number": int,
#   "frames":        [image_name, ...],   5 frames
#   "shadow_frames": [image_name, ...],   5 frames
#   "frame":         int,
#   "timer":         int (ms),
#   "opening":       bool,
# }

# ── Airlock (room 26) state ───────────────────────────────────────────────────

airlock_door_frame = 0   # 0=closed … 5=fully open
_airlock_active    = False

# ── Engineering door timer ────────────────────────────────────────────────────

_engineering_timer    = 0
_engineering_counting = False


# ── Public API ────────────────────────────────────────────────────────────────

def open_door(door_number):
    """
    Start a door-opening animation.
    Faithful to MissionPython's open_door().
    """
    global _anim
    _anim = {
        "door_number":  door_number,
        "frames":       ["door1", "door2", "door3", "door4", "floor"],
        "shadow_frames":["door1_shadow", "door2_shadow", "door3_shadow",
                         "door4_shadow", "door_shadow"],
        "frame":  0,
        "timer":  0,
        "opening": True,
    }


def close_door(door_number, player_y, room_height):
    """
    Start a door-closing animation.
    Faithful to MissionPython's close_door() — also nudges the
    player out of the doorway if they're standing in it.
    Returns the (possibly adjusted) player_y.
    """
    global _anim
    _anim = {
        "door_number":  door_number,
        "frames":       ["door4", "door3", "door2", "door1", "door"],
        "shadow_frames":["door4_shadow", "door3_shadow", "door2_shadow",
                         "door1_shadow", "door_shadow"],
        "frame":  0,
        "timer":  0,
        "opening": False,
    }
    # If player is in the same row as the door, push them clear
    if player_y == PROPS[door_number][1]:
        if player_y == 0:
            player_y = 1
        else:
            player_y = room_height - 2
    return player_y


def is_animating():
    return _anim is not None


def get_current_frame():
    """Returns (image_name, shadow_name, prop_y, prop_x) for the active frame."""
    if _anim is None:
        return None
    door_num = _anim["door_number"]
    f        = min(_anim["frame"], 4)
    py, px   = PROPS[door_num][1], PROPS[door_num][2]
    return _anim["frames"][f], _anim["shadow_frames"][f], py, px


def update_door_anim(dt):
    """
    Advance the door animation by dt milliseconds.
    Returns True while animation is active.
    Call from main loop BEFORE drawing.
    """
    global _anim
    if _anim is None:
        return False

    _anim["timer"] += dt
    if _anim["timer"] < DOOR_FRAME_MS:
        return True

    _anim["timer"] = 0
    _anim["frame"] += 1

    if _anim["frame"] >= 5:
        # Animation finished
        if _anim["opening"]:
            # Remove door from props (same as MissionPython)
            PROPS[_anim["door_number"]][0] = 0
        _anim = None
        return False

    return True


# ── Room-26 airlock door ──────────────────────────────────────────────────────
# MissionPython scheduled door_in_room_26 every 0.05 s.
# We call update_airlock() every frame with dt instead.

_AIRLOCK_FRAME_MS = 50   # matches MissionPython's 0.05 s

_airlock_timer = 0

def start_airlock():
    global _airlock_active, airlock_door_frame, _airlock_timer
    _airlock_active    = True
    airlock_door_frame = 0
    _airlock_timer     = 0

def stop_airlock():
    global _airlock_active
    _airlock_active = False

def update_airlock(dt, current_room, player_y, player_x, props_bin_full):
    """
    Faithful to MissionPython's door_in_room_26().
    Call every frame when current_room == 26.
    props_bin_full: True if prop 63 (bin full of water) is at [26, 8, 2].
    Returns the updated room_map changes as a list of (y, x, value) tuples,
    or an empty list if nothing changed.
    """
    global airlock_door_frame, _airlock_timer
    if not _airlock_active or current_room != 26:
        return []

    _airlock_timer += dt
    if _airlock_timer < _AIRLOCK_FRAME_MS:
        return []
    _airlock_timer = 0

    changes = []
    on_pad  = (player_y == 8 and player_x == 2) or props_bin_full

    # Door is present (prop 21 in room 26) and player/bin is on pad → open
    if on_pad and PROPS[21][0] == 26:
        airlock_door_frame += 1
        if airlock_door_frame >= 5:
            airlock_door_frame = 5
            PROPS[21][0] = 0   # remove door from map
            changes = [(0, 1, 0), (0, 2, 0), (0, 3, 0)]

    # Door removed (not in room) and player/bin off pad → close
    if not on_pad and airlock_door_frame > 0:
        if airlock_door_frame == 5:
            # Put door back so the closing animation is visible
            PROPS[21][0] = 26
            changes = [(0, 1, 21), (0, 2, 255), (0, 3, 255)]
        airlock_door_frame -= 1

    return changes


def get_airlock_frame_images():
    """Returns (image_name, shadow_name) for the current airlock frame."""
    frames = ["door", "door1", "door2", "door3", "door4", "floor"]
    shadows = ["door_shadow", "door1_shadow", "door2_shadow",
               "door3_shadow", "door4_shadow", None]
    f = min(airlock_door_frame, 5)
    return frames[f], shadows[f]


# ── Engineering door timer ────────────────────────────────────────────────────

def start_engineering_timer():
    """Called when the button in room 27/40 is pressed."""
    global _engineering_timer, _engineering_counting
    _engineering_timer    = 0
    _engineering_counting = True


def update_engineering_timer(dt):
    """
    Returns True (once) when 60 seconds have elapsed — caller should
    then close the engineering doors and call stop_engineering_timer().
    """
    global _engineering_timer, _engineering_counting
    if not _engineering_counting:
        return False
    _engineering_timer += dt
    if _engineering_timer >= ENGINEERING_DOOR_MS:
        _engineering_counting = False
        return True
    return False


def stop_engineering_timer():
    global _engineering_counting
    _engineering_counting = False
