"""
inventory.py — Inventory and prop interaction for urmisszio
Ported from Mission Python by Sean McManus (pygame zero → pygame)

Owns: in_my_pockets, selected_item, item_carrying
Reads game state (room_map, player coords, etc.) via parameters.
Returns result dicts for side-effects that main.py applies.
"""
from data import (
    OBJECTS, PROPS, RECIPES, ACCESS_DICTIONARY,
    items_player_may_carry, outdoor_rooms,
    PLAYER_NAME, LANDER_SECTOR, LANDER_X, LANDER_Y,
)
import room   # for room.room_map, room.get_floor_type

# ── Module-level inventory state ──────────────────────────────────────────────

in_my_pockets = [55]   # start with yoyo (object 55)
selected_item  = 0
item_carrying  = 55    # mirrors in_my_pockets[selected_item]

# ── Position helpers ──────────────────────────────────────────────────────────

def find_object_start_x(player_y, player_x):
    """
    Scan left through 255 tiles to find the true leftmost tile of an object.
    Faithful to MissionPython's find_object_start_x().
    """
    checker_x = player_x
    while room.room_map[player_y][checker_x] == 255:
        checker_x -= 1
    return checker_x


def get_item_under_player(player_y, player_x):
    """Faithful to MissionPython's get_item_under_player()."""
    item_x = find_object_start_x(player_y, player_x)
    return room.room_map[player_y][item_x]


# ── Core inventory operations ─────────────────────────────────────────────────

def add_object(item):
    """
    Adds item to inventory and moves it off the map (room 0).
    Faithful to MissionPython's add_object().
    """
    global selected_item, item_carrying, in_my_pockets
    in_my_pockets.append(item)
    item_carrying = item
    selected_item = len(in_my_pockets) - 1
    PROPS[item][0] = 0   # carried objects live in room 0 (off the map)


def remove_object(item):
    """
    Removes item from inventory and updates selection.
    Faithful to MissionPython's remove_object().
    """
    global selected_item, item_carrying, in_my_pockets
    in_my_pockets.remove(item)
    selected_item -= 1
    if selected_item < 0:
        selected_item = 0
    if len(in_my_pockets) == 0:
        item_carrying = False
    else:
        item_carrying = in_my_pockets[selected_item]


def cycle_selected_item():
    """Advance selected_item by one (Tab key). Faithful to MissionPython."""
    global selected_item, item_carrying
    if not in_my_pockets:
        return
    selected_item += 1
    if selected_item > len(in_my_pockets) - 1:
        selected_item = 0
    item_carrying = in_my_pockets[selected_item]


# ── Pick up / drop ────────────────────────────────────────────────────────────

def pick_up_object(current_room, player_y, player_x):
    """
    Faithful to MissionPython's pick_up_object().
    Returns (message, sound_name | None).
    Clears room_map tile and adds to inventory directly.
    """
    item_player_is_on = get_item_under_player(player_y, player_x)
    if item_player_is_on in items_player_may_carry:
        room.room_map[player_y][player_x] = room.get_floor_type(current_room)
        add_object(item_player_is_on)
        return "Now carrying " + OBJECTS[item_player_is_on][3], "pickup"
    else:
        return "You can't carry that!", None


def drop_object(old_y, old_x, current_room):
    """
    Faithful to MissionPython's drop_object().
    Returns (message, sound_name | None).
    Updates room_map and PROPS directly.
    """
    if room.room_map[old_y][old_x] in [0, 2, 39]:
        PROPS[item_carrying][0] = current_room
        PROPS[item_carrying][1] = old_y
        PROPS[item_carrying][2] = old_x
        room.room_map[old_y][old_x] = item_carrying
        msg = "You have dropped " + OBJECTS[item_carrying][3]
        remove_object(item_carrying)
        return msg, "drop"
    else:
        return "You can't drop that there.", None


# ── Examine ───────────────────────────────────────────────────────────────────

