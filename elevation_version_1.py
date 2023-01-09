import rasterio
from rasterio.mask import mask
from shapely.geometry import mapping
import numpy as np
import matplotlib

# https://gis.stackexchange.com/questions/260304/extract-raster-values-within-shapefile-with-pygeoprocessing-or-gdal
# gene, Nov 5, 2017
class HighestElevationLocator(object):

    def __init__(self, dem_path, study_area):
        self.dem_path = dem_path
        # After step1, using the shapefile cut from step1 directly
        self.study_area = study_area

    def masking(self):
        # extract the geometry in GeoJSON format
        geoms = [mapping(self.study_area)]
        with rasterio.open(self.dem_path, 'r') as src:
            # msk = src.read_masks(1)
            # out_image is a Numpy masked array
            # set values for cropped area as 0 (which is the default)
            out_image, out_transform = mask(src, geoms, crop=True, nodata=0, filled=True)
        return out_image, out_transform

    def highest_locator(self):

        out_image, out_transform = self.masking()
        # print(out_image.shape)
        # find the max elevation value from out_image
        max_elev = out_image[0].max()
        # get all the coordinates from max value, may be more than one max point
        evacu_cell_idx = np.where(out_image[0] == max_elev)
        evacu_cell_row_idx = evacu_cell_idx[0]
        evacu_cell_col_idx = evacu_cell_idx[1]
        # multiple solutions may be returned from the last line
        evacu_points = []
        # append all coordinates from max points
        for i in range(len(evacu_cell_row_idx)):
            row, col = evacu_cell_row_idx[i], evacu_cell_col_idx[i]
            # Convert from pixel coordinates to world coordinates, multiplying the coordinates by the matrix
            evacu_points.append([col, row] * out_transform)

        print(f'the max elevation is: {max_elev}')
        return evacu_points, out_image, out_transform

