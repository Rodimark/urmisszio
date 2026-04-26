"""
hud.py — HUD for urmisszio, pixel-art panel style matching the main menu.
Uses the same panel/Clean 9-slice assets as the main menu buttons.
"""
import os
import pygame

# ── Screen / panel sizing ─────────────────────────────────────────────────────

SCREEN_W  = 1280
SCREEN_H  = 720
HUD_TOP_H = 160    # top panel height  (must match data.HUD_TOP_H)
HUD_BOT_H = 72     # bottom panel height (interior = 72-32 = 40px, fits 36px bars)

UI_SCALE  = 4      # matches mainmenu.py SCALE — keeps pixel art consistent

# ── Colours — matched to the main menu palette ───────────────────────────────

BLUE   = (0,   120, 255)   # button-glow blue from main menu
CYAN   = (100, 200, 255)   # lighter blue for energy bar
WHITE  = (255, 255, 255)
TEXT   = (200, 220, 255)   # main menu title colour — used for all HUD text
RED    = (180,  40,  40)   # softened red for game over

# ── Asset paths ───────────────────────────────────────────────────────────────

_PANEL_DIR   = os.path.join("assets", "ui", "panel", "Clean")
_DIVIDER_DIR = os.path.join("assets", "ui", "divider_horizontal")

# ── Image cache (UI assets — separate from game tile cache) ───────────────────

_ui_cache = {}

def _ui_raw(path):
    """Load a UI image exactly once."""
    if path not in _ui_cache:
        _ui_cache[path] = pygame.image.load(path).convert_alpha()
    return _ui_cache[path]

def _panel_slice(name):
    return _ui_raw(os.path.join(_PANEL_DIR, name + ".png"))

def _scaled(name, scale):
    """Return a panel slice scaled up by `scale`, cached."""
    key = ("scaled", name, scale)
    if key not in _ui_cache:
        src = _panel_slice(name)
        _ui_cache[key] = pygame.transform.scale(
            src, (src.get_width() * scale, src.get_height() * scale))
    return _ui_cache[key]


# ── 9-slice tiling helpers ────────────────────────────────────────────────────

def _tile_h(surface, piece, x, y, w):
    """Tile `piece` horizontally to fill a strip of width `w`."""
    pw = piece.get_width()
    ph = piece.get_height()
    clip = pygame.Rect(x, y, w, ph)
    old = surface.get_clip()
    surface.set_clip(clip)
    for xi in range(x, x + w, pw):
        surface.blit(piece, (xi, y))
    surface.set_clip(old)

def _tile_v(surface, piece, x, y, h):
    """Tile `piece` vertically to fill a column of height `h`."""
    pw = piece.get_width()
    ph = piece.get_height()
    clip = pygame.Rect(x, y, pw, h)
    old = surface.get_clip()
    surface.set_clip(clip)
    for yi in range(y, y + h, ph):
        surface.blit(piece, (x, yi))
    surface.set_clip(old)

def _tile_fill(surface, piece, x, y, w, h):
    """Tile `piece` to fill a rectangle."""
    pw = piece.get_width()
    ph = piece.get_height()
    clip = pygame.Rect(x, y, w, h)
    old = surface.get_clip()
    surface.set_clip(clip)
    for yi in range(y, y + h, ph):
        for xi in range(x, x + w, pw):
            surface.blit(piece, (xi, yi))
    surface.set_clip(old)


# ── 9-slice panel draw ────────────────────────────────────────────────────────