def examine_object(current_room, player_y, player_x):
    """
    Faithful to MissionPython's examine_object().
    Also discovers hidden props stacked under the player.
    Returns (message, sound_name | None).
    """
    item_player_is_on = get_item_under_player(player_y, player_x)
    left_x = find_object_start_x(player_y, player_x)

    if item_player_is_on in [0, 2]:
        return None, None   # don't describe the floor

    description = "You see: " + OBJECTS[item_player_is_on][2]
    found_sound  = None

    for prop_number, details in PROPS.items():
        if details[0] == current_room:
            # Prop is in the room but hidden (not shown in room_map)
            if (details[1] == player_y
                    and details[2] == left_x
                    and room.room_map[details[1]][details[2]] != prop_number):
                add_object(prop_number)
                description = "You found " + OBJECTS[prop_number][3]
                found_sound  = "combine"

    return description, found_sound


# ── Use object ────────────────────────────────────────────────────────────────

def use_object(current_room, player_y, player_x,
               air, energy, suit_stitched, air_fixed, game_over):
    """
    Faithful to MissionPython's use_object().

    Returns a result dict — main.py is responsible for applying all side effects:

        message              str   — line 0 HUD text
        secondary            str | None — line 1 HUD text
        sound                str | None — sound effect name
        air                  int   — (possibly updated) air value
        energy               int   — (possibly updated) energy value
        suit_stitched        bool
        air_fixed            bool
        start_air_countdown  bool  — True → caller starts the air timer
        open_door            int | None — door number to animate open
        open_engineering     bool  — True → remove eng doors + start 60s timer
        rescue_ship          bool  — True → move prop 40 to room 13
        game_won             bool
    """
    result = {
        "message":             "You fiddle around with it but don't get anywhere.",
        "secondary":           None,
        "sound":               None,
        "air":                 air,
        "energy":              energy,
        "suit_stitched":       suit_stitched,
        "air_fixed":           air_fixed,
        "start_air_countdown": False,
        "open_door":           None,
        "open_engineering":    False,
        "rescue_ship":         False,
        "game_won":            False,
    }

    standard_responses = {
        4:  "Air is running out! You can't take this lying down!",
        6:  "This is no time to sit around!",
        7:  "This is no time to sit around!",
        32: "It shakes and rumbles, but nothing else happens.",
        34: "Ah! That's better. Now wash your hands.",
        35: "You wash your hands and shake the water off.",
        37: "The test tubes smoke slightly as you shake them.",
        54: "You chew the gum. It's sticky like glue.",
        55: "The yoyo bounces up and down, slightly slower than on Earth",
        56: "It's a bit too fiddly. Can you thread it on something?",
        59: "You need to fix the leak before you can use the canister",
        61: "You try signalling with the mirror, but nobody can see you.",
        62: "Don't throw resources away. Things might come in handy...",
        67: "To enjoy yummy space food, just add water!",
        75: ("You are at Sector: " + str(current_room)
             + " // X: " + str(player_x)
             + " // Y: " + str(player_y)),
    }

    item_player_is_on = get_item_under_player(player_y, player_x)

    # Standard-response check — item on floor OR in hand
    for this_item in [item_player_is_on, item_carrying]:
        if this_item in standard_responses:
            result["message"] = standard_responses[this_item]

    # ── Special cases (elif chain, same order as MissionPython) ─────────────

    if item_carrying == 70 or item_player_is_on == 70:
        result["message"] = "Banging tunes!"
        result["sound"]   = "steelmusic"

    elif item_player_is_on == 11:
        # Computer status terminal
        msg = "AIR: " + str(air) + "% / ENERGY " + str(energy) + "% / "
        if not suit_stitched:
            msg += "*ALERT* SUIT FABRIC TORN / "
        if not air_fixed:
            msg += "*ALERT* SUIT AIR BOTTLE MISSING"
        if suit_stitched and air_fixed:
            msg += " SUIT OK"
        result["message"] = msg
        result["sound"]   = "say_status_report"
        return result   # early return — same as MissionPython

    elif item_carrying == 60 or item_player_is_on == 60:
        # Sealed air canister → fix the suit air supply
        result["message"]             = "You fix " + OBJECTS[60][3] + " to the suit"
        result["air_fixed"]           = True
        result["air"]                 = 90
        result["start_air_countdown"] = True
        remove_object(60)

    elif (item_carrying == 58 or item_player_is_on == 58) and not suit_stitched:
        # Needle-and-string → stitch torn suit
        result["message"]       = ("You use " + OBJECTS[56][3]
                                   + " to repair the suit fabric")
        result["suit_stitched"] = True
        remove_object(58)

    elif item_carrying == 72 or item_player_is_on == 72:
        # Radio → call rescue ship
        result["message"]     = ("You radio for help. A rescue ship is coming. "
                                 "Rendezvous Sector 13, outside.")
        result["rescue_ship"] = True

    elif (item_carrying == 66 or item_player_is_on == 66) \
            and current_room in outdoor_rooms:
        # Spoon → dig on the planet surface
        result["message"] = "You dig..."
        if (current_room == LANDER_SECTOR
                and player_x == LANDER_X
                and player_y == LANDER_Y):
            add_object(71)
            result["message"] = "You found the Poodle lander!"

    elif item_player_is_on == 40:
        # Rescue ship → mission complete
        result["message"]   = "Congratulations, " + PLAYER_NAME + "!"
        result["secondary"] = "Mission success! You have made it to safety."
        result["game_won"]  = True
        result["sound"]     = "take_off"
        return result   # early return — game over

    elif item_player_is_on == 16:
        # Lettuce → recover a little energy
        result["energy"]  = min(energy + 1, 100)
        result["message"] = "You munch the lettuce and get a little energy back"

    elif item_player_is_on == 42:
        # Button → open engineering doors (+ start 60-second close timer)
        if current_room == 27:
            result["open_door"] = 26
        result["open_engineering"] = True
        result["message"]          = "You press the button"
        result["secondary"]        = "Door to engineering bay is open for 60 seconds"
        result["sound"]            = "say_doors_open"

    elif item_carrying == 68 or item_player_is_on == 68:
        # Ready-to-eat food → full energy
        result["energy"]  = 100
        result["message"] = "You use the food to restore your energy"
        remove_object(68)

    # ── Suit repaired + air fixed → open airlock (runs regardless of elif) ───

    if result["suit_stitched"] and result["air_fixed"]:
        if current_room == 31 and PROPS[20][0] == 31:
            result["open_door"] = 20
            result["secondary"] = "The computer tells you the airlock is now open."
            result["sound"]     = "say_airlock_open"
        elif PROPS[20][0] == 31:
            PROPS[20][0] = 0   # remove door from map (no animation needed)
            result["secondary"] = "The computer tells you the airlock is now open."
            result["sound"]     = "say_airlock_open"

    # ── Recipes (faithful — checks all recipes, not just first match) ────────

    for recipe in RECIPES:
        ing1, ing2, combo = recipe
        if (item_carrying == ing1 and item_player_is_on == ing2) \
                or (item_carrying == ing2 and item_player_is_on == ing1):
            result["message"] = ("You combine " + OBJECTS[ing1][3]
                                 + " and " + OBJECTS[ing2][3]
                                 + " to make " + OBJECTS[combo][3])
            # Remove ground item from props (if it is one) and clear the tile
            if item_player_is_on in PROPS:
                PROPS[item_player_is_on][0] = 0
                room.room_map[player_y][player_x] = room.get_floor_type(current_room)
            # Faithful to MissionPython: remove carrying item directly (not remove_object)
            # so selected_item index stays stable before add_object overrides it
            in_my_pockets.remove(item_carrying)
            add_object(combo)
            result["sound"] = "combine"

    # ── Access cards → unlock matching door ──────────────────────────────────

    for card_id, door_num in ACCESS_DICTIONARY.items():
        if item_carrying == card_id:
            if PROPS[door_num][0] == current_room:
                result["message"]   = "You unlock the door!"
                result["open_door"] = door_num
                result["sound"]     = "say_doors_open"

    return result
