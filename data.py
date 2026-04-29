"""
data.py — All game data for urmisszio
Ported from Mission Python by Sean McManus
"""
import random

# ── Player config ─────────────────────────────────────────────────────────────

PLAYER_NAME  = "Jack"
FRIEND1_NAME = "Bob"
FRIEND2_NAME = "Fred"

# ── Map constants ─────────────────────────────────────────────────────────────

TILE_SIZE  = 30
MAP_WIDTH  = 5
MAP_HEIGHT = 10
MAP_SIZE   = MAP_WIDTH * MAP_HEIGHT

# ── Lander crash site (random each game) ─────────────────────────────────────

LANDER_SECTOR = random.randint(1, 24)
LANDER_X      = random.randint(2, 11)
LANDER_Y      = random.randint(2, 11)

# ── Game map ──────────────────────────────────────────────────────────────────
# Each room: name, h (height tiles), w (width tiles), top exit, right exit

GAME_MAP = {
    0:  {"name": "Room 0 — unused object storage", "h": 0,  "w": 0,  "top": False, "right": False},
    # ── Planet surface (rooms 1–25) ───────────────────────────────────────────
    1:  {"name": "The dusty planet surface",                          "h": 13, "w": 13, "top": True,  "right": True },
    2:  {"name": "The dusty planet surface",                          "h": 13, "w": 13, "top": True,  "right": True },
    3:  {"name": "The dusty planet surface",                          "h": 13, "w": 13, "top": True,  "right": True },
    4:  {"name": "The dusty planet surface",                          "h": 13, "w": 13, "top": True,  "right": True },
    5:  {"name": "The dusty planet surface",                          "h": 13, "w": 13, "top": True,  "right": True },
    6:  {"name": "The dusty planet surface",                          "h": 13, "w": 13, "top": True,  "right": True },
    7:  {"name": "The dusty planet surface",                          "h": 13, "w": 13, "top": True,  "right": True },
    8:  {"name": "The dusty planet surface",                          "h": 13, "w": 13, "top": True,  "right": True },
    9:  {"name": "The dusty planet surface",                          "h": 13, "w": 13, "top": True,  "right": True },
    10: {"name": "The dusty planet surface",                          "h": 13, "w": 13, "top": True,  "right": True },
    11: {"name": "The dusty planet surface",                          "h": 13, "w": 13, "top": True,  "right": True },
    12: {"name": "The dusty planet surface",                          "h": 13, "w": 13, "top": True,  "right": True },
    13: {"name": "The dusty planet surface",                          "h": 13, "w": 13, "top": True,  "right": True },
    14: {"name": "The dusty planet surface",                          "h": 13, "w": 13, "top": True,  "right": True },
    15: {"name": "The dusty planet surface",                          "h": 13, "w": 13, "top": True,  "right": True },
    16: {"name": "The dusty planet surface",                          "h": 13, "w": 13, "top": True,  "right": True },
    17: {"name": "The dusty planet surface",                          "h": 13, "w": 13, "top": True,  "right": True },
    18: {"name": "The dusty planet surface",                          "h": 13, "w": 13, "top": True,  "right": True },
    19: {"name": "The dusty planet surface",                          "h": 13, "w": 13, "top": True,  "right": True },
    20: {"name": "The dusty planet surface",                          "h": 13, "w": 13, "top": True,  "right": True },
    21: {"name": "The dusty planet surface",                          "h": 13, "w": 13, "top": True,  "right": True },
    22: {"name": "The dusty planet surface",                          "h": 13, "w": 13, "top": True,  "right": True },
    23: {"name": "The dusty planet surface",                          "h": 13, "w": 13, "top": True,  "right": True },
    24: {"name": "The dusty planet surface",                          "h": 13, "w": 13, "top": True,  "right": True },
    25: {"name": "The dusty planet surface",                          "h": 13, "w": 13, "top": True,  "right": True },
    # ── Station interior (rooms 26–50) ────────────────────────────────────────
    26: {"name": "The airlock",                                       "h": 13, "w": 5,  "top": True,  "right": False},
    27: {"name": "The engineering lab",                               "h": 13, "w": 13, "top": False, "right": False},
    28: {"name": "Poodle Mission Control",                            "h": 9,  "w": 13, "top": False, "right": True },
    29: {"name": "The viewing gallery",                               "h": 9,  "w": 15, "top": False, "right": False},
    30: {"name": "The crew's bathroom",                               "h": 5,  "w": 5,  "top": False, "right": False},
    31: {"name": "The airlock entry bay",                             "h": 7,  "w": 11, "top": True,  "right": True },
    32: {"name": "Left elbow room",                                   "h": 9,  "w": 7,  "top": True,  "right": False},
    33: {"name": "Right elbow room",                                  "h": 7,  "w": 13, "top": True,  "right": True },
    34: {"name": "The science lab",                                   "h": 13, "w": 13, "top": False, "right": True },
    35: {"name": "The greenhouse",                                    "h": 13, "w": 13, "top": True,  "right": False},
    36: {"name": PLAYER_NAME + "'s sleeping quarters",                "h": 9,  "w": 11, "top": False, "right": False},
    37: {"name": "West corridor",                                     "h": 15, "w": 5,  "top": True,  "right": True },
    38: {"name": "The briefing room",                                 "h": 7,  "w": 13, "top": False, "right": True },
    39: {"name": "The crew's community room",                         "h": 11, "w": 13, "top": True,  "right": False},
    40: {"name": "Main Mission Control",                              "h": 14, "w": 14, "top": False, "right": False},
    41: {"name": "The sick bay",                                      "h": 12, "w": 7,  "top": True,  "right": False},
    42: {"name": "West corridor",                                     "h": 9,  "w": 7,  "top": True,  "right": False},
    43: {"name": "Utilities control room",                            "h": 9,  "w": 9,  "top": False, "right": True },
    44: {"name": "Systems engineering bay",                           "h": 9,  "w": 11, "top": False, "right": False},
    45: {"name": "Security portal to Mission Control",                "h": 7,  "w": 7,  "top": True,  "right": False},
    46: {"name": FRIEND1_NAME + "'s sleeping quarters",               "h": 9,  "w": 11, "top": True,  "right": True },
    47: {"name": FRIEND2_NAME + "'s sleeping quarters",               "h": 9,  "w": 11, "top": True,  "right": True },
    48: {"name": "The pipeworks",                                     "h": 13, "w": 11, "top": True,  "right": False},
    49: {"name": "The chief scientist's office",                      "h": 9,  "w": 7,  "top": True,  "right": True },
    50: {"name": "The robot workshop",                                "h": 9,  "w": 11, "top": True,  "right": False},
}

