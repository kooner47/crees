import sys
from playsound import playsound
import win32gui
import win32api
import win32con
from mss import mss
import cv2
import pytesseract
import numpy as np
from time import sleep
from bader import execute_events, read_events
from text import extract_codes, extract_text, detect_arrows
from event import Event
import tkinter as tk
from statistics import mode
import time

MAP_TOP_LEFT = (5, 28)
MAP_BOTTOM_RIGHT = (184, 190)

PLATFORM_X_RANGE = (95, 101)
PLATFORM_Y_RANGE = (123, 125)

EMPTY_INV_IMG = cv2.imread('data/empty_inv.png')
NOTICE_IMG = cv2.imread('data/notice.png')
ARR_IMG = cv2.imread('data/arr.png')


def curr_time(startTime):
    return time.time() - startTime


def click(d2Box, x, y):
    win32api.SetCursorPos((x, y))
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,
                         d2Box['left'] + x, d2Box['top'] + y, 0, 0)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,
                         d2Box['left'] + x, d2Box['top'] + y, 0, 0)


def findImagePos(window, img):
    res = cv2.matchTemplate(window, img, cv2.TM_CCOEFF_NORMED)
    loc = np.where(res >= 0.9)
    return loc


def captureAndSaveWindow(d2Box, filename):
    ss = mss()
    ss_img = np.delete(np.array(ss.grab(d2Box)), 3, axis=2)
    cv2.imwrite(filename, ss_img)

    home_events = read_events('data/home.txt')
    execute_events(home_events)
    playsound('data/home.wav')
    exit()


def captureMap(d2Box):
    ss = mss()
    ss_img = np.array(ss.grab({'top': d2Box['top'] + MAP_TOP_LEFT[1], 'left': d2Box['left'] + MAP_TOP_LEFT[0],
                               'width': MAP_BOTTOM_RIGHT[0] - MAP_TOP_LEFT[0], 'height': MAP_BOTTOM_RIGHT[1] - MAP_TOP_LEFT[1]}))
    return np.delete(ss_img, 3, axis=2)


def captureInv(d2Box):
    ss = mss()
    ss_img = np.array(ss.grab(
        {'top': d2Box['top'] + 50, 'left': d2Box['left'] + 1330, 'width': 590, 'height': 420}))
    return np.delete(ss_img, 3, axis=2)


def captureMiddle(d2Box):
    ss = mss()
    ss_img = np.array(ss.grab(
        {'top': d2Box['top'] + 300, 'left': d2Box['left'] + 600, 'width': 700, 'height': 400}))
    return np.delete(ss_img, 3, axis=2)


def captureBubble(d2Box):
    ss = mss()
    ss_img = np.array(ss.grab(
        {'top': d2Box['top'] + 850, 'left': d2Box['left'] + 1320, 'width': 300, 'height': 180}))
    return np.delete(ss_img, 3, axis=2)


def captureRune(d2Box):
    ss = mss()
    ss_img = np.array(ss.grab(
        {'top': d2Box['top'] + 100, 'left': d2Box['left'] + 620, 'width': 700, 'height': 200}))
    return np.delete(ss_img, 3, axis=2)


def isInvEmpty(d2Box):
    inv_img = captureInv(d2Box)
    loc = findImagePos(inv_img, EMPTY_INV_IMG)
    return len(loc) > 0 and len(loc[0]) > 0


def isNoticePresent(d2Box):
    inv_img = captureMiddle(d2Box)
    loc = findImagePos(inv_img, NOTICE_IMG)
    return len(loc) > 0 and len(loc[0]) > 0


def getBubbleCodes(d2Box):
    bubble_img = captureBubble(d2Box)
    text = extract_text(bubble_img)
    # '@bot' should be found in text...
    codes = extract_codes(text)
    return codes


def getD2Window():
    try:
        window = win32gui.FindWindow(None, "Haiku v213.3")
        rect = win32gui.GetWindowRect(window)
        box = {'top': rect[1], 'left': rect[0],
               'width': rect[2] - rect[0], 'height': rect[3] - rect[1]}
        return box
    except:
        print("Window not found. Exiting.")
        exit()


def isYellowPixel(pixel):
    return pixel[2] > 200 and pixel[1] > 200 and pixel[0] < 100


def isPinkPixel(pixel):
    return pixel[2] > 200 and pixel[1] < 120 and pixel[0] > 230


def isYellowXY(img, x, y):
    return x >= img.shape[0] or y >= img.shape[1] or isYellowPixel(img[x][y])


def isPinkXY(img, x, y):
    return x >= img.shape[0] or y >= img.shape[1] or isPinkPixel(img[x][y])


def isYellow9Pixels(img, x, y):
    count = 0
    for i in range(x, x+3):
        for j in range(y, y+3):
            if isYellowXY(img, i, j):
                count += 1
    return count >= 9


def isPink9Pixels(img, x, y):
    count = 0
    for i in range(x, x+3):
        for j in range(y, y+3):
            if isPinkXY(img, i, j):
                count += 1
    return count >= 9


