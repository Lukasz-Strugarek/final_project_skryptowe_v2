from mamdani_class import mamdani
from PIL import Image, ImageOps
import colorsys
import matplotlib.pyplot as plt
import numpy as np
from skimage import measure
import os

mamfis = mamdani(0.3)
mamfis.addVariable("saturation", "triangle", 0.25, 0.5, 0.6)
mamfis.addVariable("hue", "triangle", 0.25, 0.5, 0.75)
mamfis.addVariable("value", "triangle", 0.25, 0.5, 0.75)
# mamfis.addVariable("entropy", "triangle", 0.25, 0.5, 0.75)
# mamfis.addVariable("saturation", "gaussian", 0.5, 0.1)
# mamfis.addVariable("hue", "gaussian", 0.5, 0.1)
# mamfis.addVariable("value", "gaussian", 0.5, 0.1)
mamfis.addRule("IF hue IS low AND saturation IS low AND value IS high THEN notCell")
mamfis.addRule("IF saturation IS high OR saturation IS medium THEN cell")
mamfis.addRule("IF ( hue IS low OR hue IS high ) AND value IS medium THEN cell")


# mamfis.addRule("IF saturation IS medium AND hue IS medium THEN cell")

def modify_pixel_hsv(hsv_pixel):

    h, s, v = hsv_pixel
    modified_s = s
    return h, modified_s, v

def rgb_to_hsv(rgb):
    r, g, b = [x / 255.0 for x in rgb]
    h, s, v = colorsys.rgb_to_hsv(r, g, b)
    return h, s, v

def calculate_entropy(image, x, y, radius):
    image_array = np.array(image)

    # Extract the region around the given pixel within the specified radius
    x_min = max(0, x - radius)
    x_max = min(image_array.shape[0] - 1, x + radius)
    y_min = max(0, y - radius)
    y_max = min(image_array.shape[1] - 1, y + radius)

    region = image_array[x_min:x_max + 1, y_min:y_max + 1]

    # Calculate the mean color value of the central pixel
    central_pixel_color = image_array[x, y]

    # Calculate the mean color difference between the central pixel and its neighbors
    color_differences = np.mean(np.abs(region - central_pixel_color), axis=(0, 1))

    return color_differences

def modify_image(input_path):
    cell_pixels = []

    flag = False
    i = 0
    img = Image.open(input_path)

    img2 = ImageOps.exif_transpose(img.convert('RGB'))

    modified_img = Image.new("RGB", img2.size)

    a = 0

    for y in range(img.size[1]):
        for x in range(img.size[0]):
            rgb_pixel = img.getpixel((x, y))
            if(len(rgb_pixel) == 4):
                flag = True
                a = rgb_pixel[0]
                rgb_pixel.remove(rgb_pixel[0])


            hsv_pixel = rgb_to_hsv(rgb_pixel)

            modified_hsv_pixel = modify_pixel_hsv(hsv_pixel)
            h, s, v = modified_hsv_pixel

            # checking certain pixel HSV

            # if(x == 164 and y == 330):
            #     print(h, s, v)
            # if(x == 432 and y == 525):
            #     print(h, s, v)
            # r, g, b = calculate_entropy(img, x, y, 1)
            # mean = ((r+g+b)/3.0)/255.0

            mamfis.calculateAll([("hue", h), ("saturation", s), ("value", v)])
            mamfis.computeRules()
            if(mamfis.getResult() == 'cell'):
                i = i + 1
                modified_rgb_pixel = (255, 0, 0)
            elif(mamfis.getResult() == 'notCell'):
                modified_rgb_pixel = colorsys.hsv_to_rgb(*modified_hsv_pixel)
                modified_rgb_pixel = tuple(int(x * 255) for x in modified_rgb_pixel)

            modified_img.putpixel((x, y), modified_rgb_pixel)
            cell_pixels.append((x, y))
    print(i)

    plt.imshow(modified_img)
    plt.title('modified')
    plt.axis('off')
    plt.show()
    return cell_pixels




def group_pixels_by_cell(filepath):

    img = Image.open(filepath)
    cell_pixels = modify_image(filepath)

    # Convert cell_pixels to a binary image
    img_shape = (img.size[1], img.size[0])  # Height x Width
    binary_img = np.zeros(img_shape, dtype=np.uint8)
    for x, y in cell_pixels:
        binary_img[y, x] = 255  # Set pixel to white (255) for cell pixels

    # Find contours of connected components
    contours = measure.find_contours(binary_img, 0.5)

    # Approximate contours to polygons
    cell_polygons = []
    for contour in contours:
        contour = np.flip(contour, axis=1)  # Convert (row, col) to (x, y) format
        print(contours)

    return cell_polygons