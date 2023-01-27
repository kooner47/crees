import win32gui
from PIL import Image
from mss import mss
import cv2
import numpy as np
from pynput.keyboard import Key, Controller
from time import sleep

'''
sleep(5)

keyboard = Controller()

# Press and release space
keyboard.press(Key.space)
keyboard.release(Key.space)
'''
'''
bounding_box = {'top': 100, 'left': 0, 'width': 400, 'height': 300}

sct = mss()

while True:
    sct_img = sct.grab(bounding_box)
    cv2.imshow('screen', np.array(sct_img))

    if (cv2.waitKey(1) & 0xFF) == ord('q'):
        cv2.destroyAllWindows()
        break
'''

name_img = cv2.imread('name.png')
h, w = name_img.shape[:-1]


def displayRect(box):
    ss = mss()

    loc = None
    count = 0

    while True:

        ss_img = np.delete(np.array(ss.grab(box)), 3, axis=2)

        if count % 2 == 0:
            loc = findCharPos(ss_img)

        for pt in zip(*loc[::-1]):
            cv2.rectangle(ss_img, pt, (pt[0] + w, pt[1] + h), (0, 255, 0), 2)

        cv2.imshow('screen', ss_img)

        if (cv2.waitKey(1) & 0xFF) == ord('q'):
            cv2.destroyAllWindows()
            break

        count += 1


def getD2Window():
    window = win32gui.FindWindow(None, "Haiku v213.3")
    rect = win32gui.GetWindowRect(window)
    return rect


def findCharPos(ss):
    res = cv2.matchTemplate(ss, name_img, cv2.TM_CCOEFF_NORMED)
    loc = np.where(res >= 0.8)
    return loc


def main():
    rect = getD2Window()
    bounding_box = {'top': rect[1], 'left': rect[0],
                    'width': rect[2] - rect[0], 'height': rect[3] - rect[1]}

    ss = np.delete(np.array(mss().grab(bounding_box)), 3, axis=2)

    displayRect(bounding_box)


main()