def getYellowPos(d2Box):
    map_img = captureMap(d2Box)
    for x in range(map_img.shape[0]):
        for y in range(map_img.shape[1]):
            if isYellow9Pixels(map_img, x, y):
                return (y, x)

    print('Cannot find self on map. Exiting')
    captureAndSaveWindow(d2Box, 'error_map.png')


def getPinkPos(d2Box):
    map_img = captureMap(d2Box)
    for x in range(map_img.shape[0]):
        for y in range(map_img.shape[1]):
            if isPink9Pixels(map_img, x, y):
                return (y, x)

    print('Pink not found. Returning none.')
    return None


def moveLeftForSeconds(time):
    events = []
    events += [Event('press', 'DIK_LEFT', 0)]
    events += [Event('release', 'DIK_LEFT', time)]
    execute_events(events)


def moveRightForSeconds(time):
    events = []
    events += [Event('press', 'DIK_RIGHT', 0)]
    events += [Event('release', 'DIK_RIGHT', time)]
    execute_events(events)


def jumpUpLow():
    events = []
    events += [Event('press', 'DIK_ALTL', 0)]
    events += [Event('release', 'DIK_ALTL', 0.1)]
    events += [Event('press', 'DIK_Z', 0.45)]
    events += [Event('release', 'DIK_Z', 1)]
    execute_events(events)


def jumpUpHigh():
    events = []
    events += [Event('press', 'DIK_ALTL', 0)]
    events += [Event('release', 'DIK_ALTL', 0.1)]
    events += [Event('press', 'DIK_Z', 0.25)]
    events += [Event('release', 'DIK_Z', 1)]
    execute_events(events)


def jumpDown():
    events = []
    events += [Event('press', 'DIK_DOWN', 0)]
    events += [Event('press', 'DIK_ALTL', 0.1)]
    events += [Event('release', 'DIK_ALTL', 0.25)]
    events += [Event('release', 'DIK_DOWN', 2)]
    execute_events(events)


def centerSelf(d2Box):
    for _ in range(2):
        yellowPos = getYellowPos(d2Box)
        x, y = yellowPos
        if x < PLATFORM_X_RANGE[0]:
            moveRightForSeconds(0.06*(2+PLATFORM_X_RANGE[0] - x))
            sleep(0.5)
        elif x > PLATFORM_X_RANGE[1]:
            moveLeftForSeconds(0.06*(2+x - PLATFORM_X_RANGE[1]))
            sleep(0.5)
        else:
            break

    yellowPos = getYellowPos(d2Box)
    x, y = yellowPos
    if x < PLATFORM_X_RANGE[0] or x > PLATFORM_X_RANGE[1]:
        print('Could not center self on platform. Exiting.')
        captureAndSaveWindow(d2Box, 'error_platform.png')

    if y < PLATFORM_Y_RANGE[0]:
        print('Ended up too high. Exiting.')
        captureAndSaveWindow(d2Box, 'error_high.png')
    elif y > PLATFORM_Y_RANGE[1]:
        jumpUpLow()
        sleep(1)
        yellowPos = getYellowPos(d2Box)
        x, y = yellowPos
        if y < PLATFORM_Y_RANGE[0] or y > PLATFORM_Y_RANGE[1]:
            print('Could not jump up. Exiting.')
            captureAndSaveWindow(d2Box, 'error_jump.png')


def moveToPink(d2Box):
    pinkPos = getPinkPos(d2Box)
    if not pinkPos:
        return
    for _ in range(2):
        yellowPos = getYellowPos(d2Box)
        x, y = yellowPos
        if x < pinkPos[0] - 5:
            moveRightForSeconds(0.06*(pinkPos[0] - x))
        elif x > pinkPos[0] + 5:
            moveLeftForSeconds(0.06*(x - pinkPos[0]))

    yellowPos = getYellowPos(d2Box)
    x, y = yellowPos
    if abs(pinkPos[0] - x) > 5:
        print('Could not match pink\'s x position. Exiting.')
        captureAndSaveWindow(d2Box, 'error_pink_x.png')

    for _ in range(3):
        yellowPos = getYellowPos(d2Box)
        x, y = yellowPos
        if y < pinkPos[1]:
            jumpDown()
        elif y > pinkPos[1]:
            jumpUpHigh()
            sleep(0.5)
        else:
            break

    yellowPos = getYellowPos(d2Box)
    x, y = yellowPos
    if abs(pinkPos[1] - y) > 5:
        print('Could not match pink\'s y position. Exiting.')
        captureAndSaveWindow(d2Box, 'error_pink_y.png')
    print('Moved to pink.')
    sleep(0.5)


def getPinkCode(d2Box):
    detecteds = []
    for _ in range(5):
        rune_img = captureRune(d2Box)
        maybe_loc = findImagePos(rune_img, ARR_IMG)
        if len(maybe_loc) == 2 and len(maybe_loc[0] > 0):
            loc = (maybe_loc[0][0], maybe_loc[1][0])
            rune_img = rune_img[loc[0]+40:, loc[1]:loc[1]+400, :]
            arrows = detect_arrows(rune_img)
            if arrows is None:
                continue
            else:
                detecteds += [arrows]
        else:
            detecteds += [['none', 'none', 'none', 'none']]
    modes = []
    for i in range(4):
        try:
            modes += [mode([detecteds[j][i]
                            for j in range(5) if detecteds[j][i] != 'none'])]
        except:
            return ['none']
    return modes


