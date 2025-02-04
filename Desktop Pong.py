import os
import shutil
import ctypes
import time
import random
import winreg
import subprocess
import pyautogui
import threading
import winsound
import sys

from Balls_Pictures import white_ball, green_ball, blue_ball, red_ball, purple_ball, yellow_ball, cyan_ball


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


beep_sequence = [
    (493, 200),
    (370, 200),
    (392, 200),
    (440, 200),
    (392, 200),
    (370, 200),
    (329, 200),
    (329, 200),
    (392, 200),
    (493, 200),
    (440, 200),
    (392, 200),
    (370, 200),
    (370, 200),
    (392, 200),
    (440, 200),
    (493, 200),
    (392, 200),
    (329, 200),
    (329, 300),
    (440, 200),
    (440, 200),
    (523, 200),
    (659, 200),
    (587, 200),
    (523, 200),
    (493, 200),
    (493, 200),
    (392, 200),
    (493, 200),
    (440, 200),
    (392, 200),
    (370, 200),
    (370, 200),
    (392, 200),
    (440, 200),
    (493, 200),
    (392, 200),
    (329, 200),
    (329, 800)
]

beep_index = 0


def play_next_beep():
    global beep_index

    threading.Thread(
        target=lambda: winsound.Beep(
            beep_sequence[beep_index][0],
            beep_sequence[beep_index][1]
        )
    ).start()

    beep_index = (beep_index + 1) % len(beep_sequence)


user32 = ctypes.windll.user32
VK_ESCAPE = 0x1B
VK_1 = 0x31
VK_2 = 0x32

SCREEN_X, SCREEN_Y = 1920, 1040
BALL_SIZE = 65
COLOR_CHANGE_DELAY = 88
FRICTION_DECAY = 0.99

colors = [white_ball, green_ball, blue_ball,
          red_ball, purple_ball, yellow_ball, cyan_ball]
previous_color = None

mode = 1


def get_new_color():
    global previous_color
    available_colors = [color for color in colors if color != previous_color]
    new_color = random.choice(available_colors)
    previous_color = new_color
    return new_color


def will_collide(mode, ball_x, ball_y, speed_x, speed_y, steps=70):
    if mode == 1:
        future_x = ball_x + speed_x * steps
        future_y = ball_y + speed_y * steps
    else:
        future_x, future_y = ball_x, ball_y
        temp_speed_x, temp_speed_y = speed_x, speed_y
        for _ in range(steps):
            future_x += temp_speed_x
            future_y += temp_speed_y
            temp_speed_x *= FRICTION_DECAY
            temp_speed_y *= FRICTION_DECAY
            if abs(temp_speed_x) < 0.1 and abs(temp_speed_y) < 0.1:
                break
    return future_x >= SCREEN_X or future_x <= 0 or future_y >= SCREEN_Y or future_y <= 0


def set_icon_alignment(enabled):
    try:
        registry_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                                      r"SOFTWARE\Microsoft\Windows\Shell\Bags\1\Desktop", 0, winreg.KEY_READ)

        current_value, _ = winreg.QueryValueEx(registry_key, "FFLAGS")
        winreg.CloseKey(registry_key)

        original_value = current_value
        desired_value = 1075839520 if enabled else 1075839524

        if current_value != desired_value:
            subprocess.run(['reg', 'add', r'HKCU\SOFTWARE\Microsoft\Windows\Shell\Bags\1\Desktop',
                           '/v', 'FFLAGS', '/t', 'REG_DWORD', '/d', str(desired_value), '/f'])
            print("Icon alignment set successfully.")

        return original_value

    except Exception as e:
        print(f"Registry modification failed: {e}")
        return None


def restore_icon_alignment(original_value):
    if original_value is not None:
        try:
            subprocess.run(['reg', 'add', r'HKCU\SOFTWARE\Microsoft\Windows\Shell\Bags\1\Desktop',
                           '/v', 'FFLAGS', '/t', 'REG_DWORD', '/d', str(original_value), '/f'])
            print("Icon alignment restored.")
        except Exception as e:
            print(f"Failed to restore icon alignment: {e}")


