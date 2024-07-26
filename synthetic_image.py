import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
import random
import os
import csv

def random_clip_and_distort(image, fraction=0.6):
    """
    Randomly clips and distorts the given image.

    Args:
        image (numpy.ndarray): The input image to be clipped and distorted.
        fraction (float64): The input image to be clipped by this multiplier
    Returns:
        numpy.ndarray: The clipped and distorted image.
    """
    
    h, w = image.shape[:2]

    # Points for the original image
    pts1 = np.float32([[0, 0], [w, 0], [0, h]])

    # Points for the distorted image
    pts2 = np.float32([[random.randint(0, w // 4), random.randint(0, h // 4)],
                       [random.randint(3 * w // 4, w), random.randint(0, h // 4)],
                       [random.randint(0, w // 4), random.randint(3 * h // 4, h)]])

    # Calculate the transformation matrix
    matrix = cv2.getAffineTransform(pts1, pts2)

    # Apply the distortion
    distorted_image = cv2.warpAffine(image, matrix, (w, h))

    # Calculate the inverse of the transformation matrix
    inv_matrix = cv2.invertAffineTransform(matrix)

    # Calculate the clipping coordinates in the distorted image
    startx = random.randint(0, int(w * (1 - fraction)))
    starty = random.randint(0, int(h * (1 - fraction)))
    endx = startx + int(w * fraction)
    endy = starty + int(h * fraction)

    # Ensure the clipping coordinates are within the image bounds
    startx = max(0, startx)
    starty = max(0, starty)
    endx = min(w, endx)
    endy = min(h, endy)

    # Clip the distorted image
    clipped_img = distorted_image[starty:endy, startx:endx]

    # Resize back to original size
    clipped_img = cv2.resize(clipped_img, (w, h))

    return clipped_img



def generate_synth_img(text, background_image, path, filename, fonts):
    """
    Generates a synthetic image with the given text and background image.

    Args:
        text (str): The text to be drawn on the image.
        background_image (str): Path to the background image.
        path (str): Directory where the generated image will be saved.
        filename (str): Name of the generated image file.
        fonts (list): List of font file paths to randomly select from.
    """
    
    # Loading and applying clip & distortion to image
    bg = cv2.imread(background_image)
    bg = random_clip_and_distort(bg)
    bg = cv2.cvtColor(bg, cv2.COLOR_BGR2RGB)
    bg_pil = Image.fromarray(bg)
    bg_pil = bg_pil.resize((256, 256))
    
    # Randomly adjust brightness and contrast
    enhancer = ImageEnhance.Brightness(bg_pil)
    bg_pil = enhancer.enhance(random.uniform(0.95, 1.05))
    enhancer = ImageEnhance.Contrast(bg_pil)
    bg_pil = enhancer.enhance(random.uniform(1, 1.2))
    
    # Choosing font and font size
    font_path = random.choice(fonts)
    font_size = int(random.uniform(35, 60))
    font = ImageFont.truetype(font_path, font_size)
    
    # Draw text on the background
    draw = ImageDraw.Draw(bg_pil)
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width, text_height = text_bbox[2] - text_bbox[0], text_bbox[3] - text_bbox[1]
    
    # Ensure the text fits within the image dimensions
    max_attempts = 10
    for _ in range(max_attempts):
        if text_width <= bg_pil.width and text_height <= bg_pil.height:
            break
        font_size -= 2  # Decrease font size if text doesn't fit
        font = ImageFont.truetype(font_path, font_size)
        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_width, text_height = text_bbox[2] - text_bbox[0], text_bbox[3] - text_bbox[1]

    
    # Random position
    x = random.randint(0, max(0, bg_pil.width - text_width))
    y = random.randint(0, max(0, bg_pil.height - text_height))
    
    # Choosing random text color
    text_color = tuple(np.random.randint(0, 256, size=3))
    draw.text((x, y), text, font=font, fill=text_color)
    
    # Converting to numpy array
    img = np.array(bg_pil)
    
    # Add random noise
    noise = np.random.normal(0, 0.5, img.shape).astype(np.uint8)
    img = cv2.add(img, noise)
    
    if not os.path.exists(path):
        os.makedirs(path)
    
    # Saving image
    cv2.imwrite(os.path.join(path, filename), cv2.cvtColor(img, cv2.COLOR_RGB2BGR))



def list_ttf_jpg(dir1, dir2):
    """
    Lists all .ttf files in the given font directory and .jpg files in the given background image directory.

    Args:
        dir1 (str): Directory containing font files.
        dir2 (str): Directory containing background images.

    Returns:
        tuple: A tuple containing two lists - list of font file paths and list of background image paths.
    """
    
    # For ttf files
    ttf_files = []
    for filename in os.listdir(dir1):
        if filename.endswith('.ttf'):
            ttf_files.append(os.path.join(dir1, filename))
    
    # For bg images
    bg_images = []
    for filename in os.listdir(dir2):
        if filename.endswith('.jpg'):
            bg_images.append(os.path.join(dir2, filename))
    
    return (ttf_files, bg_images)



def initiator(path="images/train/synth_data", font_dir='fonts/', bg_dir='bg/', characters='0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz+-*/÷', seed=69, n=100):
    """
    Initializes the synthetic image generation process.

    Args:
        path (str, optional): Directory where the generated images will be saved. Defaults to "images/train/synth_data".
        characters (str, optional): String of characters to be used for generating text. Defaults to '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz+-*/÷'.
        seed (int, optional): Random seed for reproducibility. Defaults to 69.
        font_dir (str, optional): Directory containing font files. Defaults to 'fonts/'.
        bg_dir (str, optional): Directory containing background images. Defaults to 'bg/'.
        n (int, optional): Number of synthetic images to generate. Defaults to 1000.
    """
    # Making randomness less chaotic (for testing)
    #random.seed(seed)
    
    fonts, bg = list_ttf_jpg(font_dir, bg_dir)
    
    # For keeping track of texts contained in the image
    labels = []
    
    for i in range(n):
        text = ''.join(random.choices(characters, k=5))
        bg_img = random.choice(bg)
        save_path = path
        filename = f'{i}.png'
        generate_synth_img(text=text, background_image=bg_img, path=save_path, filename=filename, fonts=fonts)
        labels.append((filename, text))
        
    with open(os.path.join(path, 'labels.csv'), 'w', newline='') as csvfile:
        labelwriter = csv.writer(csvfile)
        labelwriter.writerow(['filename', 'label'])
        labelwriter.writerows(labels)



# Only for generating images (needs to be executed once for gathering training data)
if __name__ == "__main__":
    initiator()
