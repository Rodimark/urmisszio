"""
shooter.py — Space shooter minigame for urmisszio
Vertical scrolling SHMUP using assets/spaceshooter/.
Returns "menu" when done, "quit" on window close.
"""
import pygame
import random
import os

from mainmenu import apply_crt, load_bg, make_props, draw_background
import hud as _hud

SCREEN_W  = 1280
SCREEN_H  = 720
FONT_PATH = "assets/fonts/AeogoPxltdNext-5y27B.ttf"

_SS = "assets/spaceshooter"

# Sprite scales — ship is 96×96, enemies are 64×64 natively → scale 1 fits well
PLAYER_SCALE = 1
ENEMY_SCALE  = 1

# Gameplay tuning
PLAYER_SPEED      = 5        # px per frame at 60fps
BULLET_SPEED_PX   = 800      # px / sec, upward
EBULLET_SPEED_PX  = 520      # px / sec, downward (scales up with wave)
SHOOT_COOLDOWN_MS = 180
PLAYER_LIVES      = 3
INVINCIBLE_MS     = 1500

# Background scroll speeds (px/frame at 60fps) — same structure as main menu
BG_BASE_SPEEDS = [1.5, 3.5]   # faster than menu (0.5, 1.2) for shooter feel
BG_ACCEL_RATE  = 0.00004      # fraction of base speed added per ms elapsed

# Enemy spawning
SPAWN_BASE_MS = 1800
SPAWN_MIN_MS  = 500


# ── Image cache ───────────────────────────────────────────────────────────────

_cache: dict = {}

def _img(path: str, scale: int = 1) -> pygame.Surface:
    key = (path, scale)
    if key not in _cache:
        raw = pygame.image.load(path).convert_alpha()
        if scale != 1:
            raw = pygame.transform.scale(
                raw, (raw.get_width() * scale, raw.get_height() * scale))
        _cache[key] = raw
    return _cache[key]

def _load_frames(folder, prefix, count, scale=1, vflip=False):
    frames = []
    for i in range(1, count + 1):
        img = _img(os.path.join(folder, f"{prefix}{i}.png"), scale)
        if vflip:
            img = pygame.transform.flip(img, False, True)
        frames.append(img)
    return frames


# ── Animation helper ──────────────────────────────────────────────────────────

class Anim:
    def __init__(self, frames, fps=12):
        self.frames  = frames
        self.ms_per  = 1000 / fps
        self.timer   = 0.0
        self.idx     = 0

    def update(self, dt):
        self.timer += dt
        while self.timer >= self.ms_per:
            self.timer -= self.ms_per
            self.idx = (self.idx + 1) % len(self.frames)

    @property
    def image(self):
        return self.frames[self.idx]


# ── Parallax background — reuses main menu assets exactly ────────────────────

class Background:
    """
    Same layers + props as the main menu, just faster + accelerating.
    Uses mainmenu.load_bg / make_props / draw_background so the look is
    identical — planets, asteroids, star layers and all.
    """
    def __init__(self):
        self.layers = [
            {"img": load_bg("blue-back.png"),  "scroll": 0.0,
             "speed": BG_BASE_SPEEDS[0]},
            {"img": load_bg("blue-stars.png"), "scroll": 0.0,
             "speed": BG_BASE_SPEEDS[1]},
        ]
        self.props = make_props()
        # Give props a head-start speed boost for the shooter vibe
        for spr in self.props.sprites():
            spr.speed = spr.speed * 2.5
        self.elapsed_ms = 0.0

    def tick(self, dt):
        """Call once per frame before draw(); accelerates speeds over time."""
        self.elapsed_ms += dt
        boost = 1.0 + self.elapsed_ms * BG_ACCEL_RATE
        for i, layer in enumerate(self.layers):
            layer["speed"] = BG_BASE_SPEEDS[i] * boost

    def draw(self, surface):
        """draw_background scrolls layers + updates/draws props in one call."""
        draw_background(surface, self.layers, self.props)


# ── Bullet ────────────────────────────────────────────────────────────────────

class Bullet:
    def __init__(self, x, y, img, vy):
        self.x    = float(x)
        self.y    = float(y)
        self.img  = img
        self.vy   = vy          # px/sec (negative = up)
        self.rect = img.get_rect(center=(int(x), int(y)))
        self.dead = False

    def update(self, dt):
        self.y += self.vy * dt / 1000.0
        self.rect.center = (int(self.x), int(self.y))
        if self.y < -80 or self.y > SCREEN_H + 80:
            self.dead = True

    def draw(self, surface):
        surface.blit(self.img, self.rect)


