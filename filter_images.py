import os
import shutil
import pandas as pd

# Define your valid characters
VALID_CHARACTERS = set('0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz+-*/÷')

# Flag for using image pooling
IMAGE_POOLING = True

# Function to check if all characters in the label are valid
def is_valid_label(label, valid_characters):
    if isinstance(label, str):
        return all(char in valid_characters for char in label)
    return False

# Define base directory and subdirectories
base_dir = 'images/'

# Define directory for image pool
pool_dir = os.path.join(base_dir, 'image_pool')

# Directory for CSV files
csv_dir = os.path.join(base_dir, 'csv')

# Initialize subdirectories list
sub_dirs = []

# Gather all subdirectories from CSV filenames
for file in os.listdir(csv_dir):
    if file.endswith('.csv'):
        dir = file.split('_')[1].split('.')[0]
        sub_dirs.append(dir)

# Process each subdirectory
for sub_dir in sub_dirs:
    sub_dir_path = os.path.join(base_dir, sub_dir)
    label_file = os.path.join(csv_dir, f'labels_{sub_dir}.csv')  # Path to the labels.csv file in the subdirectory

    valid_dir = os.path.join(sub_dir_path, 'valid')
    invalid_dir = os.path.join(sub_dir_path, 'invalid')

    # Ensure valid and invalid directories exist
    os.makedirs(valid_dir, exist_ok=True)
    os.makedirs(invalid_dir, exist_ok=True)

    # Read the CSV file
    labels_df = pd.read_csv(label_file)

    # Hardcode column indices: assume first column is filename, second column is label
    filename_col = labels_df.columns[0]
    label_col = labels_df.columns[1]

    # Filter images based on the labels
    for index, row in labels_df.iterrows():
        filename = row[filename_col]
        label = row[label_col]

        # Convert label to string to handle cases where it might be a float or missing
        label = str(label) if not pd.isna(label) else ""

        # Debug statements to check the values
        print(f"Processing file: {filename}, label: {label}")

        if not filename.endswith(('.jpg', '.png')):
            continue

        # Try-except block to handle missing files
        try:
            # Debug statement to check the validity of the label
            if is_valid_label(label, VALID_CHARACTERS):
                print(f"Label is valid: {label}")
                if IMAGE_POOLING:
                    shutil.move(os.path.join(pool_dir, filename), os.path.join(valid_dir, filename))
                else:
                    shutil.move(os.path.join(sub_dir_path, filename), os.path.join(valid_dir, filename))
            else:
                print(f"Label is invalid: {label}")
                if IMAGE_POOLING:
                    shutil.move(os.path.join(pool_dir, filename), os.path.join(invalid_dir, filename))
                else:
                    shutil.move(os.path.join(sub_dir_path, filename), os.path.join(invalid_dir, filename))
        except FileNotFoundError:
            print(f"File not found: {filename}. Skipping...")

    print(f"Processed directory: {sub_dir_path}")
    print(f"Valid images moved to: {valid_dir}")
    print(f"Invalid images moved to: {invalid_dir}")
