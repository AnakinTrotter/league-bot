# Anakin Trotter
# 2/28/2021
# This is a robust League of Legends bot for automatically leveling up accounts.
# It will attempt to restart itself if something goes wrong.

import subprocess
import pyautogui
import pydirectinput
import os
import time
import random

# Settings:
# Stay signed in
# Borderless
# HUD Scale: 0
# Shop Scale: 44
# Minimap Scale: 100
# Minimap on right
# Auto Attack: Enabled
# Default keybindings
# Quick Cast All (no indicator)
# Colorblind mode off

# customizable:
client_dir = "C:/Riot Games/League of Legends/LeagueClient.exe"

# only change if broken
client_process = "LeagueClient.exe"
game_process = "League of Legends.exe"
states = ["queue", "champ select", "loading", "game", "post"]
state = states[0]
nexus = [1860, 720]
images = {
    "play": "images/play button.png",
    "coop": "images/coop.png",
    "beginner": "images/beginner.png",
    "confirm": "images/confirm.png",
    "queue": "images/find match.png",
    "accept": "images/accept button.png",
    "free": "images/free champ.png",
    "pick": "images/lock in.png",
    "nexus": "images/nexus.png",
    "win": "images/continue.png",
    "ok": "images/ok.png",
    "again": "images/play again button.png",
    "missions": "images/missions.png",
    "select": "images/select.png",
    "honor": "images/honor.png",
    "clash": "images/got it.png",
    "choose": "images/choose.png",
    "qing": "images/in q.png"
}


# https://stackoverflow.com/questions/7787120/check-if-a-process-is-running-or-not-on-windows-with-python
def process_exists(process_name):
    call = 'TASKLIST', '/FI', 'imagename eq %s' % process_name
    # use buildin check_output right away
    output = subprocess.check_output(call).decode()
    # check in last line for process name
    last_line = output.strip().split('\r\n')[-1]
    # because Fail message could be translated
    return last_line.lower().startswith(process_name.lower())


def click(loc, delay=random.uniform(0.1, 0.4), button="left"):
    pyautogui.moveTo(x=loc[0], y=loc[1], duration=delay, tween=pyautogui.easeInSine)
    pydirectinput.mouseDown()
    time.sleep(random.uniform(0.05, 0.1))
    pydirectinput.mouseUp()


def click_button(image, delay=random.uniform(0.1, 0.4), timeout=5, button="left"):
    start_time = time.time()
    loc = None
    while time.time() - start_time < timeout:
        loc = pyautogui.locateCenterOnScreen(image=image, confidence=0.8, grayscale=True)
        if loc is not None:
            break
    if loc is None:
        print("No button matching image " + image + " was found. Continuing...")
        return False
    click(loc, delay, button)
    print("Button matching image " + image + " was found.")
    return True


def open_client():
    if process_exists(client_process):
        os.system(str("taskkill /IM " + client_process + " /F"))
    if process_exists(game_process):
        os.system(str("taskkill /IM " + game_process + " /F"))
    os.startfile(client_dir)


def make_lobby():
    print("Making lobby.")
    global state
    if (click_button(images.get("play")) and click_button(images.get("coop"))
            and click_button(images.get("beginner")) and click_button(images.get("confirm"))):
        state = states[0]
        return True
    else:
        pyautogui.click()
        if (click_button(images.get("coop"))
                and click_button(images.get("beginner")) and click_button(images.get("confirm"))):
            state = states[0]
            return True
    print("Unable to make lobby.")
    return False


def queue(timeout=120):
    while click_button(images.get("queue")):
        print("Attempting to start queue.")
    start_time = time.time()
    print("Queue successfully started at: " + str(start_time))
    global state
    while time.time() - start_time < timeout:
        if click_button(images.get("accept")):
            start_time = time.time()
            while time.time() - start_time < 15:
                if pyautogui.locateOnScreen(image=images.get("free"), confidence=0.8, grayscale=True) is not None:
                    state = states[1]
                    return True
                if pyautogui.locateOnScreen(image=images.get("choose"), confidence=0.8, grayscale=True) is not None:
                    state = states[1]
                    return True
        if pyautogui.locateOnScreen(image=images.get("choose"), confidence=0.8, grayscale=True) is not None:
            state = states[1]
            return True
    if pyautogui.locateOnScreen(image=images.get("choose"), confidence=0.8, grayscale=True) is not None or \
            process_exists(game_process):
        state = states[1]
        return True
    print("Queue timed out.")
    return False


def champ_select():
    print("Selecting champion.")
    time.sleep(1)
    global state
    free_champs = pyautogui.locateAllOnScreen(image=images.get("free"), confidence=0.8, grayscale=True)
    for champ in free_champs:
        champ = [champ[0] - 20, champ[1] + 20]
        click(champ, 0.25)
        if click_button(image=images.get("pick"), delay=0):
            state = states[2]
            return True
    click(loc=[700, 350])
    if click_button(image=images.get("pick"), delay=0):
        state = states[2]
        return True
    print("No champions found in champ select.")
    return False