# ── Explosion ─────────────────────────────────────────────────────────────────

class Explosion:
    def __init__(self, x, y, frames, fps=22):
        self.x    = x
        self.y    = y
        self.anim = Anim(frames, fps)
        self._dur = len(frames) * (1000.0 / fps)
        self._t   = 0.0
        self.dead = False

    def update(self, dt):
        self.anim.update(dt)
        self._t += dt
        if self._t >= self._dur:
            self.dead = True

    def draw(self, surface):
        img = self.anim.image
        surface.blit(img, (self.x - img.get_width()  // 2,
                           self.y - img.get_height() // 2))


# ── Player ────────────────────────────────────────────────────────────────────

class Player:
    def __init__(self, frames, bullet_img):
        self.anim       = Anim(frames, fps=20)
        self.bullet_img = bullet_img
        self.x               = float(SCREEN_W // 2)
        # Fixed row — horizontal movement only
        self.y               = float(SCREEN_H - 110)
        self.rect            = frames[0].get_rect(center=(self.x, self.y))
        self.lives           = PLAYER_LIVES
        self.shoot_cd        = 0.0
        self.inv_timer       = 0.0
        self._blink          = 0
        self.dead            = False

    def update(self, dt, keys):
        spd = PLAYER_SPEED * dt / 16.67
        dx  = 0.0
        if keys[pygame.K_LEFT]  or keys[pygame.K_a]: dx -= spd
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: dx += spd
        # Only play the banking animation while a key is held; idle = frame 0
        if dx != 0:
            self.anim.update(dt)
        else:
            self.anim.idx   = 0
            self.anim.timer = 0.0
        hw = self.rect.width // 2
        self.x = max(hw, min(SCREEN_W - hw, self.x + dx))
        self.rect.center = (int(self.x), int(self.y))
        if self.shoot_cd > 0:
            self.shoot_cd -= dt
        if self.inv_timer > 0:
            self.inv_timer -= dt
            self._blink = (self._blink + 1) % 6

    def try_shoot(self):
        if self.shoot_cd <= 0:
            self.shoot_cd = SHOOT_COOLDOWN_MS
            return Bullet(self.x, self.y - self.rect.height // 2,
                          self.bullet_img, -BULLET_SPEED_PX)
        return None

    def hit(self):
        if self.inv_timer > 0:
            return False
        self.lives -= 1
        self.inv_timer = INVINCIBLE_MS
        if self.lives <= 0:
            self.dead = True
        return True

    def draw(self, surface):
        if self.inv_timer > 0 and self._blink < 3:
            return
        img = self.anim.image
        surface.blit(img, (int(self.x) - img.get_width()  // 2,
                           int(self.y) - img.get_height() // 2))


# ── Enemy types ───────────────────────────────────────────────────────────────

_ETYPES = {
    "bug":    {
        "folder": os.path.join(_SS, "enemyships", "01 Bug (Animation)", "Bug 1"),
        "prefix": "bug_1_", "count": 6,
        "hp": 1, "score": 10, "spd": 90,
    },
    "danger": {
        "folder": os.path.join(_SS, "enemyships", "03 Danger"),
        "prefix": "danger_", "count": 6,
        "hp": 2, "score": 20, "spd": 130,
    },
    "heavy": {
        "folder": os.path.join(_SS, "enemyships", "02 Heavy"),
        "prefix": "heavy_", "count": 6,
        "hp": 3, "score": 35, "spd": 70,
    },
    "wings": {
        "folder": os.path.join(_SS, "enemyships", "06 Wings"),
        "prefix": "wings_", "count": 6,
        "hp": 2, "score": 25, "spd": 110,
    },
}


class Enemy:
    def __init__(self, etype, x, frames, bullet_img, spd_mult=1.0, shoot_ch=0.005):
        info          = _ETYPES[etype]
        self.etype    = etype
        self.img      = frames[0]   # static — animation frames have bad rotations
        self.bullet_img = bullet_img
        self.x        = float(x)
        self.y        = -80.0
        self.base_x   = float(x)
        self.hp       = info["hp"]
        self.score_val = info["score"]
        self.spd      = info["spd"] * spd_mult    # px/sec downward
        self.shoot_ch = shoot_ch
        self.escaped  = False
        self.dead     = False
        self.rect     = frames[0].get_rect(center=(int(x), -80))

    def update(self, dt):
        self.y += self.spd * dt / 1000.0
        self.rect.center = (int(self.x), int(self.y))
        if self.y > SCREEN_H + 40:
            self.dead    = True
            self.escaped = True   # reached bottom without being killed

    def try_shoot(self, spd_mult=1.0):
        if random.random() < self.shoot_ch:
            return Bullet(self.x, self.y + self.rect.height // 2,
                          self.bullet_img, EBULLET_SPEED_PX * spd_mult)
        return None

    def hit(self):
        self.hp -= 1
        if self.hp <= 0:
            self.dead = True
            return True
        return False

    def draw(self, surface):
        surface.blit(self.img, (int(self.x) - self.img.get_width()  // 2,
                                int(self.y) - self.img.get_height() // 2))


# ── HUD ───────────────────────────────────────────────────────────────────────

def _draw_hud(surface, font, score, lives, wave, hud_ship):
    TEXT = (200, 220, 255)
    CYAN = (100, 200, 255)
    # Score — top left
    surface.blit(font.render(f"SCORE  {score:07d}", True, TEXT), (20, 14))
    # Wave — top centre
    w_surf = font.render(f"WAVE  {wave:02d}", True, CYAN)
    surface.blit(w_surf, (SCREEN_W // 2 - w_surf.get_width() // 2, 14))
    # Lives — top right as ship icons
    gap = hud_ship.get_width() + 8
    for i in range(lives):
        surface.blit(hud_ship, (SCREEN_W - 20 - (i + 1) * gap, 10))


# ── Entry point ───────────────────────────────────────────────────────────────

def run(screen, clock):
    font     = pygame.font.Font(FONT_PATH, 30)
    font_big = pygame.font.Font(FONT_PATH, 80)

    # Player ship — 20-frame animation
    ship_frames = _load_frames(
        os.path.join(_SS, "ship", "Plane 01", "Normal"),
        "planes_01A-", 20, scale=PLAYER_SCALE)

    # Bullets
    bullet_raw  = pygame.image.load(
        os.path.join(_SS, "bullets", "Projectiles", "projectile-01.png")
    ).convert_alpha()
    bullet_img  = pygame.transform.scale(
        bullet_raw, (bullet_raw.get_width() * 2, bullet_raw.get_height() * 2))

    ebullet_raw = pygame.image.load(
        os.path.join(_SS, "bullets", "Projectiles", "projectile-02.png")
    ).convert_alpha()
    ebullet_img = pygame.transform.scale(
        ebullet_raw, (ebullet_raw.get_width() * 2, ebullet_raw.get_height() * 2))
    ebullet_img = pygame.transform.flip(ebullet_img, False, True)

    # Enemy frames — no flip; sprites naturally face downward toward the player
    eframes = {
        etype: _load_frames(info["folder"], info["prefix"],
                            info["count"], scale=ENEMY_SCALE)
        for etype, info in _ETYPES.items()
    }

    # Explosions (native: large=250×250, small=100×100, white_blast=250×250)
    exp_large      = _load_frames(
        os.path.join(_SS, "effects", "Explosion", "Large"),
        "explosion_large-", 10)
    exp_small      = _load_frames(
        os.path.join(_SS, "effects", "Explosion", "Small"),
        "explosion-", 11)
    exp_white      = _load_frames(
        os.path.join(_SS, "effects", "Explosion", "White Blast"),
        "white_blast-", 10)

    # Small ship icon for lives display
    hud_ship = pygame.transform.scale(
        ship_frames[0],
        (ship_frames[0].get_width() // 2, ship_frames[0].get_height() // 2))

    # Sounds
    _SND = os.path.join(_SS, "sounds")
    snd_laser   = pygame.mixer.Sound(os.path.join(_SND, "freesound-community-laser-gun-81720_0Q3ATYTi.wav"))
    snd_explode = pygame.mixer.Sound(os.path.join(_SND, "space-explosion-arcade-th-tqvxalmg.wav"))
    snd_engine  = pygame.mixer.Sound(os.path.join(_SND, "freesound_community-jet-engine-6753.wav"))
    snd_laser.set_volume(0.45)
    snd_explode.set_volume(0.6)
    snd_engine.set_volume(0.18)
    ch_laser  = pygame.mixer.Channel(5)
    ch_engine = pygame.mixer.Channel(6)
    ch_engine.play(snd_engine, loops=-1)   # looping engine hum

    # Music
    pygame.mixer.music.load(os.path.join(_SS, "music", "Buddy, Ryo.mp3"))
    pygame.mixer.music.set_volume(0.75)
    pygame.mixer.music.play(-1)

    # ── State ─────────────────────────────────────────────────────────────────
    bg          = Background()
    player      = Player(ship_frames, bullet_img)
    p_bullets   : list[Bullet]    = []
    e_bullets   : list[Bullet]    = []
    enemies     : list[Enemy]     = []
    explosions  : list[Explosion] = []

    score       = 0
    elapsed_ms  = 0
    spawn_timer = 0
    game_over   = False
    go_timer    = 0

    while True:
        dt = clock.tick(60)
        elapsed_ms += dt

        # ── Events ────────────────────────────────────────────────────────────
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.mixer.music.stop(); ch_engine.stop()
                return "quit"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.mixer.music.stop(); ch_engine.stop()
                    return "menu"
                if game_over and go_timer > 1500:
                    pygame.mixer.music.stop(); ch_engine.stop()
                    return "menu"

        wave     = elapsed_ms // 15000 + 1
        spd_mult = 1.0 + elapsed_ms / 60000.0

        # ── Game logic ────────────────────────────────────────────────────────
        if not game_over:
            keys = pygame.key.get_pressed()
            player.update(dt, keys)

            if keys[pygame.K_SPACE]:
                b = player.try_shoot()
                if b:
                    p_bullets.append(b)
                    if not ch_laser.get_busy():
                        ch_laser.play(snd_laser)

            for b in p_bullets: b.update(dt)
            for b in e_bullets: b.update(dt)
            p_bullets = [b for b in p_bullets if not b.dead]
            e_bullets = [b for b in e_bullets if not b.dead]

            # Spawn
            spawn_timer += dt
            spawn_ms = max(SPAWN_MIN_MS, SPAWN_BASE_MS - (wave - 1) * 160)
            if spawn_timer >= spawn_ms:
                spawn_timer = 0
                etype = random.choices(
                    ["bug", "danger", "heavy", "wings"],
                    weights=[40, 25, 15, 20])[0]
                x        = random.randint(70, SCREEN_W - 70)
                shoot_ch = 0.004 + wave * 0.001
                enemies.append(Enemy(etype, x, eframes[etype],
                                     ebullet_img, spd_mult, shoot_ch))

            for e in enemies:
                e.update(dt)
                eb = e.try_shoot(spd_mult)
                if eb:
                    e_bullets.append(eb)

            # Player bullet → enemy
            for pb in p_bullets:
                if pb.dead: continue
                for e in enemies:
                    if e.dead: continue
                    if pb.rect.colliderect(e.rect):
                        pb.dead = True
                        was_tanky = _ETYPES[e.etype]["hp"] >= 2
                        killed    = e.hit()
                        if killed:
                            score += e.score_val
                            snd_explode.play()
                            # Tanky enemies (heavy/danger/wings) get a white blast
                            exf = exp_white if was_tanky else exp_large
                            explosions.append(Explosion(int(e.x), int(e.y), exf))
                        else:
                            explosions.append(Explosion(int(e.x), int(e.y), exp_small))
                        break

            # Enemy bullet / body → player
            for eb in e_bullets:
                if not eb.dead and eb.rect.colliderect(player.rect):
                    eb.dead = True
                    if player.hit():
                        # Small white blast on the player to signal the hit
                        explosions.append(Explosion(int(player.x), int(player.y), exp_white))
            for e in enemies:
                if not e.dead and e.rect.colliderect(player.rect):
                    e.dead = True
                    explosions.append(Explosion(int(e.x), int(e.y), exp_large))
                    player.hit()

            # Escaped enemies (reached bottom) damage the player
            for e in enemies:
                if e.dead and e.escaped:
                    player.hit()

            enemies = [e for e in enemies if not e.dead]
            for ex in explosions: ex.update(dt)
            explosions = [ex for ex in explosions if not ex.dead]

            if player.dead:
                game_over = True
                pygame.mixer.music.stop()
                ch_engine.stop()
        else:
            go_timer += dt

        # ── Draw ──────────────────────────────────────────────────────────────
        bg.tick(dt)
        bg.draw(screen)

        for e  in enemies:    e.draw(screen)
        for pb in p_bullets:  pb.draw(screen)
        for eb in e_bullets:  eb.draw(screen)
        for ex in explosions: ex.draw(screen)
        if not player.dead:
            player.draw(screen)

        _draw_hud(screen, font, score, player.lives, wave, hud_ship)

        if game_over and go_timer > 600:
            # Full-screen game over — same style as the main game
            _hud.draw_game_over_arcade(screen, score)

        apply_crt(screen)
        pygame.display.flip()
