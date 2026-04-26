import pygame
import random

def _apply_glow(screen):
    """Soft glow — smoothscale down then back up, blended over the screen."""
    w, h = screen.get_size()
    glow = pygame.transform.smoothscale(screen, (w // 2, h // 2))
    glow = pygame.transform.smoothscale(glow, (w, h))
    glow.set_alpha(100)
    screen.blit(glow, (0, 0))

SCALE = 4
SCREEN_W, SCREEN_H = 1280, 720

UI = "assets/ui/"
BG = "assets/background/layered/"
FONT = "assets/fonts/AeogoPxltdNext-5y27B.ttf"

BTN_SIZE = (400, 148)  # change button size here


def load_bg(name):
    img = pygame.image.load(BG + name).convert_alpha()
    return pygame.transform.scale(img, (img.get_width() * SCALE, img.get_height() * SCALE))


def load_ui(path, size):
    img = pygame.image.load(UI + path).convert_alpha()
    return pygame.transform.scale(img, size)


class Prop(pygame.sprite.Sprite):
    def __init__(self, image, speed):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, SCREEN_W - self.rect.width)
        self.rect.y = random.randint(-SCREEN_H, 0)
        self.speed = speed

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > SCREEN_H:
            self.rect.x = random.randint(0, SCREEN_W - self.rect.width)
            self.rect.y = -self.rect.height



def draw_tiling_layer(surface, img, scroll):
    h = img.get_height()
    w = img.get_width()
    y = scroll % h
    for row_y in range(int(y) - h, SCREEN_H, h):
        for col_x in range(0, SCREEN_W, w):
            surface.blit(img, (col_x, row_y))


def make_props():
    props = pygame.sprite.Group()
    for _ in range(2):
        props.add(Prop(load_bg("prop-planet-big.png"),   speed=1.0))
        props.add(Prop(load_bg("prop-planet-small.png"), speed=1.5))
    for _ in range(4):
        props.add(Prop(load_bg("asteroid-1.png"), speed=random.uniform(2.0, 3.5)))
        props.add(Prop(load_bg("asteroid-2.png"), speed=random.uniform(2.5, 4.0)))
    return props


def draw_background(screen, layers, props, glitching=False):
    for layer in layers:
        layer["scroll"] += layer["speed"]
    for layer in layers:
        draw_tiling_layer(screen, layer["img"], layer["scroll"])
    if not glitching:
        props.update()
    props.draw(screen)


def draw_title(screen, font, glitching=False):
    shadow_raw = font.render("URMISSZIO", True, (10, 30, 120))
    title_raw  = font.render("URMISSZIO", True, (200, 220, 255))
    w, h = title_raw.get_size()
    shadow = pygame.transform.scale(shadow_raw, (w, h * 2))
    title  = pygame.transform.scale(title_raw,  (w, h * 2))
    tx = SCREEN_W // 2 - title.get_width() // 2
    ty = 80
    screen.blit(shadow, (tx + 3, ty + 3))
    screen.blit(title,  (tx,     ty))
    intensity = "maximum" if glitching else "medium"
    _add_glitch_effect(SCREEN_H, SCREEN_W, screen, intensity)


def _draw_button(screen, btn_n, btn_h, btn_c, font, rect, label, hover, down):
    """Generic button draw — same pixel-art style for any label."""
    if down and hover:
        screen.blit(btn_c, rect)
    elif hover:
        screen.blit(btn_h, rect)
    else:
        screen.blit(btn_n, rect)
    lbl = font.render(label, True, (255, 255, 255))
    lx  = rect.centerx - lbl.get_width()  // 2
    ly  = rect.centery - lbl.get_height() // 2
    if hover:
        shadow = font.render(label, True, (0, 120, 255))
        screen.blit(shadow, (lx + 4, ly + 4))
    screen.blit(lbl, (lx, ly))
    _add_glitch_effect(SCREEN_H, SCREEN_W, screen, "medium")


def draw_play_button(screen, btn_n, btn_h, btn_c, font, play_rect, play_hover, play_down):
    _draw_button(screen, btn_n, btn_h, btn_c, font, play_rect,
                 "START", play_hover, play_down)


def draw_arcade_button(screen, btn_n, btn_h, btn_c, font, rect, hover, down):
    _draw_button(screen, btn_n, btn_h, btn_c, font, rect,
                 "ARCADE", hover, down)


def handle_events(play_rect, arcade_rect, play_down, arcade_down):
    mx, my = pygame.mouse.get_pos()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return "quit", play_down, arcade_down, mx, my
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            return "quit", play_down, arcade_down, mx, my
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if play_rect.collidepoint(mx, my):
                play_down   = True
            if arcade_rect.collidepoint(mx, my):
                arcade_down = True
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if play_down and play_rect.collidepoint(mx, my):
                return "start", play_down, arcade_down, mx, my
            if arcade_down and arcade_rect.collidepoint(mx, my):
                return "arcade", play_down, arcade_down, mx, my
            play_down   = False
            arcade_down = False
    return None, play_down, arcade_down, mx, my

def _add_glitch_effect(height, width, glitch_surface, intensity):
    shift_amount = {"minimum": 10, "medium": 20, "maximum": 40}.get(intensity, 20)
    if random.random() < 0.1:
        y_start = random.randint(0, height - 20)
        slice_height = random.randint(5, 20)
        offset = random.randint(-shift_amount, shift_amount)

        slice_area = pygame.Rect(0, y_start, width, slice_height)
        slice_copy = glitch_surface.subsurface(slice_area).copy()
        glitch_surface.blit(slice_copy, (offset, y_start))

def apply_crt(screen, glitching=False):
    scanline = pygame.Surface((SCREEN_W, 2), pygame.SRCALPHA)
    scanline.fill((0, 0, 0, 80))
    for y in range(0, SCREEN_H, 4):
        screen.blit(scanline, (0, y))

    flicker_chance = 0.3 if glitching else 0.05
    flicker_alpha  = 40  if glitching else 12
    if random.random() < flicker_chance:
        flicker = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        flicker.fill((255, 255, 255, flicker_alpha))
        screen.blit(flicker, (0, 0))

    _apply_glow(screen)


def run(screen, clock):
    layers = [
        {"img": load_bg("blue-back.png"),  "scroll": 0, "speed": 0.5},
        {"img": load_bg("blue-stars.png"), "scroll": 0, "speed": 1.2},
    ]
    props = make_props()

    btn_n = load_ui("button/Normal/button_normal.png",   BTN_SIZE)
    btn_h = load_ui("button/Hover/button_hover.png",     BTN_SIZE)
    btn_c = load_ui("button/Clicked/button_clicked.png", BTN_SIZE)
    BW, BH = BTN_SIZE

    font_title = pygame.font.Font(FONT, 130)
    font_btn   = pygame.font.Font(FONT, 55)

    cx          = SCREEN_W // 2 - BW // 2
    GAP         = 22
    # Stack the two buttons; centre the combined block in the lower 2/3 of screen
    # (title occupies roughly y=80–340, so useful area is ~340–720 = 380px)
    BLOCK_H     = BH * 2 + GAP          # 318 px
    BLOCK_TOP   = 340 + (380 - BLOCK_H) // 2   # centres block in space below title
    play_rect   = pygame.Rect(cx, BLOCK_TOP,           BW, BH)
    arcade_rect = pygame.Rect(cx, BLOCK_TOP + BH + GAP, BW, BH)

    pygame.mixer.music.load("assets/audio/menumusic/pointless - d2s1.mp3")
    pygame.mixer.music.play(-1)
    power_on_sfx = pygame.mixer.Sound("assets/audio/soundeffects/Crap_Computer_02.wav")

    glitch_sfx = [
        pygame.mixer.Sound("assets/audio/glitches/dragon-studio-glitch-effect-1-397982.wav"),
        pygame.mixer.Sound("assets/audio/glitches/dragon-studio-glitch-effect-2-397980.wav"),
        pygame.mixer.Sound("assets/audio/glitches/dragon-studio-glitch-noise-454247.wav"),
        pygame.mixer.Sound("assets/audio/glitches/dragon-studio-glitch-sound-effect-443130.wav"),
        pygame.mixer.Sound("assets/audio/glitches/virtual_vibes-computer-distortion-glitch-400944.wav"),
    ]
    glitch_sfx_timer = random.randint(300, 600)  # frames between interruptions
    glitch_channel   = pygame.mixer.Channel(1)


    pygame.mouse.set_visible(False)
    cursor         = load_ui("cursors/cursor2.png",         size=(32, 32))
    cursor_clicked = load_ui("cursors/cursor2_clicked.png", size=(32, 32))

    play_down   = False
    arcade_down = False
    glitching   = False
    original_speeds = [layer["speed"] for layer in layers]

    # CRT power-on: black bars shrink from top and bottom toward center
    power_on      = True
    bar_height    = SCREEN_H // 2  # starts covering the full screen
    power_on_speed = 15            # pixels per frame — higher = faster
    power_on_sfx.play()            # play once when menu opens

    while True:
        clock.tick(60)

        result, play_down, arcade_down, mx, my = handle_events(
            play_rect, arcade_rect, play_down, arcade_down)
        if result:
            pygame.mixer.music.stop()
            return result

        glitch_sfx_timer -= 1
        if glitch_sfx_timer <= 0 and not glitching:
            pygame.mixer.music.pause()
            glitch_channel.play(random.choice(glitch_sfx))
            glitch_sfx_timer = random.randint(300, 600)
            glitching = True
            for layer in layers:
                layer["speed"] = 0  # freeze background
        if glitching and not glitch_channel.get_busy():
            pygame.mixer.music.unpause()
            for i, layer in enumerate(layers):
                layer["speed"] = original_speeds[i]  # restore
            glitching = False

        draw_background(screen, layers, props, glitching)
        draw_title(screen, font_title, glitching)
        draw_play_button(screen, btn_n, btn_h, btn_c, font_btn,
                         play_rect,   play_rect.collidepoint(mx, my),   play_down)
        draw_arcade_button(screen, btn_n, btn_h, btn_c, font_btn,
                           arcade_rect, arcade_rect.collidepoint(mx, my), arcade_down)
        apply_crt(screen, glitching)

        if power_on:
            pygame.draw.rect(screen, (0, 0, 0), (0, 0, SCREEN_W, bar_height))
            pygame.draw.rect(screen, (0, 0, 0), (0, SCREEN_H - bar_height, SCREEN_W, bar_height))
            bar_height -= power_on_speed
            if bar_height <= 0:
                power_on = False


        img = cursor_clicked if pygame.mouse.get_pressed()[0] else cursor
        screen.blit(img, (mx, my))
        pygame.display.flip()
