import numpy as np
import cv2
from PIL import Image


def HSVSegmentSeq(fnin, fnout, Hint, Sint, Vint):

    # print info
    print('** Analyzing images -- Segment images **')

    # color segment images
    NumImgs = len(fnin.number)
    for i in range(NumImgs):
        # print a point to show progress
        if i % 9 == 0:
            print(".")

        # read image(roi) from file
        img = ReadImage(fnin, i)

        # color segmentation (generate array of mask)
        mask = HSVSegment(img, Hint, Sint, Vint)    # array, not image.

        # save image(mask)
        WriteImage(mask, fnout, i)

        # pre deal with mask
        dealWithMaskImage(i, Vint, fnout)


##########################################################
# read an image (roi)
def ReadImage(fn, idx):
    imgfilename = fn.base + ("%04d" % fn.number[idx]) + fn.extension
    img = cv2.imread(imgfilename)
    return img


##########################################################
# save an image (mask) from the maskArray
def WriteImage(imgArray, fn, idx):
    imgfilename = fn.base + ("%04d" % fn.number[idx]) + fn.extension
    # img = toimage(img, (2 ** 16 - 1), 0, mode='I')  # workaround to create 16-bit .pngs
    img = Image.fromarray(imgArray)
    img.save(imgfilename)


##########################################################
#   cut off the bottom noisy of the target in the mask images
def dealWithMaskImage(imgNum, vint, fn):
    img = cv2.imread(fn.base + '0{:02d}0.png'.format(imgNum))
    vintValue = vint[0]
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  # change to gray image
    res, dst = cv2.threshold(gray, vintValue, 255, 0)  # 0,255 cv2.THRESH_OTSU
    element = cv2.getStructuringElement(cv2.MORPH_CROSS, (3, 3))  # Morphological denoising
    dst = cv2.morphologyEx(dst, cv2.MORPH_OPEN, element)  # Open operation denoising

    contours, hierarchy = cv2.findContours(dst, cv2.RETR_EXTERNAL,
                                           cv2.CHAIN_APPROX_SIMPLE)  # Contour detection function
    maxCont = 0
    for cont in contours:
        area = cv2.contourArea(cont)  # Calculate the area of the enclosing shape
        if area < 1000:  # keep the largest one, which is the target.
            continue
        maxCont = cont

    mask = np.zeros_like(img)
    cv2.drawContours(mask, [maxCont], 0, (255, 255, 255), -1)
    new_image = cv2.bitwise_and(img, mask)
    new_image = cv2.cvtColor(new_image, cv2.COLOR_BGR2GRAY)     # array, not image

    img = Image.fromarray(new_image)     # convert array to image
    img.save(fn.base + '0{:02d}0.png'.format(imgNum))


##########################################################
# perform HSV segmentation
def HSVSegment(rgb_image, Hint, Sint, Vint):
    # convert RGB image to HSV
    hsv_image = cv2.cvtColor(rgb_image, cv2.COLOR_RGB2HSV)
    sz = hsv_image.shape

    # define masks for each channel and set pixels with the respective
    # channel value in the given interval to foreground, i.e. 255
    hmask = np.zeros((sz[0], sz[1]), int)
    hmask[(hsv_image[:, :, 0] >= Hint[0]) & (hsv_image[:, :, 0] <= Hint[1])] = 255
    smask = np.zeros((sz[0], sz[1]), int)
    smask[(hsv_image[:, :, 1] >= Sint[0]) & (hsv_image[:, :, 1] <= Sint[1])] = 255
    vmask = np.zeros((sz[0], sz[1]), int)
    vmask[(hsv_image[:, :, 2] >= Vint[0]) & (hsv_image[:, :, 2] <= Vint[1])] = 255
    # combine channel masks to a single mask
    return hmask * smask * vmask
