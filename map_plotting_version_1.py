import rasterio
import numpy as np
from cartopy import crs
from matplotlib_scalebar.scalebar import ScaleBar
import geopandas
from shapely import geometry
from matplotlib import pyplot as plt
from rasterio.plot import show


class MapPlotting(object):

    def __init__(self, background_path, final_decision_path, user_input, evacu_points, start_itn, end_itn,
                 raster_img, out_transform):
        self.background_path = background_path
        self.final_decision_path = final_decision_path
        self.user_input = user_input
        self.evacu_points = evacu_points
        self.start_itn = start_itn
        self.end_itn = end_itn
        self.raster_img = raster_img
        self.out_transform = out_transform
        self.start_point = 0
        self.highest_point = 0
        self.background_image = 0
        self.display_extent = 0
        self.ax = 0
        self.extent = 0
        self.im = 0

    # initialize the fig and ax
    def init_fig(self):
        fig = plt.figure(figsize=(3, 3), dpi=300)
        self.ax = fig.add_subplot(1, 1, 1, projection=crs.OSGB())
        return

    # load the background map
    def add_background(self):
        """
        Referenced from Week 8 Practical: RTree and NetworkX
        Author: Aldo Lipani, 2022
        """
        background = rasterio.open(self.background_path)
        back_array = background.read(1)
        bounds = background.bounds
        self.extent = [bounds.left, bounds.right, bounds.bottom, bounds.top]

        palette = np.array([value for key, value in background.colormap(1).items()])
        self.background_image = palette[back_array]

        self.im = self.ax.imshow(self.background_image, origin='upper', extent=self.extent, zorder=0)

        return

    def add_evacu_points(self):
        for i, evacu_point in enumerate(self.evacu_points):
            evacu_point = geometry.Point(self.evacu_points[0][0], self.evacu_points[0][1])
            evacu_point = geopandas.GeoSeries([evacu_point], crs='EPSG:27700', index=['evacu_point'])
            evacu_point.plot(ax=self.ax, color='blue', markersize=0.5, zorder=3, label=f'Highest point {i + 1}')

    def add_user_points(self):
        user_point = geometry.Point(self.user_input[0], self.user_input[1])
        user_point = geopandas.GeoSeries([user_point], crs='EPSG:27700', index=['user_point'])
        user_point.plot(ax=self.ax, color='red', markersize=3, zorder=3, label='User location')

    def add_start_points(self):
        start_itn = geometry.Point(self.start_itn[0][0], self.start_itn[0][1])
        start_itn = geopandas.GeoSeries([start_itn], crs='EPSG:27700', index=['start_itn'])
        start_itn.plot(ax=self.ax, color='green', markersize=1.5, zorder=3, label='Start point')

    def add_end_points(self):
        end_itn = geometry.Point(self.end_itn[0][0], self.end_itn[0][1])
        end_itn = geopandas.GeoSeries([end_itn], crs='EPSG:27700', index=['end_itn'])
        end_itn.plot(ax=self.ax, color='black', markersize=1.5, zorder=3, label='End point')

    # load the north arrow
    def add_north_arrow(self):
        x, y, arrow_length = 0.02, 0.35, 0.3
        self.ax.annotate('N', xy=(x, y), xytext=(x, y - arrow_length),
                         arrowprops=dict(facecolor='black', width=1, headwidth=4),
                         ha='center', va='center', fontsize=8,
                         xycoords=self.ax.transAxes)
        self.ax.add_artist(ScaleBar(1, box_alpha=0.5))

    # load the elevation image
    def add_elevation(self):
        self.raster_img[self.raster_img == 0] = None
        show(self.raster_img, ax=self.ax, zorder=1, cmap='RdYlGn', alpha=0.7, transform=self.out_transform)

    # load the shortest image
    def add_path(self):
        self.final_decision_path.plot(ax=self.ax, edgecolor='green', linewidth=0.5, zorder=2, label='Path')

    # show the final image
    def show(self):
        xlim = [self.user_input[0] - 10000, self.user_input[0] + 10000]
        ylim = [self.user_input[1] - 10000, self.user_input[1] + 10000]
        self.ax.set_xlim(xlim)
        self.ax.set_ylim(ylim)
        # self.ax.set_extent(self.display_extent, projection=crs.OSGB())
        plt.legend(loc='lower right', fontsize=3)

        # add title
        plt.title("Flood Evacuation Planning on Isle of Wright",
                  fontdict={'fontsize': 8})
        self.im.set_cmap('RdYlGn')

        # add elevation range bar
        plt.colorbar(self.im, ax=self.ax, shrink=0.7, label='Elevation(m)')
        plt.show(block=False)

    def close(self):
        plt.close()
