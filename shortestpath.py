import geopandas as gpd
import pandas as pd
from shapely import wkt
from shapely.geometry import Point,LineString
import networkx as nx
import json
import rasterio


class ShortestPath(object):

    def __init__(self, itn_file_path, dem_path):

        self.itn_file_path = itn_file_path
        self.dem = rasterio.open(dem_path)
        self.read_dem = self.dem.read(1)
        # self.user_itn_fid = user_itn_fid
        # self.evacu_itn_fid = evacu_itn_fid
        
        with open(itn_file_path, 'r') as f:
            itn_data = json.load(f)

        self.itn_nodes = itn_data['roadnodes']
        self.itn_links = itn_data['roadlinks']
        
        self.gdf_itn_nodes = gpd.GeoDataFrame(self.itn_nodes).T
        self.gdf_itn_links = gpd.GeoDataFrame(self.itn_links).T
        # nodes-coordinates（dict）
        self.node_coors_dict = self.gdf_itn_nodes['coords'].apply(Point).to_dict()
        
    def cal_v_time(self, start_elev, end_elev):
        """Calculates the v_time, v_time of downhill path = 0
        Args:
            start_elev (float)
            end_elev (float)
        """
        elev_diff = end_elev - start_elev
        if elev_diff > 0:
            v_time = elev_diff/10
        else:
            v_time = 0
        return v_time
    
    def cal_edges_weight(self):
        """Calculates the weight of the edge"""

        # The coordinates of the start and end nodes of each edge
        self.gdf_itn_links['start_coords'] = self.gdf_itn_links['start'].map(self.node_coors_dict)
        self.gdf_itn_links['end_coords'] = self.gdf_itn_links['end'].map(self.node_coors_dict)
        
        # The height corresponding to the coordinates of the start and end nodes
        self.gdf_itn_links['start_elev'] = self.gdf_itn_links['start_coords'].apply(lambda x: self.read_point_dem(x))
        self.gdf_itn_links['end_elev'] = self.gdf_itn_links['end_coords'].apply(lambda x: self.read_point_dem(x))
        
        # Calculate the Vertical time for each edge
        self.gdf_itn_links['v_time'] = self.gdf_itn_links[['start_elev', 'end_elev']].apply(lambda x: self.cal_v_time(x['start_elev'], x['end_elev']), axis=1)
        
        # Calculate the horizontal time for each edge
        self.gdf_itn_links['h_time'] = ((self.gdf_itn_links['length']/1000)/5)*60  # minutes
            
        # time = v_time+h_time
        self.gdf_itn_links['time'] = self.gdf_itn_links['h_time'] + self.gdf_itn_links['v_time']

        return self.gdf_itn_links

    def read_point_dem(self, coords: Point):
        """Read dem according to coordinates"""
        row_index, col_index = self.dem.index(coords.x, coords.y)
        elev_point = self.read_dem[row_index, col_index]
        return elev_point
    
    def gener_graph(self):
        """Build the network"""
        self.cal_edges_weight()
        # Create an empty graph
        g = nx.Graph()
        #
        # self.gdf_itn_links['u_v'] = self.gdf_itn_links[['start','end']].apply(tuple,axis=1)
        # links  = self.gdf_itn_links[['u_v','time']].set_index('u_v')['time'].to_dict()
        
        links = self.gdf_itn_links[['start', 'end', 'time']]
        nodes = self.gdf_itn_nodes.index
        
        g.add_nodes_from(nodes)  # Add nodes to the diagram
        g.add_weighted_edges_from(links.values)  # Add edges to the diagram
        
        nx.draw(g, node_size=20)
        nx.write_gexf(g, "road_G.gexf")
        
        return g
        
    def find_nearest_route_and_time(self, user_itn_fid, evacu_itn_fid):
        """Find the shortest path between evacu_itn_fid and evacu_itn_fid, weighted by time

        Args:
            user_itn_fid (tuple): the nearest INT node to the user(Output of Task 3)
            evacu_itn_fid (tuple): the nearest INT node to the highest point(Output of Task 3)
            gener_G(bool):Generate G or input G,default:False,input G(The G of the weight has been calculated)
            
        return:
            route(LineString)
            time(float)
        """
        g = self.gener_graph()
        # g can be generated via gener_graph, but every query does not need to build a road network again"""
        g = nx.read_gexf("road_G.gexf")
        print('Whether the graph is connected: ', nx.is_connected(g))
        
        # Find the shortest path between nodes and nodes
        route = nx.shortest_path(g, user_itn_fid, evacu_itn_fid, weight='time')
        
        # The total time for the shortest path
        time_total = nx.shortest_path_length(g, user_itn_fid, evacu_itn_fid, weight='time')
        print('route:{},\n time of two nodes {} min'.format(route, time_total))
        return route, time_total
    
    def turn_route_to_linestring(self, route):
        line_list = []
        for item in route:
            coord = self.node_coors_dict[item]
            line_list.append(coord)
        line = LineString(line_list)
        return line


# --------
# itn_file_path = 'Material/itn/solent_itn.json'
# dem_path = 'Material/elevation/SZ.asc'
# # Test the nodes
# nearest_node_user_input_fid = ['osgb4000000026219230']  #The node of the test
# nearest_node_evacu_points_fid = ['osgb5000005190446083', 'osgb5000005190446083'] #The node of the test

# sp = ShortestPath(itn_file_path, dem_path)
# # Test the nodes
# # nearest_node_user_input_fid = ['osgb4000000026219230']  #The node of the test
# # nearest_node_evacu_points_fid = ['osgb5000005190446083', 'osgb5000005190446083'] #The node of the test

# # there may be multiple solutions
# # Number of schemes:
# user_num = len(nearest_node_user_input_fid)
# evacu_num = len(nearest_node_evacu_points_fid)
# N_scenarios = user_num*evacu_num
# user_id = list(range(user_num))
# evacu_id = list(range(evacu_num))
# evacu_id
# Build compound indexes
# index = pd.MultiIndex.from_product([user_id, evacu_id])
# path_gdf = gpd.GeoDataFrame(index=index,columns = ['geometry'],crs='EPSG:27700')
# # path_gdf.loc[(0,1)]

# for i,user_itn_fid in enumerate(nearest_node_user_input_fid):
#     for j,evacu_itn_fid in enumerate(nearest_node_evacu_points_fid):
#         route,_ = SP.find_nearest_route_and_time(user_itn_fid, evacu_itn_fid,gener_G = False)
#         path = SP.turn_route_to_LineString(route)
#         path_gdf.loc[(i,j),'geometry'] = path
        

# print('The path is:',path_gdf)
# ax = path_gdf["geometry"].plot(alpha=.5,figsize = (12,15))

