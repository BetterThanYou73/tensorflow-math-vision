# Character Image Generation

This repository contains a script to generate synthetic images of characters using various fonts. The images are augmented with random transformations such as rotation, shear, and zoom.

## Requirements

Ensure you have the following packages installed:
- `Pillow`
- `concurrent.futures`
- `multiprocessing`

You can install the required packages using pip:

```sh
pip install Pillow
```

## Directory Structure

```root_directory/
├── fonts/           # Directory containing .ttf font files
├── images/
│   └── dataset/     # Directory where generated images will be saved
└── generate_images.py  # This script
```

One important thing to note is that this script stores the images in it inside a folder with it's ascii number.

For example
```
[A] => 65/
[B] => 66/
[C] => 67/
[D] => 68/
...
..
.

and so on.
```

## Character Range

This is the default character range.

```
! ,  # ,  $ ,  % ,  & ,  ( ,  ) ,  * ,  + ,  , ,  - ,  . ,  / ,  0 ,  1 ,  2 ,  3 ,  4 ,  5 ,  6 ,  7 ,  8 ,  9 ,  : ,  ; ,  < ,  = ,  > ,  ? ,  @ ,  A ,  B ,  C ,  D ,  E ,  F ,  G ,  H ,  I ,  J ,  K ,  L ,  M ,  N ,  O ,  P ,  Q ,  R ,  S ,  T ,  U ,  V ,  W ,  X ,  Y ,  Z ,  [ ,  ] ,  ^ ,  _ ,  a ,  b ,  c ,  d ,  e ,  f ,  g ,  h ,  i ,  j ,  k ,  l ,  m ,  n ,  o ,  p ,  q ,  r ,  s ,  t ,  u ,  v ,  w ,  x ,  y ,  z ,  { ,  | ,  }

```

by default the size of generation is set to 2400 images per class.