outdoor_rooms = set(range(1, 26))

# ── Connections (auto-generated from GAME_MAP) ────────────────────────────────
# (room, direction) → destination room number

CONNECTIONS = {}
for _n, _r in GAME_MAP.items():
    if _n == 0:
        continue
    if _r["right"] and _n % MAP_WIDTH != 0:
        CONNECTIONS[(_n, "right")] = _n + 1
        CONNECTIONS[(_n + 1, "left")] = _n
    if _r["top"] and _n > MAP_WIDTH:
        CONNECTIONS[(_n, "top")] = _n - MAP_WIDTH
        CONNECTIONS[(_n - MAP_WIDTH, "bottom")] = _n

# ── Objects ───────────────────────────────────────────────────────────────────
# id → (image_name, shadow_name, description, pickup_name)
# shadow_name and pickup_name are None if not applicable

OBJECTS = {
    0:  ("floor",                None,                       "The floor is shiny and clean",                                                None),
    1:  ("pillar",               "full_shadow",              "The wall is smooth and cold",                                                 None),
    2:  ("soil",                 None,                       "It's like a desert. Or should that be dessert?",                              None),
    3:  ("pillar_low",           "half_shadow",              "The wall is smooth and cold",                                                 None),
    4:  ("bed",                  "half_shadow",              "A tidy and comfortable bed",                                                  None),
    5:  ("table",                "half_shadow",              "It's made from strong plastic.",                                              None),
    6:  ("chair_left",           None,                       "A chair with a soft cushion",                                                 None),
    7:  ("chair_right",          None,                       "A chair with a soft cushion",                                                 None),
    8:  ("bookcase_tall",        "full_shadow",              "Bookshelves, stacked with reference books",                                   None),
    9:  ("bookcase_small",       "half_shadow",              "Bookshelves, stacked with reference books",                                   None),
    10: ("cabinet",              "half_shadow",              "A small locker, for storing personal items",                                  None),
    11: ("desk_computer",        "half_shadow",              "A computer. Use it to run life support diagnostics",                          None),
    12: ("plant",                "plant_shadow",             "A spaceberry plant, grown here",                                              None),
    13: ("electrical1",          "half_shadow",              "Electrical systems used for powering the space station",                      None),
    14: ("electrical2",          "half_shadow",              "Electrical systems used for powering the space station",                      None),
    15: ("cactus",               "cactus_shadow",            "Ouch! Careful on the cactus!",                                               None),
    16: ("shrub",                "shrub_shadow",             "A space lettuce. A bit limp, but amazing it's growing here!",                None),
    17: ("pipes1",               "pipes1_shadow",            "Water purification pipes",                                                    None),
    18: ("pipes2",               "pipes2_shadow",            "Pipes for the life support systems",                                         None),
    19: ("pipes3",               "pipes3_shadow",            "Pipes for the life support systems",                                         None),
    20: ("door",                 "door_shadow",              "Safety door. Opens automatically for astronauts in functioning spacesuits.",  None),
    21: ("door",                 "door_shadow",              "The airlock door. For safety reasons, it requires two person operation.",     None),
    22: ("door",                 "door_shadow",              f"A locked door. It needs {PLAYER_NAME}'s access card",                       None),
    23: ("door",                 "door_shadow",              f"A locked door. It needs {FRIEND1_NAME}'s access card",                      None),
    24: ("door",                 "door_shadow",              f"A locked door. It needs {FRIEND2_NAME}'s access card",                      None),
    25: ("door",                 "door_shadow",              "A locked door. It is opened from Main Mission Control",                       None),
    26: ("door",                 "door_shadow",              "A locked door in the engineering bay.",                                       None),
    27: ("map",                  "full_shadow",              f"The screen says the crash site was Sector: {LANDER_SECTOR} // X: {LANDER_X} // Y: {LANDER_Y}", None),
    28: ("rock_large",           "rock_large_shadow",        "A rock. Its coarse surface feels like a whetstone",                          "the rock"),
    29: ("rock_small",           "rock_small_shadow",        "A small but heavy piece of Martian rock",                                    None),
    30: ("crater",               None,                       "A crater in the planet surface",                                             None),
    31: ("fence",                None,                       "A fine gauze fence. It helps protect the station from dust storms",          None),
    32: ("contraption",          "contraption_shadow",       "One of the scientific experiments. It gently vibrates",                      None),
    33: ("robot_arm",            "robot_arm_shadow",         "A robot arm, used for heavy lifting",                                        None),
    34: ("toilet",               "half_shadow",              "A sparkling clean toilet",                                                    None),
    35: ("sink",                 None,                       "A sink with running water",                                                   "the taps"),
    36: ("globe",                "globe_shadow",             "A giant globe of the planet. It gently glows from inside",                   None),
    37: ("science_lab_table",    None,                       "A table of experiments, analyzing the planet soil and dust",                 None),
    38: ("vending_machine",      "full_shadow",              "A vending machine. It requires a credit.",                                   "the vending machine"),
    39: ("floor_pad",            None,                       "A pressure sensor to make sure nobody goes out alone.",                      None),
    40: ("rescue_ship",          "rescue_ship_shadow",       "A rescue ship!",                                                             None),
    41: ("mission_control_desk", "mission_control_desk_shadow", "Mission Control stations.",                                               None),
    42: ("button",               "button_shadow",            "The button for opening the time-locked door in engineering.",                None),
    43: ("whiteboard",           "full_shadow",              "The whiteboard is used in brainstorms and planning meetings.",               None),
    44: ("window",               "full_shadow",              "The window provides a view out onto the planet surface.",                    None),
    45: ("robot",                "robot_shadow",             "A cleaning robot, turned off.",                                              None),
    46: ("robot2",               "robot2_shadow",            "A planet surface exploration robot, awaiting set-up.",                       None),
    47: ("rocket",               "rocket_shadow",            "A 1-person craft in repair.",                                                None),
    48: ("toxic_floor",          None,                       "Toxic floor - do not walk on!",                                             None),
    49: ("drone",                None,                       "A delivery drone",                                                           None),
    50: ("energy_ball",          None,                       "An energy ball - dangerous!",                                                None),
    51: ("energy_ball2",         None,                       "An energy ball - dangerous!",                                                None),
    52: ("computer",             "computer_shadow",          "A computer workstation, for managing space station systems.",                None),
    53: ("clipboard",            None,                       "A clipboard. Someone has doodled on it.",                                   "the clipboard"),
    54: ("bubble_gum",           None,                       "A piece of sticky bubble gum. Spaceberry flavour.",                         "bubble gum"),
    55: ("yoyo",                 None,                       "A toy made of fine, strong string and plastic. Used for antigrav experiments.", f"{PLAYER_NAME}'s yoyo"),
    56: ("thread",               None,                       "A piece of fine, strong string",                                            "a piece of string"),
    57: ("needle",               None,                       "A sharp needle from a cactus plant",                                        "a cactus needle"),
    58: ("threaded_needle",      None,                       "A cactus needle, spearing a length of string",                              "needle and string"),
    59: ("canister",             None,                       "The air canister has a leak.",                                              "a leaky air canister"),
    60: ("canister",             None,                       "It looks like the seal will hold!",                                         "a sealed air canister"),
    61: ("mirror",               None,                       "The mirror throws a circle of light on the walls.",                         "a mirror"),
    62: ("bin_empty",            None,                       "A rarely used bin, made of light plastic",                                  "a bin"),
    63: ("bin_full",             None,                       "A heavy bin full of water",                                                 "a bin full of water"),
    64: ("rags",                 None,                       "An oily rag. Pick it up by a corner if you must!",                         "an oily rag"),
    65: ("hammer",               None,                       "A hammer. Maybe good for cracking things open...",                          "a hammer"),
    66: ("spoon",                None,                       "A large serving spoon",                                                     "a spoon"),
    67: ("food_pouch",           None,                       "A dehydrated food pouch. It needs water.",                                  "a dry food pack"),
    68: ("food",                 None,                       "A food pouch. Use it to get 100% energy.",                                  "ready-to-eat food"),
    69: ("book",                 None,                       "The book has the words 'Don't Panic' on the cover in large, friendly letters", "a book"),
    70: ("mp3_player",           None,                       "An MP3 player, with all the latest tunes",                                  "an MP3 player"),
    71: ("lander",               None,                       "The Poodle, a small space exploration craft. Its black box has a radio sealed inside.", "the Poodle lander"),
    72: ("radio",                None,                       "A radio communications system, from the Poodle",                           "a communications radio"),
    73: ("gps_module",           None,                       "A GPS Module",                                                              "a GPS module"),
    74: ("positioning_system",   None,                       "Part of a positioning system. Needs a GPS module.",                        "a positioning interface"),
    75: ("positioning_system",   None,                       "A working positioning system",                                              "a positioning computer"),
    76: ("scissors",             None,                       "Scissors. They're too blunt to cut anything. Can you sharpen them?",       "blunt scissors"),
    77: ("scissors",             None,                       "Razor-sharp scissors. Careful!",                                            "sharpened scissors"),
    78: ("credit",               None,                       "A small coin for the station's vending systems",                           "a station credit"),
    79: ("access_card",          None,                       f"This access card belongs to {PLAYER_NAME}",                               "an access card"),
    80: ("access_card",          None,                       f"This access card belongs to {FRIEND1_NAME}",                              "an access card"),
    81: ("access_card",          None,                       f"This access card belongs to {FRIEND2_NAME}",                              "an access card"),
}

