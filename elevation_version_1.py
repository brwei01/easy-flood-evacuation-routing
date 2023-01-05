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
            out_image, out_transform = mask(src, geoms, crop=True)
        return out_image, out_transform

    def highest_locator(self):

        out_image, out_transform = self.masking()
        max_elev = out_image.max()
        evacu_cell_idx = np.where(out_image == max_elev)

        # multiple solutions may be returned from the last line
        evacu_points = []
        for idx in evacu_cell_idx:
            row, col = idx[1], idx[0]
            evacu_points.append([row, col] * out_transform)

        print(f'the max elevation is: {max_elev}')
        return evacu_points

