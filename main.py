"""
main.py — Game loop for urmisszio
Ported from Mission Python by Sean McManus (pygame zero → pygame)

Wires together: room, hud, doors, inventory, hazards, player
All delta-time based; no clock.schedule calls.
"""
import pygame
import sys
import math
import random

import mainmenu
import shooter
import loadscreen
from mainmenu import apply_crt, _add_glitch_effect
import room
import hud
import doors
import inventory
import hazards
import player as pl

from data import (
    OBJECTS, PROPS, PROPS_DEFAULT,
    PLAYER_NAME, MAP_WIDTH,
    items_player_may_stand_on,
)

# ── Pygame init ───────────────────────────────────────────────────────────────

pygame.init()
pygame.mixer.init()

SCREEN_W, SCREEN_H = 1280, 720
screen = pygame.display.set_mode((SCREEN_W, SCREEN_H), vsync=1)
pygame.display.set_caption("urmisszio")
clock = pygame.time.Clock()

FONT = pygame.font.Font("assets/fonts/AeogoPxltdNext-5y27B.ttf", 22)

# ── Module inits (require display to exist first) ─────────────────────────────

hud.init_hud(FONT)
room.init_pillars()
pl.init_player()

# ── Sound loader (graceful — missing files are silently skipped) ──────────────

_sounds = {}

def _load_sound(name, filename):
    try:
        _sounds[name] = pygame.mixer.Sound(f"assets/audio/sounds/{filename}")
    except Exception:
        pass

_load_sound("pickup",              "pickup.wav")
_load_sound("drop",                "drop.wav")
_load_sound("combine",             "combine.wav")
_load_sound("ouch",                "ouch.wav")
_load_sound("doors",               "doors.wav")
_load_sound("alarm",               "alarm.wav")
_load_sound("gameover",            "gameover.wav")
_load_sound("take_off",            "take_off.wav")
_load_sound("completion",          "completion.wav")
_load_sound("steelmusic",          "steelmusic.wav")
_load_sound("say_status_report",   "say_status_report.wav")
_load_sound("say_airlock_open",    "say_airlock_open.wav")
_load_sound("say_doors_open",      "say_doors_open.wav")
_load_sound("say_doors_closed",    "say_doors_closed.wav")
_load_sound("say_breach",          "say_breach.wav")
_load_sound("say_air_low",         "say_air_low.wav")
_load_sound("say_act_now",         "say_act_now.wav")
_load_sound("say_mission_fail",    "say_mission_fail.wav")
_load_sound("say_mission_complete","say_mission_complete.wav")
_load_sound("mission",             "mission.wav")

def play(name, loops=0):
    if name in _sounds:
        _sounds[name].play(loops)

# ── Glitch sound pool ─────────────────────────────────────────────────────────

_glitch_sfx = []
for _gf in [
    "assets/music/glitches/dragon-studio-glitch-effect-1-397982.wav",
    "assets/music/glitches/dragon-studio-glitch-effect-2-397980.wav",
    "assets/music/glitches/dragon-studio-glitch-noise-454247.wav",
    "assets/music/glitches/dragon-studio-glitch-sound-effect-443130.wav",
    "assets/music/glitches/virtual_vibes-computer-distortion-glitch-400944.wav",
]:
    try:
        _glitch_sfx.append(pygame.mixer.Sound(_gf))
    except Exception:
        pass

_glitch_channel = pygame.mixer.Channel(2)   # dedicated channel so it doesn't cut ouch/pickup
_alarm_channel  = pygame.mixer.Channel(3)   # dedicated so we can stop it cleanly on death

def play_glitch():
    if _glitch_sfx and not _glitch_channel.get_busy():
        _glitch_channel.play(random.choice(_glitch_sfx))


# ── Main game function ────────────────────────────────────────────────────────

