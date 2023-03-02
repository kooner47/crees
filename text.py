import cv2
import pytesseract
import numpy as np


def add_rounded_freqs(freqs, img):
    for row in range(img.shape[0]):
        for col in range(img.shape[1]):
            pixel = img[row][col]
            rounded_pixel = (pixel[0] // 20 * 20,
                             pixel[1] // 20 * 20, pixel[2] // 20 * 20)
            if rounded_pixel not in freqs:
                freqs[rounded_pixel] = 0
            freqs[rounded_pixel] += 1


def extract_arrows(img):
    col_dim = img.shape[1] // 4-5
    bg_color_freq = {}
    above = img[:5, :, :]
    below = img[-5:, :, :]
    add_rounded_freqs(bg_color_freq, above)
    add_rounded_freqs(bg_color_freq, below)
    for quad in range(4):
        arrow = img[5:-5, quad*col_dim+5:(quad+1)*col_dim-5, :]
        before = img[5:-5, quad*col_dim:quad*col_dim+5, :]
        after = img[5:-5, (quad+1)*col_dim-5:(quad+1)*col_dim, :]
        add_rounded_freqs(bg_color_freq, before)
        add_rounded_freqs(bg_color_freq, after)

    arrows = []
    for quad in range(4):
        arrow = img[5:-5, quad*col_dim+5:(quad+1)*col_dim-5, :]
        for row in range(arrow.shape[0]):
            for col in range(arrow.shape[1]):
                pixel = arrow[row][col]
                rounded_pixel = (pixel[0] // 20 * 20,
                                 pixel[1] // 20 * 20, pixel[2] // 20 * 20)
                if rounded_pixel in bg_color_freq:
                    arrow[row][col] = [0, 0, 0]
                else:
                    arrow[row][col] = [255, 255, 255]
        arrows += [arrow]

    return arrows


def lotsOfNeighbors(img, x, y):
    whiteCount = 0
    for row in range(x-2, x+2):
        for col in range(y-2, y+2):
            if isWhiteXY(img, row, col):
                whiteCount += 1

    for row in range(x-2, x+2):
        for col in range(y-2, y+2):
            if isWhiteXY(img, row, col):
                whiteCount += 1

    return whiteCount >= 14


def someNeighbors(img, x, y):
    whiteCount = 0
    for row in range(x-2, x+2):
        for col in range(y-2, y+2):
            if isWhiteXY(img, row, col):
                whiteCount += 1

    for row in range(x-2, x+2):
        for col in range(y-2, y+2):
            if isWhiteXY(img, row, col):
                whiteCount += 1

    return whiteCount >= 10


def isWhiteXY(img, x, y):
    if x < 0 or x >= img.shape[0] or y < 0 or y >= img.shape[1]:
        return False
    pixel = img[x][y]
    return pixel[0] == 255 and pixel[1] == 255 and pixel[2] == 255


def detect_arrow(img):
    x_dim = img.shape[0] // 2
    y_dim = img.shape[1] // 2

    cutoffPointTop = None
    numPopularsFound = 0
    for x in range(x_dim*2):
        for y in range(y_dim-2, y_dim+3):
            if lotsOfNeighbors(img, x, y):
                numPopularsFound += 1
                if numPopularsFound >= 3:
                    cutoffPointTop = x
                    break
        if cutoffPointTop is not None:
            break
    if cutoffPointTop is None:
        numPopularsFound = 0
        for x in range(x_dim*2):
            for y in range(y_dim-6, y_dim+7):
                if someNeighbors(img, x, y):
                    numPopularsFound += 1
                    if numPopularsFound >= 3:
                        cutoffPointTop = x
                        break
            if cutoffPointTop is not None:
                break
        if cutoffPointTop is None:
            print('Failed to detect cutoff point top. Returning None')
            return None

    cutoffPointBot = None
    numPopularsFound = 0
    for x in range(img.shape[0] - 1, img.shape[0] - 1 - 2*x_dim, -1):
        for y in range(y_dim-2, y_dim+3):
            if lotsOfNeighbors(img, x, y):
                numPopularsFound += 1
                if numPopularsFound >= 3:
                    cutoffPointBot = x
                    break
        if cutoffPointBot is not None:
            break
    if cutoffPointBot == None:
        numPopularsFound = 0
        for x in range(img.shape[0] - 1, img.shape[0] - 1 - 2*x_dim, -1):
            for y in range(y_dim-6, y_dim+7):
                if someNeighbors(img, x, y):
                    numPopularsFound += 1
                    if numPopularsFound >= 3:
                        cutoffPointBot = x
                        break
            if cutoffPointBot is not None:
                break
        if cutoffPointBot is None:
            print('Failed to detect cutoff point bot. Returning None')
            return None

    cutoffPointRight = None
    numPopularsFound = 0
    for y in range(img.shape[1] - 1, img.shape[1] - 1 - 2*y_dim, -1):
        for x in range(x_dim-2, x_dim+3):
            if lotsOfNeighbors(img, x, y):
                numPopularsFound += 1
                if numPopularsFound >= 3:
                    cutoffPointRight = y
                    break
        if cutoffPointRight is not None:
            break
    if cutoffPointRight is None:
        numPopularsFound = 0
        for y in range(img.shape[1] - 1, img.shape[1] - 1 - 2*y_dim, -1):
            for x in range(x_dim-6, x_dim+7):
                if someNeighbors(img, x, y):
                    numPopularsFound += 1
                    if numPopularsFound >= 3:
                        cutoffPointRight = y
                        break
            if cutoffPointRight is not None:
                break
        if cutoffPointRight is None:
            print('Failed to detect cutoff point right. Returning None')
            return None

    cutoffPointLeft = None
    numPopularsFound = 0
    for y in range(2*y_dim):
        for x in range(x_dim-2, x_dim+3):
            if lotsOfNeighbors(img, x, y):
                numPopularsFound += 1
                if numPopularsFound >= 3:
                    cutoffPointLeft = y
                    break
        if cutoffPointLeft is not None:
            break
    if cutoffPointLeft == None:
        numPopularsFound = 0
        for y in range(2*y_dim):
            for x in range(x_dim-6, x_dim+7):
                if someNeighbors(img, x, y):
                    numPopularsFound += 1
                    if numPopularsFound >= 3:
                        cutoffPointLeft = y
                        break
            if cutoffPointLeft is not None:
                break
        if cutoffPointLeft == None:
            print('Failed to detect cutoff point left. Returning None')
            return None

    img = img[cutoffPointTop:cutoffPointBot,
              cutoffPointLeft:cutoffPointRight, :]

    x_dim = img.shape[0]
    y_dim = img.shape[1]

    top_count = 0
    for row in range(x_dim*1//3):
        for col in range(y_dim*1//3, y_dim*2//3):
            if isWhiteXY(img, row, col):
                top_count += 1
    right_count = 0
    for row in range(x_dim*1//3, x_dim*2//3):
        for col in range(y_dim*2//3, y_dim):
            if isWhiteXY(img, row, col):
                right_count += 1
    bot_count = 0
    for row in range(x_dim*2//3, x_dim):
        for col in range(y_dim*1//3, y_dim*2//3):
            if isWhiteXY(img, row, col):
                bot_count += 1
    left_count = 0
    for row in range(x_dim*1//3, x_dim*2//3):
        for col in range(y_dim*1//3):
            if isWhiteXY(img, row, col):
                left_count += 1

    max_count = max([top_count, right_count, bot_count, left_count])
    if top_count == max_count:
        return 'up'
    elif right_count == max_count:
        return 'right'
    elif bot_count == max_count:
        return 'down'
    elif left_count == max_count:
        return 'left'
    else:
        return None


def detect_arrows(img):
    arrows = extract_arrows(img)
    keys = []
    for arrow in arrows:
        key = detect_arrow(arrow)
        if key is None:
            return None
        keys += [key]
    return keys


def extract_text(img):
    # Mention the installed location of Tesseract-OCR in your system
    pytesseract.pytesseract.tesseract_cmd = 'C:\Program Files\Tesseract-OCR\\tesseract.exe'

    # Preprocessing the image starts

    # Convert the image to gray scale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Performing OTSU threshold
    ret, thresh1 = cv2.threshold(
        gray, 0, 255, cv2.THRESH_OTSU | cv2.THRESH_BINARY_INV)

    # Specify structure shape and kernel size.
    # Kernel size increases or decreases the area
    # of the rectangle to be detected.
    # A smaller value like (10, 10) will detect
    # each word instead of a sentence.
    rect_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (18, 18))

    # Applying dilation on the threshold image
    dilation = cv2.dilate(thresh1, rect_kernel, iterations=1)

    # Finding contours
    contours, hierarchy = cv2.findContours(dilation, cv2.RETR_EXTERNAL,
                                           cv2.CHAIN_APPROX_NONE)

    # Creating a copy of image
    im2 = gray.copy()

    output_text = ''

    # Looping through the identified contours
    # Then rectangular part is cropped and passed on
    # to pytesseract for extracting text from it
    # Extracted text is then written into the text file
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)

        # Drawing a rectangle on copied image
        rect = cv2.rectangle(im2, (x, y), (x + w, y + h), (0, 255, 0), 2)

        # Cropping the text block for giving input to OCR
        cropped = im2[y:y + h, x:x + w]

        # Apply OCR on the cropped image
        text = pytesseract.image_to_string(cropped)

        # Appending the text into file
        output_text += text + '\n'

    return output_text


def extract_codes(text):
    try:
        code = text.split('@bot')[1].split('\n')[0].strip()
    except:
        print('Expected text not found. Returning empty codes.')
        return []

    os = ['o', 'O', '0']

    zeros_indexes = []
    for i in range(len(code)):
        char = code[i]
        if char in os:
            zeros_indexes += [i]

    ret = [code]
    for zero_index in zeros_indexes:
        ret2 = []
        ret_length = len(ret)
        for i in range(ret_length):
            old_code = ret[i]
            for o in os:
                code_copy = old_code[:zero_index] + o + old_code[zero_index+1:]
                ret2 += [code_copy]
        ret = ret2

    return ret


def main():
    img = cv2.imread('data/arrow7.png')
    cv2.imshow('screen', img)
    cv2.waitKey(0)
    print(detect_arrows(img))
    exit()


if __name__ == '__main__':
    main()