items_player_may_carry    = list(range(53, 82))
items_player_may_stand_on = items_player_may_carry + [0, 39, 2, 48]

# ── Scenery ───────────────────────────────────────────────────────────────────
# room → [[obj_id, y, x], ...]

SCENERY = {
    26: [[39, 8, 2]],
    27: [[33, 5, 5], [33, 1, 1], [33, 1, 8], [47, 5, 2], [47, 3, 10], [47, 9, 8], [42, 1, 6]],
    28: [[27, 0, 3], [41, 4, 3], [41, 4, 7]],
    29: [[7, 2, 6], [6, 2, 8], [12, 1, 13], [44, 0, 1], [36, 4, 10], [10, 1, 1], [19, 4, 2], [17, 4, 4]],
    30: [[34, 1, 1], [35, 1, 3]],
    31: [[11, 1, 1], [19, 1, 8], [46, 1, 3]],
    32: [[48, 2, 2], [48, 2, 3], [48, 2, 4], [48, 3, 2], [48, 3, 3], [48, 3, 4], [48, 4, 2], [48, 4, 3], [48, 4, 4]],
    33: [[13, 1, 1], [13, 1, 3], [13, 1, 8], [13, 1, 10], [48, 2, 1], [48, 2, 7], [48, 3, 6], [48, 3, 3]],
    34: [[37, 2, 2], [32, 6, 7], [37, 10, 4], [28, 5, 3]],
    35: [[16, 2, 9], [16, 2, 2], [16, 3, 3], [16, 3, 8], [16, 8, 9], [16, 8, 2], [16, 1, 8], [16, 1, 3],
         [12, 8, 6], [12, 9, 4], [12, 9, 8], [15, 4, 6], [12, 7, 1], [12, 7, 11]],
    36: [[4, 3, 1], [9, 1, 7], [8, 1, 8], [8, 1, 9], [5, 5, 4], [6, 5, 7], [10, 1, 1], [12, 1, 2]],
    37: [[48, 3, 1], [48, 3, 2], [48, 7, 1], [48, 5, 2], [48, 5, 3], [48, 7, 2], [48, 9, 2], [48, 9, 3], [48, 11, 1], [48, 11, 2]],
    38: [[43, 0, 2], [6, 2, 2], [6, 3, 5], [6, 4, 7], [6, 2, 9], [45, 1, 10]],
    39: [[38, 1, 1], [7, 3, 4], [7, 6, 4], [5, 3, 6], [5, 6, 6], [6, 3, 9], [6, 6, 9], [45, 1, 11], [12, 1, 8], [12, 1, 4]],
    40: [[41, 5, 3], [41, 5, 7], [41, 9, 3], [41, 9, 7], [13, 1, 1], [13, 1, 3], [42, 1, 12]],
    41: [[4, 3, 1], [10, 3, 5], [4, 5, 1], [10, 5, 5], [4, 7, 1], [10, 7, 5], [12, 1, 1], [12, 1, 5]],
    44: [[46, 4, 3], [46, 4, 5], [18, 1, 1], [19, 1, 3], [19, 1, 5], [52, 4, 7], [14, 1, 8]],
    45: [[48, 2, 1], [48, 2, 2], [48, 3, 3], [48, 3, 4], [48, 1, 4], [48, 1, 1]],
    46: [[10, 1, 1], [4, 1, 2], [8, 1, 7], [9, 1, 8], [8, 1, 9], [5, 4, 3], [7, 3, 2]],
    47: [[9, 1, 1], [9, 1, 2], [10, 1, 3], [12, 1, 7], [5, 4, 4], [6, 4, 7], [4, 1, 8]],
    48: [[17, 4, 1], [17, 4, 2], [17, 4, 3], [17, 4, 4], [17, 4, 5], [17, 4, 6], [17, 4, 7],
         [17, 8, 1], [17, 8, 2], [17, 8, 3], [17, 8, 4], [17, 8, 5], [17, 8, 6], [17, 8, 7], [14, 1, 1]],
    49: [[14, 2, 2], [14, 2, 4], [7, 5, 1], [5, 5, 3], [48, 3, 3], [48, 3, 4]],
    50: [[45, 4, 8], [11, 1, 1], [13, 1, 8], [33, 2, 1], [46, 4, 6]],
}

