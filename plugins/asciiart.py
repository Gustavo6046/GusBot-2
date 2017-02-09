# -*- encoding: utf-8 -*-
import requests
import StringIO
import plugincon
import math

from PIL import Image

# Credits to https://www.hackerearth.com/practice/notes/beautiful-python-a-simple-ascii-art-generator-from-images/ for most of code.

CHARS = [' ', '.', ',', '-', ';', '*', '+', '~', '/', '‡', '$', '‼', '※', '@', '&', '#']

def scale_image(image, new_width=100):
    """Resizes an image preserving the aspect ratio.
    """
    (original_width, original_height) = image.size
    aspect_ratio = original_height/float(original_width)
    new_height = int(aspect_ratio * new_width)

    new_image = image.resize((new_width, new_height))
    return new_image

def convert_to_grayscale(image):
    return image.convert('L')

def map_pixels_to_ascii_chars(image):
    """Maps each pixel to an ascii char based on the range
    in which it lies.
    """

    pixels_in_image = list(image.getdata())
    pixels_to_chars = [CHARS[-int(math.floor(float(pixel_value) / 255 * (len(CHARS) - 1))) + (len(CHARS) - 1)] for pixel_value in pixels_in_image]

    return "".join(pixels_to_chars)

def convert_image_to_ascii(image, new_width=100):
    image = scale_image(image, new_width)
    image = convert_to_grayscale(image)

    pixels_to_chars = map_pixels_to_ascii_chars(image)
    len_pixels_to_chars = len(pixels_to_chars)

    image_ascii = [pixels_to_chars[index: index + new_width] for index in
            xrange(0, len_pixels_to_chars, new_width)]

    return "\n".join(image_ascii)

def handle_image_conversion(image_filepath):
    image = None
    try:
        image = Image.open(image_filepath)
    except Exception, e:
        print "Unable to open image file {image_filepath}.".format(image_filepath=image_filepath)
        print e
        return

    image_ascii = convert_image_to_ascii(image)
    print image_ascii

@plugincon.easy_bot_command("paa_url", True)
def ascii_art_from_url(message, raw):
    if raw:
        return

    try:
        image = Image.open(StringIO.StringIO(requests.get(message["arguments"][1]).content))

    except IndexError:
        return "Syntax: paa_url <URL>"

    return ["Result:"] + convert_image_to_ascii(image, 75).split("\n")
