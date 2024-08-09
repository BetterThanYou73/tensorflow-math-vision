import os
import random
from PIL import Image, ImageDraw, ImageFont, ImageChops, ImageOps
from concurrent.futures import ThreadPoolExecutor
import multiprocessing

# Mapping for characters
char_to_folder = {
    33 : ' ! ',
    35 : ' # ',
    36 : ' $ ',
    37 : ' % ',
    38 : ' & ',
    40 : ' ( ',
    41 : ' ) ',
    42 : ' * ',
    43 : ' + ',
    44 : ' , ',
    45 : ' - ',
    46 : ' . ',
    47 : ' / ',
    48 : ' 0 ',
    49 : ' 1 ',
    50 : ' 2 ',
    51 : ' 3 ',
    52 : ' 4 ',
    53 : ' 5 ',
    54 : ' 6 ',
    55 : ' 7 ',
    56 : ' 8 ',
    57 : ' 9 ',
    58 : ' : ',
    59 : ' ; ',
    60 : ' < ',
    61 : ' = ',
    62 : ' > ',
    63 : ' ? ',
    64 : ' @ ',
    65 : ' A ',
    66 : ' B ',
    67 : ' C ',
    68 : ' D ',
    69 : ' E ',
    70 : ' F ',
    71 : ' G ',
    72 : ' H ',
    73 : ' I ',
    74 : ' J ',
    75 : ' K ',
    76 : ' L ',
    77 : ' M ',
    78 : ' N ',
    79 : ' O ',
    80 : ' P ',
    81 : ' Q ',
    82 : ' R ',
    83 : ' S ',
    84 : ' T ',
    85 : ' U ',
    86 : ' V ',
    87 : ' W ',
    88 : ' X ',
    89 : ' Y ',
    90 : ' Z ',
    91 : ' [ ',
    93 : ' ] ',
    94 : ' ^ ',
    95 : ' _ ',
    97 : ' a ',
    98 : ' b ',
    99 : ' c ',
    100 : ' d ',
    101 : ' e ',
    102 : ' f ',
    103 : ' g ',
    104 : ' h ',
    105 : ' i ',
    106 : ' j ',
    107 : ' k ',
    108 : ' l ',
    109 : ' m ',
    110 : ' n ',
    111 : ' o ',
    112 : ' p ',
    113 : ' q ',
    114 : ' r ',
    115 : ' s ',
    116 : ' t ',
    117 : ' u ',
    118 : ' v ',
    119 : ' w ',
    120 : ' x ',
    121 : ' y ',
    122 : ' z ',
    123 : ' { ',
    124 : ' | ',
    125 : ' } ',
}

def calculate_crop_box(image, bg_color):
    bg = Image.new(image.mode, image.size, bg_color)
    diff = ImageChops.difference(image, bg)
    bbox = diff.getbbox()
    if bbox:
        padding = random.randint(10, 50)  # Add random padding to the crop box
        left = max(bbox[0] - padding, 0)
        upper = max(bbox[1] - padding, 0)
        right = min(bbox[2] + padding, image.width)
        lower = min(bbox[3] + padding, image.height)
        return (left, upper, right, lower)
    else:
        return (0, 0, image.width, image.height)

def generate_character_image(args):
    char, path, filename, font_path, font_size, fg_color, bg_color = args
    print(f"Generating image for character '{char}' with font '{font_path}'.")

    # Create a larger blank image with the specified background color
    large_image_size = (512, 512)
    image = Image.new('RGB', large_image_size, bg_color)
    draw = ImageDraw.Draw(image)

    font = ImageFont.truetype(font_path, font_size)

    # Draw the text in the center of the large image
    text_bbox = draw.textbbox((0, 0), char, font=font)
    text_width, text_height = text_bbox[2] - text_bbox[0], text_bbox[3] - text_bbox[1]
    while text_width > large_image_size[0] or text_height > large_image_size[1]:
        font_size -= 5
        font = ImageFont.truetype(font_path, font_size)
        text_bbox = draw.textbbox((0, 0), char, font=font)
        text_width, text_height = text_bbox[2] - text_bbox[0], text_bbox[3] - text_bbox[1]

    # Apply random transformations
    x = (large_image_size[0] - text_width) // 2
    y = (large_image_size[1] - text_height) // 2
    draw.text((x, y), char, font=font, fill=fg_color)

    # Apply augmentations: rotation, shear
    angle = random.uniform(-5, 5)  # Rotation angle
    image = image.rotate(angle, expand=True)

    shear = random.uniform(-0.15, 0.15)  # Shear factor
    width, height = image.size
    xshift = abs(shear) * width
    new_width = width + int(round(xshift))
    image = image.transform((new_width, height), Image.AFFINE, (1, shear, -xshift if shear > 0 else 0, 0, 1, 0), Image.BICUBIC)

    # Calculate the crop box based on the furthest non-background pixels
    crop_box = calculate_crop_box(image, bg_color)
    print(f"Crop box: {crop_box}")

    try:
        cropped_image = image.crop(crop_box)

        # Apply augmentations: zoom, stretching
        zoom_factor = random.uniform(0.8, 1.2)
        new_size = (int(cropped_image.width * zoom_factor), int(cropped_image.height * zoom_factor))
        resized_image = cropped_image.resize(new_size, Image.LANCZOS)

        resized_image = resized_image.resize((168, 168), Image.LANCZOS)

        # Determine the directory based on the ASCII code
        save_path = os.path.join(path, str(ord(char)))
        if not os.path.exists(save_path):
            os.makedirs(save_path)
            print(f"Created directory: {save_path}")

        file = os.path.join(save_path, f"synth_{filename}")
        resized_image.save(file)
    except Exception as e:
        print(f"Error saving image {filename}: {e}")

def list_ttf(dir1):
    ttf_files = []
    for filename in os.listdir(dir1):
        if filename.endswith('.ttf'):
            ttf_files.append(os.path.join(dir1, filename))
    print(f"Found font files: {ttf_files}")
    return ttf_files

def initiator(path="images/dataset/", font_dir='fonts/', characters=char_to_folder, check_existing=True, seed=420, size=2400):
    random.seed(seed)
    fonts = list_ttf(font_dir)
    args_list = []

    for char_code, char in characters.items():
        save_path = os.path.join(path, str(char_code))
        print(f'Checking dir {char_code} aka {char} at {save_path}')
        existing_files = len([name for name in os.listdir(save_path) if os.path.isfile(os.path.join(save_path, name))]) if os.path.exists(save_path) else 0
        print(f'Existing size of dir {char_code} aka {char}: {existing_files}')
        images_to_generate = size - existing_files if check_existing else size

        for _ in range(images_to_generate):
            fg_color, bg_color = (255, 255, 255), (0, 0, 0)  # White on black
            font_path = random.choice(fonts)
            font_name = os.path.splitext(os.path.basename(font_path))[0]
            filename = f'{font_name}_{char_code}_{random.randint(1, 10000)}_synth.png'
            
            args_list.append((chr(char_code), path, filename, font_path, random.randint(100, 150), fg_color, bg_color))

    # Use all available cores and threads for processing
    max_workers = multiprocessing.cpu_count()
    print(f"Using {max_workers} threads for processing.")
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        executor.map(generate_character_image, args_list)

if __name__ == "__main__":
    initiator()