# Add random scenery to planet surface rooms
for _room in range(1, 26):
    if _room != 13:
        _item = random.choice([16, 28, 29, 30])
        SCENERY[_room] = [[_item, random.randint(2, 10), random.randint(2, 10)]]

# Add fences to planet surface border rooms
for _coord in range(0, 13):
    for _rn in [1, 2, 3, 4, 5]:
        SCENERY.setdefault(_rn, []).append([31, 0, _coord])
    for _rn in [1, 6, 11, 16, 21]:
        SCENERY.setdefault(_rn, []).append([31, _coord, 0])
    for _rn in [5, 10, 15, 20, 25]:
        SCENERY.setdefault(_rn, []).append([31, _coord, 12])

SCENERY[21].pop()
SCENERY[25].pop()

# ── Props ─────────────────────────────────────────────────────────────────────
# obj_id → [room, y, x]  (mutable — changes as player picks up / drops things)

PROPS = {
    20: [31, 0, 4],  21: [26, 0, 1],  22: [41, 0, 2],  23: [39, 0, 5],
    24: [45, 0, 2],
    25: [32, 0, 2],  26: [27, 12, 5],
    40: [0,  8, 6],  53: [45, 1, 5],  54: [0,  0, 0],  55: [0,  0, 0],
    56: [0,  0, 0],  57: [35, 4, 6],  58: [0,  0, 0],  59: [31, 1, 7],
    60: [0,  0, 0],  61: [36, 1, 1],  62: [36, 1, 6],  63: [0,  0, 0],
    64: [27, 8, 3],  65: [50, 1, 7],  66: [39, 5, 6],  67: [46, 1, 1],
    68: [0,  0, 0],  69: [30, 3, 3],  70: [47, 1, 3],
    71: [0,  LANDER_Y, LANDER_X],
    72: [0,  0, 0],  73: [27, 4, 6],  74: [28, 1, 11], 75: [0,  0, 0],
    76: [41, 3, 5],  77: [0,  0, 0],  78: [35, 9, 11], 79: [31, 3, 5],
    80: [41, 9, 3],  81: [29, 1, 1],   # Bob's card on a clear floor tile in sick bay
}

