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

    def data_extraction(self):
        with rasterio.open(self.dem_path, 'r') as src:
            no_data = src.nodata
            out_image = self.masking()[0]
            data = out_image[0]
            row, col = np.where(data != no_data)
            elev = np.extract(data != no_data, data)
        return row, col, elev

    def array_to_coords(self):
        out_image, out_transform = self.masking()
        row, col, elev = self.data_extraction()
        T1 = out_transform * Affine.translation(0.5, 0.5)
        rc2xy = lambda r, c: (c, r) * T1
        #cell2points = gpd.GeoDataFrame({'col': col, 'row': row, 'elev': elev})
        cell2points = pd.DataFrame({'col': col, 'row': row, 'elev': elev})
        cell2points['x'] = cell2points.apply(lambda row: rc2xy(row.row, row.col)[0], axis=1)
        cell2points['y'] = cell2points.apply(lambda row: rc2xy(row.row, row.col)[1], axis=1)
        return cell2points

    def highest_locator(self):
        evacu_points = []
        cell2points = self.array_to_coords()
        idx = cell2points['elev'] == cell2points['elev'].max()
        evacu_point_idx = cell2points.index[idx]
        for i in evacu_point_idx:
            evacu_points.append((cell2points['x'][i], cell2points['y'][i]))
        return evacu_points