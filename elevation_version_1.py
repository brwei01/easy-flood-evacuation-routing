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

        evacu_points = []
        out_image, out_transform = self.masking()
        max_elev = out_image.max()
        evacu_cell_idx = np.where(out_image == max_elev)
        row, col = evacu_cell_idx[1], evacu_cell_idx[0]
        evacu_point_coords = [row, col] * out_transform
        evacu_points.append(tuple(evacu_point_coords))
        print(f'the max elevation is: {max_elev}')

        return evacu_points

