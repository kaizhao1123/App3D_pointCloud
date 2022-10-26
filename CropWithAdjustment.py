import cv2
import numpy as np
import math


# get the area of the target (seed) from the side view of image : pic
def GetArea(dic, vintValue, imageNum, imageType, middle_original, imageHeight):
    if imageType == "original":
        imgname = dic + ("%04d" % imageNum) + '.bmp'
    else:
        imgname = dic + 'ROI_0{:02d}0.png'.format(imageNum - 1)

    img = cv2.imread(imgname)  # input image, used to get the height of the target
    if dic[-1] == 'd':  # captured folder
        img_new = img[0:middle_original - 10, :]  # input image, used to get the width and length of the target
    else:
        if imageType == "original":
            img_new = img[0:middle_original - 10, :]
        else:
            img_new = img

    # ####### to get the height of target ##########
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
    maxRect = cv2.boundingRect(maxCont)
    height = maxRect[3]

    # ####### to get the width and length of target ##########
    gray = cv2.cvtColor(img_new, cv2.COLOR_BGR2GRAY)  # change to gray image
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
    maxRect = cv2.boundingRect(maxCont)
    X = maxRect[0]
    Y = maxRect[1]
    width = maxRect[2]

    return X, Y, width, height


# get the expected width of the target in each images, that is the width when the seed located in the exact turn center
# find the width of the pair opposite images, then calculate the average to get the expected width(the center position)
# the largest one is the length of the target(seed), the smallest one is the width of the target(seed)
def getExpectedValues(dic, vintValue, src, middle_original, imageHeight):
    expectedWidth = []
    heights = []  # the height of all 36 images.
    imgNum = 1
    while imgNum < 19:  # the first 18 images
        X, Y, width, height = GetArea(dic, vintValue, imgNum, src, middle_original, imageHeight)
        oppoX, oppoY, oppositeWidth, oppositeHeight = GetArea(dic, vintValue, imgNum + 18, src, middle_original,
                                                              imageHeight)
        expectedWidth.append(width / 2 + oppositeWidth / 2)
        heights.append(height)
        heights.append(oppositeHeight)
        imgNum += 1
    index = 19
    while index > 1:  # the last 18 images
        expectedWidth.append(expectedWidth[19 - index])
        index -= 1

    return expectedWidth, heights


# increase or decrease the target size in the image, based on the expected width. And relocate the target on the bottom
# line of the image.
def normalizeImage(dic, vintValue, imageNum, expectedWidth, imageWidth, imageHeight, bottomY, middle_original):
    imgname = dic + ("%04d" % imageNum) + '.bmp'
    img = cv2.imread(imgname)  # read input image
    X, Y, width, height = GetArea(dic, vintValue, imageNum, "original", middle_original, imageHeight)

    # draw the black circle edge
    center = (round(X + width / 2), round(Y + height / 2))
    color = (0, 0, 0)
    thickness = 10
    img = cv2.circle(img, center, round(max(width / 2 + 10, height / 2 + 10)), color, thickness)
    ####

    firstCrop = img[Y: Y + height, X: X + width]  # get the target
    H = firstCrop.shape[0]
    W = firstCrop.shape[1]

    ratio = expectedWidth / width
    newW = math.ceil(W * ratio)
    newH = math.ceil(H * ratio)
    dim = (newW, newH)
    resized = cv2.resize(firstCrop, dim, interpolation=cv2.INTER_AREA)  # resize the target (increase or decrease)

    result = np.zeros([imageHeight, imageWidth, 3], dtype=np.uint8)
    start_Y = math.ceil((imageHeight - newH) / 2)
    start_X = math.ceil((imageWidth - newW) / 2)

    # make the new target in the bottom center of the result image
    try:
        if bottomY == 0:  # the 1st image.
            result[start_Y: start_Y + newH, start_X: start_X + newW] = resized
        else:
            result[bottomY - newH: bottomY, start_X: start_X + newW] = resized
    except:
        print("Error caused by the light!")
    # save the image
    cv2.imwrite(dic + "ROI_0{:02d}0.png".format(imageNum - 1), result)

    # X, Y, width, height = GetArea(dic, vintValue, imageNum, "roi")
    # print("image:{} x:{} y:{} width:{} height:{}".format(imageNum, X, Y, width, height))
    return start_Y + newH


