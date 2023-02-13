import cv2
import pytesseract


def extract_text(img):
    # Mention the installed location of Tesseract-OCR in your system
    pytesseract.pytesseract.tesseract_cmd = 'C:\Program Files\Tesseract-OCR\\tesseract.exe'

    # Preprocessing the image starts

    # Convert the red text to blue
    for x in range(img.shape[0]):
        for y in range(img.shape[1]):
            pixel = img[x][y]
            if pixel[0] < 20 and pixel[1] < 20 and pixel[2] > 240:
                img[x][y][0] = 255
                img[x][y][1] = 0
                img[x][y][2] = 0

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
    im2 = img.copy()

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
        code = text.split('@bot')[1].strip()
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
    img = cv2.imread('data/test.png')
    text = extract_text(img)
    print(text)
    codes = extract_codes(text)
    print(codes)
    exit()


if __name__ == '__main__':
    main()
