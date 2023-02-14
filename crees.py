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
from text import extract_codes, extract_text
from event import Event

MAP_TOP_LEFT = (5, 28)
MAP_BOTTOM_RIGHT = (184, 175)

EMPTY_INV_IMG = cv2.imread('data/empty_inv.png')


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


def isInvEmpty(d2Box):
    inv_img = captureInv(d2Box)
    loc = findImagePos(inv_img, EMPTY_INV_IMG)
    return len(loc) > 0 and len(loc[0]) > 0


def getD2Window():
    try:
        window = win32gui.FindWindow(None, "Haiku v213.3")
        rect = win32gui.GetWindowRect(window)
        return rect
    except:
        print("Window not found. Exiting.")
        exit()


def isYellowPixel(pixel):
    return pixel[2] > 200 and pixel[1] > 200 and pixel[0] < 50


def isYellowXY(img, x, y):
    return x > img.shape[0] or y > img.shape[1] or isYellowPixel(img[x][y])


def isYellow9Pixels(img, x, y):
    for i in range(x, x+3):
        for j in range(y, y+3):
            if not isYellowXY(img, i, j):
                return False
    return True


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
    execute_events(code_events)


'''
blah blah
dd

'''


def main():
    buff_events = read_events('data/buff.txt')
    mob_events = read_events('data/mob.txt')
    sell_events = read_events('data/sell.txt')
    code_events = read_events('data/code.txt')

    print('Waiting for 2 seconds.')
    sleep(2)
    print('Starting.')

    for _i in range(4):
        print('Outer iteration %d.' % (_i))
        rect = getD2Window()
        box = {'top': rect[1], 'left': rect[0],
               'width': rect[2] - rect[0], 'height': rect[3] - rect[1]}

        print('Executing buffs.')
        execute_events(buff_events)
        for _j in range(12):
            print('Inner iteration %d.' % (_j))
            notice_img = captureMiddle(box)
            text = extract_text(notice_img)
            if '@bot' in text:
                print('Found text bubble.')
                playsound('data/sound.wav')
                codes = extract_codes(text)
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

            # TODO: reduce mob time to 15 seconds and repeat a second time
            print('Executing mobbing.')
            # TODO: add click on screen here, increase movement within mob.txt to test whether empty attacking still occurs
            execute_events(mob_events)


if __name__ == '__main__':
    main()