def CropWithAdjustment(dic, vintValue, imageWidth, imageHeight, expectedWidth, middle_original):
    # get the stand bottomY position in the image, based on the first image.
    bottomY = normalizeImage(dic, vintValue, 1, expectedWidth[0], imageWidth, imageHeight, 0, middle_original)  # 1/0.
    imgNum = 2
    while imgNum < 37:
        normalizeImage(dic, vintValue, imgNum, expectedWidth[imgNum - 1], imageWidth, imageHeight, bottomY,
                       middle_original)
        imgNum += 1


# test new idea
##############################################################################################
def PreAdjustment(path, vintValue):
    imgNum = 1
    while imgNum < 37:
        print(imgNum)
        imgName = path + ("%04d" % imgNum) + '.bmp'
        img = cv2.imread(imgName)

        image = cv2.GaussianBlur(img, (3, 3), 0)
        edges = cv2.Canny(image, 0, 30)  # using low vint value.
        edges = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)

        # modify the edges image to remove the bottom noisy.
        gap = 20
        coverLineVal = modifyEdges(edges, gap)
        width = img.shape[1]
        height = img.shape[0]
        coverImage = np.zeros((coverLineVal, width, 3))
        edges[height - coverLineVal:height, :] = coverImage

        # combine the edges image and original image
        new_image = cv2.add(edges, img)
        cv2.imwrite(path + ("%04d" % imgNum) + '.bmp', new_image)

        # draw the black circle edge around the target.
        X, Y, width, height = GetArea(path, vintValue, imgNum, "original")
        center = (round(X + width / 2), round(Y + height / 2))
        color = (0, 0, 0)
        thickness = 5
        new_image = cv2.circle(new_image, center, round(max(width / 2 + 5, height / 2 + 5)), color, thickness)

        cv2.imwrite(path + ("%04d" % imgNum) + '.bmp', new_image)

        imgNum += 1


# remove the bottom noisy
def modifyEdges(edges, gap):

    height, width, _ = edges.shape
    temp = edges[height-gap:height, :]

    # get all point with color
    res = []
    for row in range(0, gap):
        for col in range(0, width):
            if temp[row][col][0] == 255:
                res.append((col, row))
    res = sorted(res)

    # keep the points existed in the same col, and separate them in groups.
    # such as [28, [0, 18]], where 28 is col, 0 and 18 is row.
    newRes = []
    pre = -1
    for i in range(0, len(res) - 1):
        if res[i][0] == pre:
            newRes.append(res[i])
        else:
            if res[i][0] == res[i + 1][0]:
                newRes.append(res[i])
            pre = res[i][0]
    all_values = [list[0] for list in newRes]
    unique_values = sorted(set(all_values))

    result = []
    for value in unique_values:
        this_group = []
        for list in newRes:
            if list[0] == value:
                this_group.append(list[1])
        result.append((value, this_group))

    # select the first 10 groups in the left side and right side respectively.
    leftPart = result[:10]
    rightPart = result[len(result) - 10:]

    # get the noisy level
    minValue = gap
    for item in leftPart:
        if isValid(item[1], gap):
            for ele in item[1]:
                if 15 <= ele <= minValue:
                    minValue = ele
    for item in rightPart:
        if isValid(item[1], gap):
            for ele in item[1]:
                if 15 <= ele <= minValue:
                    minValue = ele
    return gap - minValue


def isValid(list, gap):
    if list[0] < int(gap * 0.75) <= list[len(list) - 1]:
        return True
    else:
        return False

