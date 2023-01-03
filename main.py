from input import User_Input
from elevation import HighestElevationLocator
from nearest_ITN import IntegratedTransportNetwork
from path import ShortestPath
import time
import pandas as pd
import geopandas as gpd

def main():

    # user input and study area generation
    user_input, study_area = User_Input().input()
    print("user's location is:", user_input)
    # Plotter().show_rim(study_area)

    # generating cell values in study area
    t1 = time.time()
    dem_path = 'Material/elevation/SZ.asc'
    evacu_points = HighestElevationLocator(dem_path, study_area).highest_locator()
    print("evacuation point is:", evacu_points)
    t2 = time.time()
    print(t2-t1)

    # finding the nearest ITNs for user location and evacuation point
    itn_file_path = 'Material/itn/solent_itn.json'

    '''
    nearest_node_user_input = IntegratedTransportNetwork(itn_file_path, user_input).get_nearest_node_coords()
    print('nearest itn to user location:', nearest_node_user_input)
    nearest_node_evacu_points = []
    for evacu_point in evacu_points:  # multiple solutions may exist
        nearest_node_evacu_points += IntegratedTransportNetwork(itn_file_path, evacu_point).get_nearest_node_coords()
    print('nearest itn to evacuation points', nearest_node_evacu_points)
    '''

    nearest_node_user_input_fid = IntegratedTransportNetwork(itn_file_path, user_input).get_nearest_node_fid()
    print('nearest itn to user location:', nearest_node_user_input_fid)
    nearest_node_evacu_points_fid = []
    for evacu_point in evacu_points:  # multiple solutions may exist
        nearest_node_evacu_points_fid += IntegratedTransportNetwork(itn_file_path, evacu_point).get_nearest_node_fid()
    print('nearest itn to evacuation points', nearest_node_evacu_points_fid)



    # Task 4
    # Numbers of schemes
    user_num = len(nearest_node_user_input_fid)
    evacu_num = len(nearest_node_evacu_points_fid)
    user_id = list(range(user_num))
    evacu_id = list(range(evacu_num))

    # Build compound indexes
    index = pd.MultiIndex.from_product([user_id, evacu_id])
    path_gdf = gpd.GeoDataFrame(index=index, columns=['path_fid', 'path_geom', 'walking_time'])

    sp = ShortestPath(itn_file_path, dem_path)
    for i, user_itn_fid in enumerate(nearest_node_user_input_fid):
        for j, evacu_itn_fid in enumerate(nearest_node_evacu_points_fid):
            path = sp.find_path(user_itn_fid, evacu_itn_fid)
            path_link, path_geom, path_time = sp.path_to_linestring(path)

            path_gdf.loc[(i, j), 'path_fid'] = path_link
            path_gdf.loc[(i, j), 'path_geom'] = path_geom
            path_gdf.loc[(i, j), 'walking_time'] = path_time
    path_gdf = path_gdf.set_geometry('path_geom')
    path_gdf = path_gdf.set_crs('EPSG:27700')

    min_walking_time = min(path_gdf['walking_time'])
    # this is for final plotting, plot this!
    final_decision_path = path_gdf.loc[path_gdf['walking_time'] == min_walking_time]

    print(f'The path is {final_decision_path["path_fid"]}')
    print(f'The total walking time is {final_decision_path["walking_time"]} minutes')

    t3 = time.time()
    print(t3 - t2)


if __name__ == '__main__':
    main()

