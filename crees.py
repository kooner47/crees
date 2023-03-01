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

MAP_TOP_LEFT = (5, 28)
MAP_BOTTOM_RIGHT = (184, 190)

PLATFORM_X_RANGE = (95, 101)
PLATFORM_Y_RANGE = (123, 125)

EMPTY_INV_IMG = cv2.imread('data/empty_inv.png')
NOTICE_IMG = cv2.imread('data/notice.png')
ARR_IMG = cv2.imread('data/arr.png')


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


def getPinkCode(d2Box):
    detecteds = []
    for _ in range(7):
        rune_img = captureRune(d2Box)
        maybe_loc = findImagePos(rune_img, ARR_IMG)
        if len(maybe_loc) == 2 and len(maybe_loc[0] > 0):
            loc = (maybe_loc[0][0], maybe_loc[1][0])
            rune_img = rune_img[loc[0]+40:, loc[1]:loc[1]+400, :]
            detecteds += [detect_arrows(rune_img)]
        else:
            detecteds += [['none', 'none', 'none', 'none']]
    modes = []
    for i in range(4):
        modes += [mode([detecteds[j][i]
                        for j in range(7) if detecteds[j][i] != 'none'])]
    return modes


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
    exit()


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
        exit()

    if y < PLATFORM_Y_RANGE[0]:
        print('Ended up too high. Exiting.')
        captureAndSaveWindow(d2Box, 'error_high.png')
        exit()
    elif y > PLATFORM_Y_RANGE[1]:
        jumpUpLow()
        sleep(0.5)
        yellowPos = getYellowPos(d2Box)
        x, y = yellowPos
        if y < PLATFORM_Y_RANGE[0] or y > PLATFORM_Y_RANGE[1]:
            print('Could not jump up. Exiting.')
            captureAndSaveWindow(d2Box, 'error_jump.png')
            exit()


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
        exit()

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
        exit()

    exit()


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
    sleep(1)
    box = getD2Window()
    print(getPinkCode(box))
    exit()
    moveToPink(box)
    exit()

    buff_events = read_events('data/buff.txt')
    mob_events = read_events('data/mob.txt')
    sell_events = read_events('data/sell.txt')
    code_events = read_events('data/code.txt')
    home_events = read_events('data/home.txt')

    print('Waiting for 2 seconds.')
    sleep(2)
    print('Starting.')

    for _i in range(4):
        print('Outer iteration %d.' % (_i))
        box = getD2Window()

        print('Executing buffs.')
        execute_events(buff_events)
        for _j in range(12):
            print('Inner iteration %d.' % (_j))
            isPresent = isNoticePresent(box)
            if isPresent:
                print('Found text bubble.')
                # flashScreen()
                playsound('data/sound.wav')

                codes = getBubbleCodes(box)
                click(box, 960, 720)
                execute_events([Event('press', 'DIK_ENTER', 0.5),
                                Event('release', 'DIK_ENTER', 0.5)])
                for code in codes:
                    print('Executing code "%s".' % (code))
                    writeCode(code_events, code)

                    # TODO: find another way to determine test is passed and stop attempting more codes
                    '''
                    notice_img = captureMiddle(box)
                    text = extract_text(notice_img)
                    if '@bot' not in text:
                        print('Text bubble no longer found. Continuing.')
                        break
                    '''

                # TODO: verify notice is dismissed by initial enter press, find other way to determine test is passed
                '''
                notice_img = captureMiddle(box)
                text = extract_text(notice_img)
                if '@bot' in text:
                    print('Text bubble still visible. Exiting.')
                    captureAndSaveWindow(box, 'error_text_bubble.png')
                    exit()
                '''

            if not isInvEmpty(box):
                print('Inventory not empty. Executing sell command.')
                execute_events(sell_events)
                if not isInvEmpty(box):
                    print('Inventory still not empty. Exiting.')
                    captureAndSaveWindow(box, 'error_inventory.png')
                    exit()

            print('Executing mobbing.')
            # TODO: add click on screen here, increase movement within mob.txt to test whether empty attacking still occurs
            execute_events(mob_events)


if __name__ == '__main__':
    main()