# ── Default PROPS snapshot — used to reset world state on replay ──────────────
import copy as _copy
PROPS_DEFAULT = _copy.deepcopy(PROPS)

# ── Recipes ───────────────────────────────────────────────────────────────────
# [ingredient1, ingredient2, result]

RECIPES = [
    [62, 35, 63],   # bin + taps = bin full of water
    [76, 28, 77],   # blunt scissors + rock = sharpened scissors
    [78, 38, 54],   # credit + vending machine = bubble gum
    [73, 74, 75],   # gps module + positioning interface = positioning computer
    [59, 54, 60],   # leaky canister + bubble gum = sealed canister
    [77, 55, 56],   # sharpened scissors + yoyo = thread
    [56, 57, 58],   # thread + cactus needle = needle and string
    [71, 65, 72],   # lander + hammer = communications radio
    [67, 35, 68],   # dry food pack + taps = ready-to-eat food
]

# ── Door keys ─────────────────────────────────────────────────────────────────
# key item obj_id → door obj_id it unlocks

ACCESS_DICTIONARY = {
    79: 22,   # player's access card → player's locked door
    80: 23,   # friend1's access card → friend1's locked door
    81: 24,   # friend2's access card → friend2's locked door
}

# ── Hazards ───────────────────────────────────────────────────────────────────
# room → [[y, x, direction, bounce_delta]]
# directions: 1=up, 2=right, 3=down, 4=left

HAZARD_DATA = {
    28: [[1, 8, 2, 1],  [7, 3, 4, 1]],
    32: [[1, 5, 4, -1]],
    34: [[5, 1, 1, 1],  [5, 5, 1, 2]],
    35: [[4, 4, 1, 2],  [2, 5, 2, 2]],
    36: [[2, 1, 2, 2]],
    38: [[1, 4, 3, 2],  [5, 8, 1, 2]],
    40: [[3, 1, 3, -1], [6, 5, 2, 2], [7, 5, 4, 2]],
    41: [[4, 5, 2, 2],  [6, 3, 4, 2], [8, 1, 2, 2]],
    42: [[2, 1, 2, 2],  [4, 3, 2, 2], [6, 5, 2, 2]],
    46: [[2, 1, 2, 2]],
    48: [[1, 8, 3, 2],  [8, 8, 1, 2], [3, 9, 3, 2]],
}

# ── HUD layout constants ──────────────────────────────────────────────────────

HUD_TOP_H = 160   # height of the top panel (room name, messages, inventory)
HUD_BOT_H = 72    # height of the bottom panel (air + energy bars)
