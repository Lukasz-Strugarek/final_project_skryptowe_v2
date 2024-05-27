import tifffile
import cv2 as cv
import numpy as np
import math
import click
import os
import os.path as pp
from tqdm import tqdm
from itertools import product


# @click.command()
# @click.argument("filename")
# @click.argument("output_dir")
# @click.option("--tile_size", default=128, help="Tile size")
# @click.option("--overlap", default=0.1, help="Tile overlap percantage as float")
# @click.option("--cutoff", default=0.05, help="White pixel cutoff percentage")
# @click.option(
#     "--threshold", default=245, help="Pixel value threshold to be considered white"
# )
def split_tiff(filename, output_dir, tile_size, overlap, cutoff, threshold):
    os.makedirs(output_dir, exist_ok=True)

    with tifffile.TiffFile(filename) as tif:
        fh = tif.filehandle
        for page in tif.pages:
            tile_step = tile_size * (1 - overlap)
            page_tile_size = page.tile[0]

            def convert_value_to_tile_value(x: int):
                return max(0, math.ceil((x - tile_size) / tile_step))

            def convert_tile_value_to_value(x: int):
                return 0 if x == 0 else int((x - 1) * tile_step + tile_size)

            def convert_value_to_page_tile_value(x: int):
                return x // page_tile_size

            page_cols = convert_value_to_page_tile_value(page.imagewidth)
            tile_cols = convert_value_to_tile_value(page.imagewidth)
            tile_rows = convert_value_to_tile_value(page.imagelength)

            tiles = product(range(tile_rows), range(tile_cols))
            for tile_row, tile_col in tqdm(tiles, total=tile_rows * tile_cols):
                left_x = convert_tile_value_to_value(tile_col)
                top_y = convert_tile_value_to_value(tile_row)
                right_x = min(left_x + tile_size, page.imagewidth)
                bottom_y = min(top_y + tile_size, page.imagelength)

                base_tile = np.zeros((tile_size, tile_size, 3))

                page_top_y = convert_value_to_page_tile_value(top_y)
                page_bottom_y = convert_value_to_page_tile_value(bottom_y)
                page_left_x = convert_value_to_page_tile_value(left_x)
                page_right_x = convert_value_to_page_tile_value(right_x)

                page_tiles = product(
                    range(page_left_x, page_right_x + 1),
                    range(page_top_y, page_bottom_y + 1),
                )

                for page_col, page_row in page_tiles:
                    idx = page_row * page_cols + page_col

                    _ = fh.seek(page.dataoffsets[idx])
                    data = fh.read(page.databytecounts[idx])
                    tile, _, _ = page.decode(data, idx, jpegtables=page.jpegtables)

                    top_crop = max(0, top_y - page_row * page_tile_size)
                    bottom_crop = max(0, (page_row + 1) * page_tile_size - bottom_y)
                    left_crop = max(0, left_x - page_col * page_tile_size)
                    right_crop = max(0, (page_col + 1) * page_tile_size - right_x)

                    top_offset = max(0, page_row * page_tile_size - top_y)
                    left_offset = max(0, page_col * page_tile_size - left_x)

                    base_tile[
                        top_offset : top_offset
                        + page_tile_size
                        - (top_crop + bottom_crop),
                        left_offset : left_offset
                        + page_tile_size
                        - (left_crop + right_crop),
                        :,
                    ] = tile[
                        0,
                        top_crop : page_tile_size - bottom_crop,
                        left_crop : page_tile_size - right_crop,
                        :,
                    ]

                non_white_pixels = np.sum(
                    cv.inRange(base_tile, (0, 0, 0), (threshold, threshold, threshold))
                )
                if non_white_pixels > (1 - cutoff) * tile_size * tile_size * 3:
                    cv.imwrite(
                        pp.join(output_dir, f"img_{tile_row}_{tile_col}.jpeg"),
                        cv.cvtColor(base_tile.astype(np.uint8), cv.COLOR_RGB2BGR),
                    )