def loading_screen(timeout=420):
    print("Waiting for game to start.")
    start_time = time.time()
    while time.time() - start_time < timeout:
        nexus_loc = pyautogui.locateOnScreen(image=images.get("nexus"), confidence=0.8, grayscale=True)
        if nexus_loc is not None:
            global nexus, state
            # if abs(nexus_loc[0] - nexus[0]) > 100 or abs(nexus_loc[1] - nexus[1]) > 100:
            #     nexus = [nexus_loc[0], nexus_loc[1]]
            state = states[3]
            return True
    print("Loading screen timed out.")
    return False


def game():
    time.sleep(1)
    pydirectinput.press("y")
    pydirectinput.press("p")
    pydirectinput.keyDown("ctrl")
    pydirectinput.press("l")
    pydirectinput.keyUp("ctrl")
    pydirectinput.write("dor")
    pydirectinput.press("enter")
    pydirectinput.press("p")
    start_time = time.time()
    timer = start_time
    while not click_button(image=images.get("win"), timeout=1):
        pydirectinput.press("a")
        if time.time() - start_time < 600:
            click(loc=[nexus[0] + 10 * random.random() - 150, nexus[1] + 10 * random.random() + 150])
        else:
            click(loc=[nexus[0] + 10 * random.random(), nexus[1] + 10 * random.random()])
        time.sleep(random.random())
        if random.random() > 0.75:
            pyautogui.moveTo(x=1160, y=300, duration=0.05, tween=pyautogui.easeInSine)
            pydirectinput.press("e")
            pydirectinput.press("w")
            pydirectinput.press("q")
        if random.random() > 0.95:
            pyautogui.moveTo(x=1160, y=300, duration=0.05, tween=pyautogui.easeInSine)
            pydirectinput.press("r")
            pydirectinput.press("d")
            pydirectinput.press("f")
        pydirectinput.keyDown("ctrl")
        pydirectinput.press("r")
        pydirectinput.press("q")
        pydirectinput.press("w")
        pydirectinput.press("e")
        pydirectinput.keyUp("ctrl")
        if time.time() - timer > 3:
            pydirectinput.press("p")
            pydirectinput.keyDown("ctrl")
            pydirectinput.press("l")
            pydirectinput.keyUp("ctrl")
            pydirectinput.press("enter")
            pydirectinput.press("p")
            timer = time.time()
    global state
    state = states[4]
    return True


def post_game():
    start_time = time.time()
    honor_loc = None
    while time.time() - start_time < 10:
        pyautogui.click()
        honor_loc = pyautogui.locateCenterOnScreen(image=images.get("honor"), confidence=0.8, grayscale=True)
        if honor_loc is not None:
            click(loc=honor_loc)
            break
    if honor_loc is None:
        pyautogui.click()
    start_time = time.time()
    while not click_button(image=images.get("again"), timeout=1):
        click_button(image=images.get("ok"), timeout=10)
        if time.time() - start_time > 60:
            print("Post game lobby timed out.")
            return False
    global state
    state = states[0]
    return True


# restarts the game if there is an error
def fail_safe(tries=5, timeout=90):
    print("Starting game...")
    global state
    state = None
    open_client()
    start_time = time.time()
    while tries > 0:
        if process_exists(client_process) and \
                pyautogui.locateOnScreen(image=images.get("play"), confidence=0.8, grayscale=True) is not None and \
                make_lobby():
            return
        else:
            if pyautogui.locateOnScreen(image=images.get("nexus"), confidence=0.8, grayscale=True) is not None:
                state = "game"
                return
            missions = pyautogui.locateOnScreen(image=images.get("missions"), confidence=0.8, grayscale=True)
            if missions is not None:
                pyautogui.moveTo(x=missions[0], y=missions[1] + 300)
                click_button(image=images.get("select"))
                time.sleep(1)
                click_button(image=images.get("ok"))
            else:
                click_button(image=images.get("clash"))
        if time.time() - start_time > timeout:
            start_time = time.time()
            tries -= 1
            open_client()
            print("Failed to load client. Retrying...")
    exit("Failed to load client (patching?).")


def read_config():
    config = open("config.txt")
    if config.readline().lower()[8:].strip() != "true":
        config.close()
        return
    print("Loading config...")
    global client_dir
    client_dir = config.readline()[14:].strip()
    config.close()


read_config()
if pyautogui.locateOnScreen(image=images.get("nexus"), confidence=0.8, grayscale=True) is not None:
    state = "game"
else:
    fail_safe()
while True:
    worked = True
    if state == "queue":
        worked = queue()
    elif state == "champ select":
        worked = champ_select()
    elif state == "loading":
        worked = loading_screen()
    elif state == "game":
        worked = game()
    elif state == "post":
        worked = post_game()
    else:
        worked = False
    if not worked:
        print("FATAL ERROR! Attempting fail safe measures...")
        fail_safe()