def play_game(screen, clock):
    """
    Run one full play session.
    Returns 'menu' when the player escapes or the game ends,
    or 'quit' if the window is closed.
    """

    # ── Reset mutable world state so replays start fresh ─────────────────────
    for key, val in PROPS_DEFAULT.items():
        PROPS[key] = list(val)
    inventory.reset_inventory()
    doors.reset_doors()

    # ── Game state ────────────────────────────────────────────────────────────

    current_room     = 31
    player_y, player_x = 2, 5
    from_player_y, from_player_x = 2, 5   # tile the player just stepped FROM
    player_direction = "down"
    player_frame     = 0                   # 0 = idle, 1-8 = walk animation
    player_offset_x  = 0.0
    player_offset_y  = 0.0

    air    = 100
    energy = 100
    suit_stitched = False
    air_fixed     = False
    game_over     = False
    game_over_reason = ""
    game_won      = False
    launch_frame  = 0
    _win_sounds_played = False

    # ── HUD message state (redrawn every frame) ───────────────────────────────

    hud_msg_0 = ""
    hud_msg_1 = ""

    # ── Timers (ms) ───────────────────────────────────────────────────────────

    AIR_COUNTDOWN_MS   = 5_000
    ALARM_DELAY_MS     = 10_000
    PLAYER_ANIM_MS     = 25
    TRANSPARENCY_MS    = 50
    LAUNCH_FRAME_MS    = 250
    HIT_FLASH_TOTAL    = 350
    CRITICAL_LEVEL     = 20

    _air_timer         = 0
    _alarm_timer       = 0
    _alarm_shown       = False
    _player_anim_timer = 0
    _trans_timer       = 0
    _launch_timer      = 0
    _hit_flash_timer   = 0

    # ── Helpers ───────────────────────────────────────────────────────────────

    def end_the_game(reason):
        nonlocal game_over, game_over_reason
        game_over        = True
        game_over_reason = reason
        pygame.mixer.stop()
        play("say_mission_fail")
        play("gameover")

    def deplete_energy(penalty):
        nonlocal energy, _hit_flash_timer
        if game_over:
            return
        energy -= penalty
        _hit_flash_timer = HIT_FLASH_TOTAL
        play_glitch()
        if energy < 1:
            energy = 0
            end_the_game("You're out of energy!")

    def _draw_player_fn(surface):
        pl.draw_player(surface, player_direction, player_frame,
                       player_y, player_x, player_offset_y, player_offset_x)

    def start_room():
        nonlocal hud_msg_0, hud_msg_1, player_frame, player_offset_x, player_offset_y
        player_frame    = 0
        player_offset_x = 0.0
        player_offset_y = 0.0
        hud_msg_0 = room.room_name
        hud_msg_1 = ""
        if current_room == 26:
            doors.start_airlock()
        else:
            doors.stop_airlock()
        hazards.hazard_stop()
        hazards.hazard_start(current_room)

    def _apply_use_result(res):
        nonlocal air, energy, suit_stitched, air_fixed, game_won, launch_frame
        nonlocal hud_msg_0, hud_msg_1, _win_sounds_played

        air           = res["air"]
        energy        = res["energy"]
        suit_stitched = res["suit_stitched"]
        air_fixed     = res["air_fixed"]

        hud_msg_0 = res["message"]
        if res["secondary"]:
            hud_msg_1 = res["secondary"]

        if res["sound"]:
            play(res["sound"])
            if res["sound"] == "say_doors_open":
                play("doors")

        if res["rescue_ship"]:
            PROPS[40][0] = 13

        if res["open_engineering"]:
            PROPS[25][0] = 0
            PROPS[26][0] = 0
            room.generate_map(current_room)
            doors.start_engineering_timer()

        if res["open_door"] is not None:
            doors.open_door(res["open_door"])

        if res["game_won"]:
            game_won           = True
            launch_frame       = 0
            _win_sounds_played = False
            play("take_off")

    def _shut_engineering_door():
        nonlocal player_y, hud_msg_1
        PROPS[25][0] = 32
        PROPS[26][0] = 27
        room.generate_map(current_room)
        if current_room == 27:
            player_y = doors.close_door(26, player_y, room.room_height)
        if current_room == 32:
            player_y = doors.close_door(25, player_y, room.room_height)
        hud_msg_1 = "The computer tells you the doors are closed."
        play("say_doors_closed")

    # ── Build starting room ───────────────────────────────────────────────────

    room.generate_map(current_room)
    start_room()
    play("mission")

    # ── Game loop ─────────────────────────────────────────────────────────────

    while True:
        dt = clock.tick(60)

        # ── Events ────────────────────────────────────────────────────────────
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"

            if event.type == pygame.KEYDOWN:

                # ESC always returns to main menu
                if event.key == pygame.K_ESCAPE:
                    pygame.mixer.stop()
                    return "menu"

                # After game over or win: any key → back to main menu
                if game_over or game_won:
                    pygame.mixer.stop()
                    return "menu"

                # One-shot actions (faithful key mapping to MissionPython)
                if event.key == pygame.K_g:
                    msg, snd = inventory.pick_up_object(
                        current_room, player_y, player_x)
                    hud_msg_0 = msg
                    if snd:
                        play(snd)

                elif event.key == pygame.K_TAB and inventory.in_my_pockets:
                    inventory.cycle_selected_item()

                elif event.key == pygame.K_d and inventory.item_carrying:
                    msg, snd = inventory.drop_object(player_y, player_x, current_room)
                    hud_msg_0 = msg
                    if snd:
                        play(snd)

                elif event.key == pygame.K_SPACE:
                    msg, snd = inventory.examine_object(
                        current_room, player_y, player_x)
                    if msg:
                        hud_msg_0 = msg
                    if snd:
                        play(snd)

                elif event.key == pygame.K_u:
                    res = inventory.use_object(
                        current_room, player_y, player_x,
                        air, energy, suit_stitched, air_fixed, game_over)
                    _apply_use_result(res)

        # ── Game over overlay ─────────────────────────────────────────────────

        if game_over:
            hud.draw_game_over(screen, game_over_reason)
            for _ in range(20):
                _add_glitch_effect(SCREEN_H, SCREEN_W, screen, "maximum")
            apply_crt(screen, glitching=True)
            pygame.display.flip()
            continue

        # ── Win / launch sequence ─────────────────────────────────────────────

        if game_won:
            screen.fill((5, 8, 15))
            room.draw_room(screen, current_room, -1, lambda s: None)
            _launch_timer += dt
            if _launch_timer >= LAUNCH_FRAME_MS:
                _launch_timer = 0
                if launch_frame < 9:
                    launch_frame += 1
            if launch_frame < 9:
                room.draw_image(screen, room.img("rescue_ship"),        8 - launch_frame, 6)
                room.draw_shadow(screen, room.img("rescue_ship_shadow"), 8,               6)
            else:
                if not _win_sounds_played:
                    _win_sounds_played = True
                    play("completion")
                    play("say_mission_complete")
                hud.draw_mission_complete(screen)
            pygame.display.flip()
            continue

        # ── Air countdown ─────────────────────────────────────────────────────

        _air_timer += dt
        if _air_timer >= AIR_COUNTDOWN_MS:
            _air_timer = 0
            air -= 1
            if air == 20:
                play("say_air_low")
            if air == 10:
                play("say_act_now")
            if air < 1:
                air = 0
                end_the_game("You're out of air!")

        if not _alarm_shown:
            _alarm_timer += dt
            if _alarm_timer >= ALARM_DELAY_MS:
                _alarm_shown = True
                hud_msg_1 = (f"Air is running out, {PLAYER_NAME}! "
                             "Get to safety, then radio for help!")
                if "alarm" in _sounds:
                    _alarm_channel.play(_sounds["alarm"], loops=3)
                play("say_breach")

        # ── Player animation advance ──────────────────────────────────────────

        if player_frame > 0:
            _player_anim_timer += dt
            if _player_anim_timer >= PLAYER_ANIM_MS:
                _player_anim_timer = 0
                player_frame      += 1
                if player_frame == 9:
                    player_frame    = 0
                    player_offset_x = 0.0
                    player_offset_y = 0.0

        # ── Movement (only when idle between tiles) ───────────────────────────

        if player_frame == 0:
            keys = pygame.key.get_pressed()
            old_player_x = player_x
            old_player_y = player_y
            moved = False

            if keys[pygame.K_RIGHT]:
                from_player_x, from_player_y = player_x, player_y
                player_x += 1;  player_direction = "right";  moved = True
            elif keys[pygame.K_LEFT]:
                from_player_x, from_player_y = player_x, player_y
                player_x -= 1;  player_direction = "left";   moved = True
            elif keys[pygame.K_UP]:
                from_player_x, from_player_y = player_x, player_y
                player_y -= 1;  player_direction = "up";     moved = True
            elif keys[pygame.K_DOWN]:
                from_player_x, from_player_y = player_x, player_y
                player_y += 1;  player_direction = "down";   moved = True

            if moved:
                player_frame       = 1
                _player_anim_timer = 0

            # ── Room transitions ──────────────────────────────────────────────

            if player_x == room.room_width:              # exit RIGHT
                hazards.hazard_stop()
                current_room += 1
                room.generate_map(current_room)
                player_x = 0
                player_y = room.room_height // 2
                start_room()
                continue

            if player_x == -1:                           # exit LEFT
                hazards.hazard_stop()
                current_room -= 1
                room.generate_map(current_room)
                player_x = room.room_width - 1
                player_y = room.room_height // 2
                start_room()
                continue

            if player_y == room.room_height:             # exit BOTTOM
                hazards.hazard_stop()
                current_room += MAP_WIDTH
                room.generate_map(current_room)
                player_y = 0
                player_x = room.room_width // 2
                start_room()
                continue

            if player_y == -1:                           # exit TOP
                hazards.hazard_stop()
                current_room -= MAP_WIDTH
                room.generate_map(current_room)
                player_y = room.room_height - 1
                player_x = room.room_width // 2
                start_room()
                continue

            # ── Wall / hazard collision — restore old position ────────────────

            if (room.room_map[player_y][player_x] not in items_player_may_stand_on
                    or room.hazard_map[player_y][player_x] != 0):
                player_x    = old_player_x
                player_y    = old_player_y
                player_frame = 0

            # ── Toxic floor ───────────────────────────────────────────────────

            if room.room_map[player_y][player_x] == 48:
                deplete_energy(1)

        # ── Smooth walk offsets ───────────────────────────────────────────────

        if player_frame > 0:
            t = player_frame / 8.0
            if player_direction == "right":
                player_offset_x = -1 + t;  player_offset_y = 0.0
            elif player_direction == "left":
                player_offset_x =  1 - t;  player_offset_y = 0.0
            elif player_direction == "up":
                player_offset_x = 0.0;  player_offset_y =  1 - t
            elif player_direction == "down":
                player_offset_x = 0.0;  player_offset_y = -1 + t

        # ── Wall transparency ─────────────────────────────────────────────────

        _trans_timer += dt
        if _trans_timer >= TRANSPARENCY_MS:
            _trans_timer = 0
            room.adjust_wall_transparency(player_y, player_x)

        # ── Door animation ────────────────────────────────────────────────────

        anim_was_active = doors.is_animating()
        doors.update_door_anim(dt)
        if anim_was_active and not doors.is_animating():
            room.generate_map(current_room)

        # ── Airlock (room 26) ─────────────────────────────────────────────────

        if current_room == 26:
            props_bin_full = (PROPS[63][0] == 26
                             and PROPS[63][1] == 8
                             and PROPS[63][2] == 2)
            changes = doors.update_airlock(
                dt, current_room, player_y, player_x, props_bin_full)
            for (row, col, val) in changes:
                room.room_map[row][col] = val

        # ── Engineering door 60-second timer ─────────────────────────────────

        if doors.update_engineering_timer(dt):
            _shut_engineering_door()

        # ── Hazards ───────────────────────────────────────────────────────────

        energy_hit = hazards.update_hazards(
            dt, current_room,
            player_y, player_x,
            from_player_y, from_player_x, player_frame,
            game_over)
        if energy_hit:
            play("ouch")
            deplete_energy(energy_hit)

        # ── Draw ──────────────────────────────────────────────────────────────

        screen.fill((5, 8, 15))

        hazard_draws = hazards.get_hazard_draws(current_room)
        room.draw_room(screen, current_room, player_y, _draw_player_fn, hazard_draws)
        hud.draw_room_dim(screen)

        if doors.is_animating():
            frame_data = doors.get_current_frame()
            if frame_data:
                img_name, shad_name, dy, dx = frame_data
                room.draw_image(screen, room.img(img_name), dy, dx)
                if shad_name:
                    room.draw_shadow(screen, room.img(shad_name), dy, dx)

        if current_room == 26:
            air_img, air_shad = doors.get_airlock_frame_images()
            door_y, door_x = PROPS[21][1], PROPS[21][2]
            room.draw_image(screen, room.img(air_img), door_y, door_x)
            if air_shad:
                room.draw_shadow(screen, room.img(air_shad), door_y, door_x)

        hud.draw_hud_panels(screen)
        if hud_msg_0:
            hud.show_text(screen, hud_msg_0, 0)
        else:
            hud.draw_room_name(screen, room.room_name)
        if hud_msg_1:
            hud.show_text(screen, hud_msg_1, 1)
        hud.display_inventory(screen, inventory.in_my_pockets,
                              inventory.selected_item, OBJECTS, room.img)
        hud.draw_energy_air(screen, air, energy)

        # ── Screen flash ──────────────────────────────────────────────────────

        _hit_flash_timer = max(0, _hit_flash_timer - dt)
        hit_alpha = int(150 * _hit_flash_timer / HIT_FLASH_TOTAL)

        crit_alpha = 0
        if air <= CRITICAL_LEVEL or energy <= CRITICAL_LEVEL:
            crit_alpha = int(abs(math.sin(pygame.time.get_ticks() * 0.004)) * 90)

        flash_alpha = max(hit_alpha, crit_alpha)
        if flash_alpha > 0:
            hud.draw_flash(screen, flash_alpha)

        if _hit_flash_timer > 0:
            for _ in range(6):
                _add_glitch_effect(SCREEN_H, SCREEN_W, screen, "maximum")
        elif crit_alpha > 0:
            _add_glitch_effect(SCREEN_H, SCREEN_W, screen, "medium")

        apply_crt(screen)
        pygame.display.flip()


# ── Top-level loop: menu → game → menu … ─────────────────────────────────────

result = mainmenu.run(screen, clock)

while True:
    if result == "quit":
        pygame.quit()
        sys.exit()

    elif result == "arcade":
        sub = shooter.run(screen, clock)
        if sub == "quit":
            pygame.quit()
            sys.exit()
        result = mainmenu.run(screen, clock)

    elif result == "start":
        loadscreen.run(screen, clock)
        result = play_game(screen, clock)
        # result is "menu" or "quit" — loop back to top

    elif result == "menu":
        result = mainmenu.run(screen, clock)

    else:
        # Fallback — shouldn't happen
        pygame.quit()
        sys.exit()