DESKTOP = os.path.join(os.path.expanduser("~"), "Desktop")
BACKUP = os.path.join(os.path.expanduser("~"), "Documents", "Desktop_Backup")
os.makedirs(BACKUP, exist_ok=True)


def move_files_to_backup():
    for item in os.listdir(DESKTOP):
        src, dst = os.path.join(DESKTOP, item), os.path.join(BACKUP, item)
        if os.path.isfile(src) or os.path.isdir(src):
            shutil.move(src, dst)


def restore_files_from_backup():
    for item in os.listdir(BACKUP):
        shutil.move(os.path.join(BACKUP, item), os.path.join(DESKTOP, item))


def save_ball_image(ball_data):
    with open(os.path.join(DESKTOP, "Ball.png"), "wb") as f:
        f.write(ball_data)


def ball_logic():
    global mode

    desktop_utils = ctypes.WinDLL(resource_path("Movement API.dll"))
    desktop_utils.RepositionItem.argtypes = (
        ctypes.c_int, ctypes.c_int, ctypes.c_int)
    desktop_utils.RepositionItem.restype = ctypes.c_long

    x, y = 0, 0
    speed_x, speed_y = 7, 7
    index = 0
    color_change_pending = False
    color_change_cooldown = 0
    sound_timer = 0

    prev_mouse_x, prev_mouse_y = pyautogui.position()

    original_value = set_icon_alignment(False)
    move_files_to_backup()
    time.sleep(1)
    save_ball_image(white_ball)

    try:
        while True:
            if user32.GetAsyncKeyState(VK_ESCAPE) & 1:
                break
            if user32.GetAsyncKeyState(VK_1) & 1:
                mode = 1
                print("Switched to Mode 1: Classic physics")
            if user32.GetAsyncKeyState(VK_2) & 1:
                mode = 2
                print("Switched to Mode 2: Mouse interaction with friction")

            mouse_x, mouse_y = pyautogui.position()
            mouse_dx = mouse_x - prev_mouse_x
            mouse_dy = mouse_y - prev_mouse_y
            prev_mouse_x, prev_mouse_y = mouse_x, mouse_y

            if color_change_cooldown > 0:
                color_change_cooldown -= 1

            if sound_timer > 0:
                sound_timer -= 1

            if will_collide(mode, x, y, speed_x, speed_y) and not color_change_pending and color_change_cooldown == 0:
                save_ball_image(get_new_color())
                color_change_pending = True
                color_change_cooldown = COLOR_CHANGE_DELAY

            if x + speed_x > SCREEN_X - BALL_SIZE or x + speed_x < 0:
                speed_x = -speed_x
                color_change_pending = False
                if sound_timer == 0:
                    play_next_beep()
                    sound_timer = 5

            if y + speed_y > SCREEN_Y - BALL_SIZE or y + speed_y < 0:
                speed_y = -speed_y
                color_change_pending = False
                if sound_timer == 0:
                    play_next_beep()
                    sound_timer = 5

            if mode == 2:
                if x < mouse_x < x + BALL_SIZE and y < mouse_y < y + BALL_SIZE:
                    speed_x += mouse_dx * 0.5
                    speed_y += mouse_dy * 0.5

                speed_x *= FRICTION_DECAY
                speed_y *= FRICTION_DECAY

                if abs(speed_x) < 0.1:
                    speed_x = 0
                if abs(speed_y) < 0.1:
                    speed_y = 0

            x += speed_x
            y += speed_y
            desktop_utils.RepositionItem(index, int(x), int(y))

            time.sleep(0.001)
    finally:
        restore_icon_alignment(original_value)
        restore_files_from_backup()
        print("Desktop restored.")


if __name__ == "__main__":
    ball_logic()
