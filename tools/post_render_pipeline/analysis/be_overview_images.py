#!/usr/bin/env python
# Copyright (c) 2025 Max Planck Society
# License: https://bedlam2.is.tuebingen.mpg.de/license.html
#
# Create overview images including first, middle and last image of each sequence
#
# Requirements:
#   + pillow
#

from pathlib import Path
from PIL import Image, ImageDraw
import sys

THUMBNAIL_WIDTH = 256
THUMBNAIL_HEIGHT = 144
THUMBNAILS_PER_ROW = 3
ROWS_PER_IMAGE = 10
COLUMN_LINE_WIDTH = 2
ROW_LINE_WIDTH = 6

def create_overview_images(renderjob_path, rotate):
    print(f"Creating overview images: {renderjob_path}, rotate={rotate}")

    if not rotate:
        thumbnail_width = THUMBNAIL_WIDTH
        thumbnail_height = THUMBNAIL_HEIGHT
    else:
        thumbnail_width = THUMBNAIL_HEIGHT
        thumbnail_height = THUMBNAIL_WIDTH


    target_images = []
    images_path = renderjob_path / "png"
    sequence_paths = sorted(images_path.glob("*"))
    for sequence_path in sequence_paths:
        image_paths = sorted(list(sequence_path.glob("*.png")))
        target_images.append(image_paths[0])
        target_images.append(image_paths[len(image_paths) // 2])
        target_images.append(image_paths[-1])

    montage_width = THUMBNAILS_PER_ROW * thumbnail_width
    montage_height = ROWS_PER_IMAGE * thumbnail_height
    overview_index = 0
    while len(target_images) > 0:
        montage_image = Image.new('RGB', (montage_width, montage_height), color='black')
        draw = ImageDraw.Draw(montage_image)

        for index in range(THUMBNAILS_PER_ROW * ROWS_PER_IMAGE):
            row = index // THUMBNAILS_PER_ROW
            col = index % THUMBNAILS_PER_ROW
            x_offset = col * thumbnail_width
            y_offset = row * thumbnail_height

            target_image = target_images.pop(0)

            image = Image.open(target_image)

            if rotate:
                image = image.rotate(-90, expand=True)

            image_resized = image.resize((thumbnail_width, thumbnail_height), Image.Resampling.LANCZOS)

            montage_image.paste(image_resized, (x_offset, y_offset))

            if len(target_images) == 0:
                break

        # Draw grid lines
        for row in range(ROWS_PER_IMAGE - 1):
            y = (row + 1) * thumbnail_height
            draw.line([(0, y), (montage_width, y)], fill="black", width=ROW_LINE_WIDTH)

        for col in range(THUMBNAILS_PER_ROW - 1):
            x = (col + 1) * thumbnail_width
            draw.line([(x, 0), (x, montage_height)], fill="black", width=COLUMN_LINE_WIDTH)

        # Save montage image
        output_path = renderjob_path / "overview" / "images" / f"overview_{overview_index:03d}.png"
        if not output_path.parent.exists():
            output_path.parent.mkdir(parents=True, exist_ok=True)

        print(f"  Saving: {output_path}")
        montage_image.save(output_path)

        overview_index += 1

    return


if __name__ == "__main__":
    if (len(sys.argv) < 2) or (len(sys.argv) > 3):
        print("Usage: %s RENDERJOB_FOLDER [rotate]" % (sys.argv[0]), file=sys.stderr)
        sys.exit(1)

    renderjob_path = Path(sys.argv[1])
    rotate = False
    if len(sys.argv) == 3:
        rotate = True

    create_overview_images(renderjob_path, rotate)
