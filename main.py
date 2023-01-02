from input import User_Input
from elevation import HighestElevationLocator
from nearest_ITN import IntegratedTransportNetwork
from path import ShortestPath

def main():
    # user input and study area generation
    user_input, study_area = User_Input().input()
    print("user's location is:", user_input)
    # Plotter().show_rim(study_area)

    # generating cell values in study area
    dem_path = 'Material/elevation/SZ.asc'
    evacu_points = HighestElevationLocator(dem_path, study_area).highest_locator()
    print("evacuation point is:", evacu_points)

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


    # create graph and find the shortest paths
    # there may be multiple solutions
    shortest_path_list = []
    for user_itn_fid in nearest_node_user_input_fid:
        for evacu_itn_fid in nearest_node_evacu_points_fid:
            shortest_path_list.append(ShortestPath(itn_file_path, dem_path).find_path(user_itn_fid, evacu_itn_fid)[1])
    graph = ShortestPath(itn_file_path, dem_path).find_path(user_itn_fid, evacu_itn_fid)[0]
    print('ready for plotting')

if __name__ == '__main__':
    main()