# Image Filtering Script

This repository contains a script (`filter_images.py`) to filter and organize images based on valid characters in their labels. The script reads labels from CSV files, checks if the labels contain only valid characters, and then moves the images to valid or invalid subdirectories.

## Directory Structure

The directory structure for the images and CSV files is as follows:

![Directory Structure](image%20filter%20system%20flowchart.png)

- `CSV LABELS`: Contains CSV files with labels for training, validation, and testing datasets.
  - `labels_train.csv`
  - `labels_validation.csv`
  - `labels_test.csv`
- `IMAGE POOLING`: Contains the pool of images to be filtered.
  - `image1.jpg`
  - `image2.png`
  - `image3.png`
- `TEST`, `TRAIN`, `VALIDATION`: Directories where the images are organized after filtering.
  - `Valid`: Contains images with valid labels.
    - `img1.png`
    - `img2.png`
    - `img3.png`
  - `Invalid`: Contains images with invalid labels.
    - `img1.png`
    - `img2.png`
    - `img3.png`

## Script: `filter_images.py`

This script reads labels from CSV files, checks if the labels contain only valid characters, and moves the images to appropriate subdirectories.

### Valid Characters

The set of valid characters is defined as follows:

```python
VALID_CHARACTERS = set('0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz+-*/÷')
