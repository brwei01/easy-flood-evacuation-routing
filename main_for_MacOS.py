from input_version_1 import UserInput
from elevation_version_1 import HighestElevationLocator
from nearest_ITN_version_1 import IntegratedTransportNetwork, GetPointCoords
from path_version_1 import ShortestPath, DataManipulation
import pandas as pd
import geopandas as gpd
from map_plotting_for_MacOS import MapPlotting


def main():
    try:
        # TASK 1 & 6
        # user input and study area generation
        user_input, study_area = UserInput().input()
        print("user's location is:", user_input)

        # TASK 2
        # getting the coordinates of point with the highest elevation values from raster cells.
        dem_path = 'Material/elevation/SZ.asc'
        evacu_helper = HighestElevationLocator(dem_path, study_area)
        # getting a list of possible evacuation points, 2-dimensional elevation matrix,
        # and Affine coordinates transformation matrix
        evacu_points, raster_img, out_transform = evacu_helper.highest_locator()
        print("possible evacuation points include:", evacu_points)

        # TASK 3
        # finding the fids and coordinates of the nearest ITN nodes for user location and evacuation point
        # defining file path
        itn_file_path = 'Material/itn/solent_itn.json'

        # for user input point
        # getting the fids of nearest itn nodes for user input point
        itn_user = IntegratedTransportNetwork(itn_file_path, user_input)
        nearest_node_user_input_fid = itn_user.get_nearest_node_fid()
        print('fids of nearest itn nodes to user location are:', nearest_node_user_input_fid)

        gpc = GetPointCoords(itn_file_path, nearest_node_user_input_fid)
        nearest_node_user_input = gpc.get_nearest_node_coords()
        print('coordinates of nearest itn nodes to user location are:', nearest_node_user_input)

        # for possible evacuation points (points with the highest elevations within study area)
        # getting the fids of nearest itn nodes for the possible evacuation points
        nearest_node_evacu_points_fid = []
        for evacu_point in evacu_points:
            itn_evacu = IntegratedTransportNetwork(itn_file_path, evacu_point)
            nearest_node_evacu_points_fid += itn_evacu.get_nearest_node_fid()
        nearest_node_evacu_points_fid = list(set(nearest_node_evacu_points_fid))
        print("nearest itn to evacuation points' fids are", nearest_node_evacu_points_fid)
        # getting the coordinates from fid
        gpc = GetPointCoords(itn_file_path, nearest_node_evacu_points_fid)
        nearest_node_evacu_points = gpc.get_nearest_node_coords()
        print('nearest itn to evacuation location coordinates are', nearest_node_evacu_points)

        # Task 4
        # Numbers of schemes
        user_num = len(nearest_node_user_input_fid)
        evacu_num = len(nearest_node_evacu_points_fid)
        user_id = list(range(user_num))
        evacu_id = list(range(evacu_num))

        # Build compound indexes
        index = pd.MultiIndex.from_product([user_id, evacu_id])
        # building a geo-dataframe to record the possible paths information
        path_gdf = gpd.GeoDataFrame(index=index, columns=['path_fid', 'path_geom', 'walking_time', 'start',
                                                          'end', 'navigation'])
        sp = ShortestPath(itn_file_path, dem_path)
        for i, user_itn_fid in enumerate(nearest_node_user_input_fid):
            for j, evacu_itn_fid in enumerate(nearest_node_evacu_points_fid):
                path = sp.find_path(user_itn_fid, evacu_itn_fid)
                path_link, path_geom, path_time, path_names = sp.path_to_linestring(path)
                path_gdf.loc[(i, j), 'path_fid'] = path_link
                path_gdf.loc[(i, j), 'path_geom'] = path_geom
                path_gdf.loc[(i, j), 'walking_time'] = path_time
                path_gdf.loc[(i, j), 'start'] = nearest_node_user_input[i]
                path_gdf.loc[(i, j), 'end'] = nearest_node_evacu_points[j]
                path_gdf.loc[(i, j), 'navigation'] = path_names

        path_gdf = path_gdf.set_geometry('path_geom')
        path_gdf = path_gdf.set_crs('EPSG:27700')

        # comparing the walking time of the possible paths solutions stored in path_gdf geo-dataframe
        min_walking_time = min(path_gdf['walking_time'])
        # get the final decision by finding the path with minimum walking time
        final_decision_path = path_gdf.loc[path_gdf['walking_time'] == min_walking_time]
        print(f'Please follow  {final_decision_path["navigation"].values}')
        print(f'The total walking time is {int(final_decision_path["walking_time"].values)} minutes')

        # TASK 5
        # Plotting evacuation map
        background_path = 'Material/background/raster-50k_2724246.tif'
        # add start itn node onto map
        start_itn = final_decision_path['start'].values
        # add end itn node onto map
        end_itn = final_decision_path['end'].values
        # putting variables required into the map plotting class
        mp = MapPlotting(background_path, final_decision_path, user_input, evacu_points,
                         start_itn, end_itn, raster_img, out_transform)
        # adding features onto canvas
        mp.init_fig()
        mp.add_background()
        mp.add_start_points()
        mp.add_end_points()
        mp.add_user_points()
        mp.add_evacu_points()
        mp.add_north_arrow()
        mp.add_elevation()
        mp.add_path()
        mp.show()

    except TypeError:
        pass


if __name__ == '__main__':
    main()
