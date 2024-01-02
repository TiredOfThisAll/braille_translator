from PIL import Image
import bin_module.bin as bin
import os


def binarize_images(image_path, output_path):
    for image_file in os.listdir(image_path):

        image = Image.open(os.path.join(image_path, image_file))
        image = image.convert('L')
        pixels_list = list(image.getdata())

        bin.bradley_binarization(pixels_list, image.width, image.height, 32)
        bin.anti_aliasing(pixels_list, image.width, image.height, 1)
        bin.bradley_binarization(pixels_list, image.width, image.height, 32)
        bin.anti_aliasing(pixels_list, image.width, image.height, 1)

        result = Image.new("L", image.size)
        result.putdata(pixels_list)
        result.save(os.path.join(output_path, image_file))


def binarize_image(image_path):
    image = Image.open(os.path.join(image_path))
    image = image.convert('L')
    pixels_list = list(image.getdata())

    bin.bradley_binarization(pixels_list, image.width, image.height, 32)
    bin.anti_aliasing(pixels_list, image.width, image.height, 1)
    bin.bradley_binarization(pixels_list, image.width, image.height, 32)
    bin.anti_aliasing(pixels_list, image.width, image.height, 1)

    result = Image.new("L", image.size)
    result.putdata(pixels_list)

    return result
