import rasterio
from rasterio import plot as rasterplot
from rasterio.mask import mask
from shapely.geometry import mapping
from rasterio import Affine
import geopandas as gpd
import pandas as pd
from shapely.geometry import Point
import numpy as np
import os


class HighestElevationLocator(object):

    def __init__(self, dem_path, study_area):
        self.dem_path = dem_path
        self.study_area = study_area

    def masking(self):
        geoms = [mapping(self.study_area)]
        with rasterio.open(self.dem_path, 'r') as src:
            # msk = src.read_masks(1)
            out_image, out_transform = mask(src, geoms, crop=True, nodata=0, filled=True)
        return out_image, out_transform

    def highest_locator(self):

        out_image, out_transform = self.masking()
        # print(out_image.shape)
        max_elev = out_image[0].max()
        evacu_cell_idx = np.where(out_image[0] == max_elev)
        evacu_cell_row_idx = evacu_cell_idx[0]
        evacu_cell_col_idx = evacu_cell_idx[1]
        # multiple solutions may be returned from the last line
        evacu_points = []
        for i in range(len(evacu_cell_row_idx)):
            row, col = evacu_cell_row_idx[i], evacu_cell_col_idx[i]
            evacu_points.append([col, row] * out_transform)

        print(f'the max elevation is: {max_elev}')
        return evacu_points, out_image, out_transform