def draw_panel(surface, x, y, w, h, scale=UI_SCALE):
    """
    Draw a pixel-art panel using the 9-slice panel/Clean assets.
    Corners are pixel-scaled; edges and center are tiled (not stretched)
    so the pixel art stays crisp at any size.

    panel/Clean slices (native px):
        corners      : 15 × 4
        top/bot edges: 45 × 4  (tiles horizontally)
        left/rt edges: 15 × 47 (tiles vertically)
        center tile  : 45 × 47 (tiles both ways)
    """
    tl = _scaled("top_left",      scale)
    tr = _scaled("top_right",     scale)
    bl = _scaled("bottom_left",   scale)
    br = _scaled("bottom_right",  scale)
    tc = _scaled("top_center",    scale)
    bc = _scaled("bottom_center", scale)
    cl = _scaled("center_left",   scale)
    cr = _scaled("center_right",  scale)
    cc = _scaled("center",        scale)

    cw  = tl.get_width()    # corner / side-edge width
    th  = tl.get_height()   # top-edge height
    bh  = bl.get_height()   # bottom-edge height
    mid_w = w - cw * 2
    mid_h = h - th - bh

    # Corners
    surface.blit(tl, (x,           y          ))
    surface.blit(tr, (x + w - cw,  y          ))
    surface.blit(bl, (x,           y + h - bh ))
    surface.blit(br, (x + w - cw,  y + h - bh ))

    # Top + bottom edges — tiled horizontally
    _tile_h(surface, tc, x + cw,  y,           mid_w)
    _tile_h(surface, bc, x + cw,  y + h - bh,  mid_w)

    # Left + right edges — tiled vertically
    _tile_v(surface, cl, x,           y + th,  mid_h)
    _tile_v(surface, cr, x + w - cw,  y + th,  mid_h)

    # Center fill — tiled both directions
    _tile_fill(surface, cc, x + cw, y + th, mid_w, mid_h)


# ── HUD layout ────────────────────────────────────────────────────────────────
# All y values are absolute screen coordinates.
# With UI_SCALE=4: top/bottom border of each panel = 4*4 = 16px.
# Top panel interior: y=16 to y=144  (fits 128px of content)

TEXT_Y0  = 22    # room name / primary message  (inside top border)
TEXT_Y1  = 52    # secondary message
ICONS_Y  = 84    # inventory icon row  (icon height ≈ TILE_SIZE = 30px → bottom at 114)
DESC_Y   = 122   # selected-item description    (fits inside interior at ≤ 144)

