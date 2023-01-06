import rasterio
import numpy as np
import geopandas as gpd
import matplotlib.pyplot as plt
from cartopy import crs
from shapely.geometry import LineString
import json
from matplotlib_scalebar.scalebar import ScaleBar
import geopandas
from shapely import geometry
from matplotlib import pyplot as plt
from rasterio.plot import show


class MapPlotting(object):

    def __init__(self, background_path, final_decision_path, user_input, evacu_points, raster_img, out_transform):
        self.background_path = background_path
        self.final_decision_path = final_decision_path
        self.user_input = user_input
        self.evacu_points = evacu_points
        self.raster_img = raster_img
        self.out_transform = out_transform
        self.start_point = 0
        self.highest_point = 0
        self.background_image = 0
        self.display_extent = 0
        self.ax = 0
        self.extent = 0

    def init_fig(self):
        fig = plt.figure(figsize=(3, 3), dpi=300)
        self.ax = fig.add_subplot(1, 1, 1, projection=crs.OSGB())

    def add_background(self):
        background = rasterio.open(self.background_path)
        back_array = background.read(1)
        bounds = background.bounds
        self.extent = [bounds.left, bounds.right, bounds.bottom, bounds.top]

        palette = np.array([value for key, value in background.colormap(1).items()])
        self.background_image = palette[back_array]
        self.display_extent = [self.user_input[0] - 10000, self.user_input[0] + 10000, self.user_input[1] - 10000,
                               self.user_input[1] + 10000]

        self.ax.imshow(self.background_image, origin='upper', extent=self.extent, zorder=0)
        return

    def add_points(self):
        '''
        这里可能还有点小问题
        明天再说
        '''
        self.start_point = geometry.Point(self.user_input[0], self.user_input[1])
        self.highest_point = geometry.Point(self.evacu_points[0][0], self.evacu_points[0][1])

        start_point = geopandas.GeoSeries([self.start_point],
                                          crs='EPSG:27700',
                                          index=['start']
                                          )

        start_point.plot(ax=self.ax, color='red', markersize=3, zorder=3, label='Start point')

        end_point = geopandas.GeoSeries([self.highest_point],
                                        crs='EPSG:27700',
                                        index=['end']
                                        )

        end_point.plot(ax=self.ax, color='blue', markersize=3, zorder=3, label='Highest point')

        return

    def add_north_arrow(self):
        x, y, arrow_length = 0.02, 0.35, 0.3
        self.ax.annotate('N', xy=(x, y), xytext=(x, y - arrow_length),
                         arrowprops=dict(facecolor='black', width=1, headwidth=4),
                         ha='center', va='center', fontsize=8,
                         xycoords=self.ax.transAxes)
        self.ax.add_artist(ScaleBar(1, box_alpha=0.5))

    def add_elevation(self):
        show(self.raster_img, ax=self.ax, zorder=1, cmap='YlGn', alpha=0.5, transform=self.out_transform)

    def add_path(self):
        self.final_decision_path.plot(ax=self.ax, edgecolor='blue', linewidth=0.5, zorder=2, label='Path')

    def show(self):
        """
        Referenced from Week 8 Practical: RTree and NetworkX
        Author: Aldo Lipani, 2022
        """
        self.ax.set_extent(self.display_extent, crs=crs.OSGB())
        plt.legend(loc='lower right', fontsize=3)
        plt.show()

