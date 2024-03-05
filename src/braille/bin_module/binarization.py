from PIL import Image
import time
from copy import deepcopy
from math import floor
from bin import bradley_binarization, anti_aliasing
import os


def bradley_binarization_py(pixels, width, height, bradley_param):
    w = width
    h = height
    bradley_p = bradley_param

    bradley_p = max(1, min(bradley_p, 32))

    s = w / bradley_p
    s2 = s / 2

    t = 0.15

    integral_image = deepcopy(pixels)

    summ = 0
    count = 0
    
    for x in range(w):
        summ = 0
        for y in range(h):
            index = y * w + x
            summ += pixels[index]
            if (x == 0):
                integral_image[index] = summ
            else:
                integral_image[index] = integral_image[index-1] + summ

    for x in range(w):
        for y in range(h):
            index = y * w + x

            x1 = floor(x - s2)
            x2 = floor(x + s2)
            y1 = floor(y - s2)
            y2 = floor(y + s2)

            if (x1 < 0):
                x1 = 0
            if (x2 >= w):
                x2 = w - 1
            if (y1 < 0):
                y1 = 0
            if (y2 >= h):
                y2 = h - 1
            
            count = (x2 - x1) * (y2 - y1)

            summ = integral_image[floor(y2 * w + x2)] - integral_image[floor(y1 * w + x2)] - integral_image[floor(y2 * w + x1)] + integral_image[floor(y1 * w + x1)]

            p = pixels[int(index)]

            if ((p * count) < (summ * (1.0 - t))):
                pixels[int(index)] = 0
            else:
                pixels[int(index)] = 255


def anti_aliasing_py(pixels, width, height, intensity):
    for i in range(intensity):
        for y in range(height - 1):
            for x in range(width - 1):
                p = pixels[int(y * width + x)]
                p1 = pixels[int(y * width + x - 1)]
                p2 = pixels[int(y * width + x + 1)]
                p3 = pixels[int(y * width + x - width)]
                p4 = pixels[int(y * width + x + width)]
                pixels[int(y * width + x)] = (p + p1 + p2 + p3 + p4) / 5

path = "D:\\PythonProjects\\braile\\data\\perfomance_test_images"
for file in os.listdir(path):
    img = Image.open(os.path.join(path, file)).convert("L")
    pixels = list(img.getdata())
    start_time = time.time()
    bradley_binarization_py(pixels, img.width, img.height, 32)
    anti_aliasing_py(pixels, img.width, img.height, 1)
    img.putdata(pixels)
    end_time = time.time()
    print(f"image {file} processed for {end_time - start_time} sec")
    img.show()


for file in os.listdir(path):
    img = Image.open(os.path.join(path, file)).convert("L")
    pixels = list(img.getdata())
    start_time = time.time()
    bradley_binarization(pixels, img.width, img.height, 32)
    anti_aliasing(pixels, img.width, img.height, 1)
    img.putdata(pixels)
    end_time = time.time()
    print(f"image {file} processed for {end_time - start_time} sec")
    img.show()