def enterPinkCode(d2Box):
    moveToPink(d2Box)
    execute_events([Event('press', 'DIK_SPACE', 0.2),
                    Event('release', 'DIK_SPACE', 0.2)])
    sleep(0.5)
    code = getPinkCode(d2Box)
    if 'none' in code:
        print('Found none in keys. Ignoring.')
        execute_events([Event('press', 'DIK_SPACE', 0.2),
                        Event('release', 'DIK_SPACE', 0.2)])
        return False
    else:
        print('Attempting keys: %s' % code)

    events = []
    time_sum = 0
    for key in code:
        time_sum += 0.2
        events += [Event('press', 'DIK_%s' % key.upper(), time_sum)]
        time_sum += 0.2
        events += [Event('release', 'DIK_%s' % key.upper(), time_sum)]
    execute_events(events)
    sleep(1)


def writeCode(code_events, code):
    sum_time = 3.15
    for char in code:
        if char.isupper():
            sum_time += 0.3
            code_events += [Event('press', 'DIK_SHIFT', sum_time)]

        sum_time += 0.3
        code_events += [Event('press', 'DIK_%s' % (char.upper()), sum_time)]
        sum_time += 0.3
        code_events += [Event('release', 'DIK_%s' % (char.upper()), sum_time)]

        if char.isupper():
            sum_time += 0.3
            code_events += [Event('release', 'DIK_SHIFT', sum_time)]

    sum_time += 0.3
    code_events += [Event('press', 'DIK_ENTER', sum_time)]
    sum_time += 0.3
    code_events += [Event('release', 'DIK_ENTER', sum_time)]
    sum_time += 0.3
    code_events += [Event('press', 'DIK_ENTER', sum_time)]
    sum_time += 0.3
    code_events += [Event('release', 'DIK_ENTER', sum_time)]
    execute_events(code_events)


def flashScreen():
    root = tk.Tk()
    root.configure(bg='red')
    root.overrideredirect(True)
    root.state('zoomed')
    root.after(2000, root.destroy)  # set the flash time to 5000 milliseconds
    root.mainloop()


'''
blah blah
dd

'''


def main():
    buff_events = read_events('data/buff.txt')
    pot_events = read_events('data/pot.txt')
    mob_events = read_events('data/mob.txt')
    sell_events = read_events('data/sell.txt')
    code_events = read_events('data/code.txt')

    print('Waiting for 2 seconds.')
    sleep(2)
    print('Starting.')

    startTime = time.time()

    buff_time = -240
    pot_time = -1800
    pink_time = -900

    if len(sys.argv) > 1:
        pot_time = 0
        pink_time = 0
    for i in range(230):
        print('Beginning of iteration %d.' % (i+1))
        playsound('data/bop.wav')
        box = getD2Window()

        isPresent = isNoticePresent(box)
        if isPresent:
            print('Found text bubble.')
            # flashScreen()
            playsound('data/notice.wav')

            codes = getBubbleCodes(box)
            click(box, 960, 720)
            execute_events([Event('press', 'DIK_ENTER', 0.5),
                            Event('release', 'DIK_ENTER', 0.5)])
            for code in codes:
                print('Executing code "%s".' % (code))
                writeCode(code_events, code)

        # TODO: fix the pink retry behavior
        pinkPos = getPinkPos(box)
        if pinkPos is not None:
            print('Found pink.')
            playsound('data/pink.wav')
            for _ in range(3):
                enterPinkCode(box)
            print('Centering self.')
            centerSelf(box)
            pinkPos = getPinkPos(box)
            if pinkPos is not None:
                print('Found pink again.')
                for _ in range(3):
                    enterPinkCode(box)
                centerSelf(box)
                pinkPos = getPinkPos(box)
                if pinkPos is not None:
                    print('Found pink a third time. Exiting.')
                    captureAndSaveWindow(box, 'error_pink_third.png')
            playsound('data/pink_done.wav')
            pink_time = curr_time(startTime)

        if curr_time(startTime) - pink_time > 1000:
            print('Went too long without a pink. Exiting.')
            captureAndSaveWindow(box, 'error_pink_time.png')

        if not isInvEmpty(box):
            print('Inventory not empty. Executing sell command.')
            execute_events(sell_events)
            sleep(1)
            if not isInvEmpty(box):
                print('Inventory still not empty. Exiting.')
                captureAndSaveWindow(box, 'error_inventory.png')

        if curr_time(startTime) - buff_time > 240:
            print('Executing buffs.')
            execute_events(buff_events)
            buff_time = curr_time(startTime)
        if curr_time(startTime) - pot_time > 1800:
            print('Executing pots.')
            execute_events(pot_events)
            pot_time = curr_time(startTime)

        print('Centering self.')
        centerSelf(box)
        print('Executing mobbing.')
        execute_events(mob_events)


if __name__ == '__main__':
    main()
