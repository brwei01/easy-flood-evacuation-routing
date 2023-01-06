import numpy as np

from input_version_1 import UserInput
from elevation_version_1 import HighestElevationLocator
from nearest_ITN_version_1 import IntegratedTransportNetwork, GetPointCoords
from path_version_1 import ShortestPath, DataManipulation
import time
import pandas as pd
import geopandas as gpd
from map_plotting_version_1 import MapPlotting
import pickle
import rasterio


def main():
    # task 1
    # user input and study area generation
    try:
        user_input, study_area = UserInput().input()
        print("user's location is:", user_input)
        # Plotter().show_rim(study_area)

        # task 2
        # generating cell values in study area
        t1 = time.time()
        dem_path = 'Material/elevation/SZ.asc'
        evacu_helper = HighestElevationLocator(dem_path, study_area)
        evacu_points, raster_img, out_transform = evacu_helper.highest_locator()
        '''
        dem_path = 'Material/elevation/SZ.asc'
        evacu_points = HighestElevationLocator(dem_path, study_area).highest_locator()
        '''
        print("evacuation points are:", evacu_points)
        t2 = time.time()
        print(t2 - t1)

        # task 3
        # finding the nearest ITNs for user location and evacuation point
        itn_file_path = 'Material/itn/solent_itn.json'
        itn_user = IntegratedTransportNetwork(itn_file_path, user_input)
        nearest_node_user_input_fid = itn_user.get_nearest_node_fid()
        print('nearest itn to user location fids are:', nearest_node_user_input_fid)

        gpc = GetPointCoords(itn_file_path, nearest_node_user_input_fid)
        nearest_node_user_input = gpc.get_nearest_node_coords()
        print('nearest itn to user location coordinates are:', nearest_node_user_input)

        nearest_node_evacu_points_fid = set()  # 去重复
        nearest_node_evacu_points_fid = []
        for evacu_point in evacu_points:
            itn_evacu = IntegratedTransportNetwork(itn_file_path, evacu_point)
            nearest_node_evacu_points_fid += itn_evacu.get_nearest_node_fid()
        nearest_node_evacu_points_fid = list(set(nearest_node_evacu_points_fid))
        print("nearest itn to evacuation points' fids are", nearest_node_evacu_points_fid)

        gpc = GetPointCoords(itn_file_path, nearest_node_evacu_points_fid)
        nearest_node_evacu_points = gpc.get_nearest_node_coords()
        print('nearest itn to evacuation location coordinates are', nearest_node_evacu_points)

        # Task 4
        t3 = time.time()
        # Numbers of schemes
        user_num = len(nearest_node_user_input_fid)
        evacu_num = len(nearest_node_evacu_points_fid)
        user_id = list(range(user_num))
        evacu_id = list(range(evacu_num))

        # Build compound indexes
        index = pd.MultiIndex.from_product([user_id, evacu_id])
        path_gdf = gpd.GeoDataFrame(index=index, columns=['path_fid', 'path_geom', 'walking_time', 'start', 'end'])

        sp = ShortestPath(itn_file_path, dem_path)
        for i, user_itn_fid in enumerate(nearest_node_user_input_fid):
            for j, evacu_itn_fid in enumerate(nearest_node_evacu_points_fid):
                path = sp.find_path(user_itn_fid, evacu_itn_fid)
                path_link, path_geom, path_time = sp.path_to_linestring(path)
                path_gdf.loc[(i, j), 'path_fid'] = path_link
                path_gdf.loc[(i, j), 'path_geom'] = path_geom
                path_gdf.loc[(i, j), 'walking_time'] = path_time
                path_gdf.loc[(i, j), 'start'] = nearest_node_user_input[i]
                path_gdf.loc[(i, j), 'end'] = nearest_node_evacu_points[j]

        path_gdf = path_gdf.set_geometry('path_geom')
        path_gdf = path_gdf.set_crs('EPSG:27700')

        min_walking_time = min(path_gdf['walking_time'])
        # this is for final plotting, plot this!

        '''
        print(f'The path is {final_decision_path["path_fid"]}')
        print(f'The total walking time is {int(final_decision_path["walking_time"].values)} minutes')
        '''
        t4 = time.time()
        print(t4 - t3)

        # task 5
        print('After\n')

        background_path = 'Material/background/raster-50k_2724246.tif'
        final_decision_path = path_gdf.loc[path_gdf['walking_time'] == min_walking_time]
        print(f'The path is {final_decision_path["path_fid"].values}')
        print(f'The total walking time is {int(final_decision_path["walking_time"].values)} minutes')
        start_itn = final_decision_path['start'].values
        end_itn = final_decision_path['end'].values
        print(end_itn)

        mp = MapPlotting(background_path, final_decision_path, user_input, evacu_points,
                         start_itn, end_itn, raster_img, out_transform)
        mp.init_fig()
        mp.add_background()
        mp.add_points()
        mp.add_north_arrow()
        mp.add_elevation()
        mp.add_path()
        mp.show()

    except TypeError:
        pass


if __name__ == '__main__':
    main()