# Bottom panel: y = SCREEN_H - HUD_BOT_H = 632
# Bar images are scaled to _BAR_H tall, centred vertically in the panel.
_BAR_H        = 36    # display height for the bar images (px)
_BAR_W        = 400   # display width for each bar
_BORDER_T     = 16    # 9-slice top border at UI_SCALE=4  (4px × 4 = 16px)
_BORDER_B     = 16    # 9-slice bottom border
_INTERIOR_H   = HUD_BOT_H - _BORDER_T - _BORDER_B          # 40px
_BAR_Y        = (SCREEN_H - HUD_BOT_H + _BORDER_T           # interior top
                 + (_INTERIOR_H - _BAR_H) // 2)             # centred inside
_LBL_GAP      = 12    # gap between label and its bar
_CENTER_GAP   = 60    # gap between the AIR group and PWR group
# Computed in init_hud() once the font is loaded — centred as a unit on screen:
_AIR_LBL_X    = 0
_AIR_X        = 0
_PWR_LBL_X    = 0
_PWR_X        = 0

_TRACK   = (10, 14, 40, 200)  # dark navy RGBA — shown behind empty portion

# ── Module state ──────────────────────────────────────────────────────────────

_font      = None
_font_go   = None
_font_mid  = None
_bar_imgs  = {}       # {"oxygen": Surface, "power": Surface}
_dlg_img   = None     # dialogue window Surface

_FONT_PATH = "assets/fonts/AeogoPxltdNext-5y27B.ttf"
_BAR_DIR   = os.path.join("assets", "ui", "healthbar")
_DLG_PATH  = os.path.join("assets", "ui", "dialogue window", "Asset 2.png")

def init_hud(font):
    """Call once after pygame.init(), passing in the game font."""
    global _font, _font_go, _font_mid, _bar_imgs, _dlg_img
    global _AIR_LBL_X, _AIR_X, _PWR_LBL_X, _PWR_X
    _font     = font
    _font_go  = pygame.font.Font(_FONT_PATH, 110)
    _font_mid = pygame.font.Font(_FONT_PATH, 52)

    # Centre both label+bar pairs as one unit on screen
    lw_air     = _font.size("AIR")[0]
    lw_pwr     = _font.size("PWR")[0]
    total_w    = lw_air + _LBL_GAP + _BAR_W + _CENTER_GAP + lw_pwr + _LBL_GAP + _BAR_W
    _left      = (SCREEN_W - total_w) // 2
    _AIR_LBL_X = _left
    _AIR_X     = _left + lw_air + _LBL_GAP
    _PWR_LBL_X = _AIR_X + _BAR_W + _CENTER_GAP
    _PWR_X     = _PWR_LBL_X + lw_pwr + _LBL_GAP

    # Load + scale bar images
    for name in ("oxygen", "power"):
        raw = pygame.image.load(
            os.path.join(_BAR_DIR, f"{name}.png")).convert_alpha()
        _bar_imgs[name] = pygame.transform.smoothscale(raw, (_BAR_W, _BAR_H))

    # Load + scale dialogue window  (2818×1180 → ~700×293)
    raw = pygame.image.load(_DLG_PATH).convert_alpha()
    dw  = 700
    dh  = int(raw.get_height() * dw / raw.get_width())
    _dlg_img = pygame.transform.smoothscale(raw, (dw, dh))


# ── Frame-start panel draw ────────────────────────────────────────────────────

def draw_hud_panels(surface):
    """
    Call once per frame AFTER drawing the room, BEFORE drawing any HUD text.
    Redraws both panel backgrounds — this acts as the HUD clear each frame.
    """
    draw_panel(surface, 0, 0,                        SCREEN_W, HUD_TOP_H)
    draw_panel(surface, 0, SCREEN_H - HUD_BOT_H,    SCREEN_W, HUD_BOT_H)


# ── Text messages ─────────────────────────────────────────────────────────────

def show_text(surface, text_to_show, line_number):
    """
    line_number 0 → TEXT_Y0  (primary status, overlays room name)
    line_number 1 → TEXT_Y1  (secondary)
    Panel background handles clearing — no black rect needed.
    """
    y = TEXT_Y1 if line_number else TEXT_Y0
    surface.blit(_font.render(text_to_show, True, TEXT), (20, y))


def draw_room_name(surface, room_name):
    """Always drawn; may be covered by show_text(surface, msg, 0)."""
    surface.blit(_font.render(room_name, True, TEXT), (20, TEXT_Y0))


# ── Inventory display ─────────────────────────────────────────────────────────

def display_inventory(surface, in_my_pockets, selected_item, objects, img_fn):
    """
    Draws item icons at ICONS_Y, a white selection box, and the description
    of the highlighted item at DESC_Y.
    Faithful to MissionPython's display_inventory() — icons at 46px intervals.
    """
    if not in_my_pockets:
        return

    start   = (selected_item // 16) * 16
    to_show = in_my_pockets[start : start + 16]
    sel_idx = selected_item % 16

    for i, item_id in enumerate(to_show):
        icon = img_fn(objects[item_id][0])
        surface.blit(icon, (25 + 46 * i, ICONS_Y))

    # White selection rectangle around current item
    box_left = sel_idx * 46 - 3
    pygame.draw.rect(surface, WHITE, (22 + box_left, ICONS_Y - 5, 40, 40), 1)

    desc = objects[in_my_pockets[selected_item]][2]
    surface.blit(_font.render(desc, True, TEXT), (20, DESC_Y))


# ── Air + energy bars (image-based, clipped to current value) ─────────────────

def _draw_img_bar(surface, x, y, img, value):
    """
    Draw `img` clipped to (value/100) of its width.
    A dark track fills the full width behind it so the empty portion is visible.
    """
    w, h = img.get_size()
    # Dark track for the empty portion
    track_surf = pygame.Surface((w, h), pygame.SRCALPHA)
    track_surf.fill(_TRACK)
    surface.blit(track_surf, (x, y))
    # Clip-blit the filled portion
    if value > 0:
        fill_w = max(1, int(w * value / 100))
        old    = surface.get_clip()
        surface.set_clip(pygame.Rect(x, y, fill_w, h))
        surface.blit(img, (x, y))
        surface.set_clip(old)


def draw_energy_air(surface, air, energy):
    """Status bars using the imported healthbar PNG assets."""
    lbl_y = _BAR_Y + _BAR_H // 2   # vertical centre for labels

    # AIR — label then bar on the same row
    lbl = _font.render("AIR", True, BLUE)
    surface.blit(lbl, (_AIR_LBL_X, lbl_y - lbl.get_height() // 2))
    _draw_img_bar(surface, _AIR_X, _BAR_Y, _bar_imgs["oxygen"], air)

    # PWR — label then bar on the same row
    elbl = _font.render("PWR", True, CYAN)
    surface.blit(elbl, (_PWR_LBL_X, lbl_y - elbl.get_height() // 2))
    _draw_img_bar(surface, _PWR_X, _BAR_Y, _bar_imgs["power"], energy)


# ── Dialogue window ───────────────────────────────────────────────────────────

def draw_dialogue(surface, text, speaker=""):
    """
    Draw the sci-fi dialogue window just above the bottom HUD panel.
    Call from main.py whenever a robot/NPC speaks.

    text    — the message to display (auto word-wrapped)
    speaker — optional name shown in the top-left corner of the window
    """
    if _dlg_img is None:
        return
    dw, dh = _dlg_img.get_size()
    dx = SCREEN_W // 2 - dw // 2
    dy = SCREEN_H - HUD_BOT_H - dh - 10
    surface.blit(_dlg_img, (dx, dy))

    # Text area inside the window (estimated inner margins)
    pad_x, pad_y = 55, 38
    max_w  = dw - pad_x * 2
    line_h = _font.get_height() + 4

    # Optional speaker name
    tx, ty = dx + pad_x, dy + pad_y
    if speaker:
        s = _font.render(speaker, True, CYAN)
        surface.blit(s, (tx, ty))
        ty += line_h + 4

    # Word-wrap the body text
    words  = text.split()
    line   = ""
    for word in words:
        test = (line + " " + word).strip()
        if _font.size(test)[0] <= max_w:
            line = test
        else:
            surface.blit(_font.render(line, True, TEXT), (tx, ty))
            ty  += line_h
            line = word
    if line:
        surface.blit(_font.render(line, True, TEXT), (tx, ty))


# ── Game over overlay ─────────────────────────────────────────────────────────

def draw_game_over(surface, reason):
    """Full-screen game over screen — big centred text."""
    surface.fill((0, 0, 0))

    go_surf  = _font_go.render("GAME OVER",        True, TEXT)
    re_surf  = _font_mid.render(reason,             True, RED )
    esc_surf = _font_mid.render("PRESS ESC TO QUIT", True, TEXT)

    # Stack vertically, centred as a block
    gap      = 30
    total_h  = go_surf.get_height() + gap + re_surf.get_height() + gap + esc_surf.get_height()
    y        = (SCREEN_H - total_h) // 2

    def cx(s): return SCREEN_W // 2 - s.get_width() // 2

    surface.blit(go_surf,  (cx(go_surf),  y))
    y += go_surf.get_height() + gap
    surface.blit(re_surf,  (cx(re_surf),  y))
    y += re_surf.get_height() + gap
    surface.blit(esc_surf, (cx(esc_surf), y))


# ── Mission complete overlay ──────────────────────────────────────────────────

def draw_mission_complete(surface):
    """Static overlay — launch animation driven by main.py."""
    m_surf = _font.render("MISSION",  True, TEXT)
    c_surf = _font.render("COMPLETE", True, TEXT)
    surface.blit(m_surf, (SCREEN_W // 2 - m_surf.get_width() // 2, 380))
    surface.blit(c_surf, (SCREEN_W // 2 - c_surf.get_width() // 2, 480))


# ── Alarm message ─────────────────────────────────────────────────────────────

def draw_alarm(surface, player_name):
    """Low-air warning — faithful to MissionPython's alarm()."""
    show_text(surface,
              f"Air is running out, {player_name}! "
              f"Get to safety, then radio for help!", 1)


# ── Screen flash ──────────────────────────────────────────────────────────────

_dim_surf   = None   # cached dark overlay for the game area
_flash_surf = None   # cached so we don't allocate every frame

def draw_room_dim(surface, alpha=110):
    """
    Darken the game area with a semi-transparent black overlay.
    Call after room.draw_room(), before draw_hud_panels().
    alpha 0-255 — higher = darker.
    """
    global _dim_surf
    if _dim_surf is None:
        _dim_surf = pygame.Surface((SCREEN_W, SCREEN_H))
        _dim_surf.fill((0, 0, 0))
    _dim_surf.set_alpha(alpha)
    surface.blit(_dim_surf, (0, 0))


def draw_flash(surface, alpha):
    """
    Full-screen red flash overlay — alpha 0-255.
    Used for hit damage (brief) and critical status (pulsing).
    """
    global _flash_surf
    if _flash_surf is None:
        _flash_surf = pygame.Surface((SCREEN_W, SCREEN_H))
        _flash_surf.fill((200, 20, 20))
    _flash_surf.set_alpha(alpha)
    surface.blit(_flash_surf, (0, 0))
