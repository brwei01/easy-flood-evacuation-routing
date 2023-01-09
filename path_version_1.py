import rasterio
import networkx as nx
import json
from shapely.geometry import Point, LineString, MultiLineString


class DataManipulation(object):

    def __init__(self, itn_file_path, dem_path):

        self.itn_file_path = itn_file_path
        self.dem_path = dem_path
        # cwd = os.getcwd()
        # self.itn_output_path = os.path.join(cwd, 'Material', 'outputs', 'modified_itnlink.json')
        with open(itn_file_path, 'r') as f:
            itn_data = json.load(f)
        self.itn_nodes = itn_data['roadnodes']
        self.itn_links = itn_data['roadlinks']


    def add_keys_to_itnlink_vertices(self):
        # adding colums: start_coords, end_coords, elev_diff, walking_time to itn_links
        # which are necessary for weight calculation of graph edges

        # find the start and end nodes of each edge
        for link_fid, details in self.itn_links.items():
            details['start_coords'] = self.itn_nodes[details['start']]['coords']
            details['end_coords'] = self.itn_nodes[details['end']]['coords']

        # read elevation_data
        with rasterio.open(self.dem_path) as src:
            elev_data = src.read(1)
        # enumerate key-value pairs in itn_links
        for link, details in self.itn_links.items():
            # turn start, end point coordinates to shapely.Point
            start_coords = Point(details['start_coords'][0], details['start_coords'][1])
            end_coords = Point(details['end_coords'][0], details['end_coords'][1])
            # Query cell indexes based on coordinates
            start_row_idx, start_col_idx = src.index(start_coords.x, start_coords.y)
            end_row_idx, end_col_idx = src.index(end_coords.x, end_coords.y)
            # get elevation data at the cells being queried
            elev_start = elev_data[start_row_idx, start_col_idx]
            elev_end = elev_data[end_row_idx, end_col_idx]
            # Calculates the height difference between the start and end nodes
            # add elevational differences to data
            details['elev_diff'] = elev_end - elev_start

        speed_in_mins = 5000 / 60
        for link_fid, details in self.itn_links.items():
            distance = details['length']
            # cal weight of edges
            # cal H_time
            total_time = distance / speed_in_mins
            # cal V_time
            if details['elev_diff'] > 0:
                additional_time = details['elev_diff'] / 10
                # total_time = H_time + V_time
                total_time += additional_time
            details['walking_time'] = total_time
        # update self.itn_links data
        return self.itn_links

    def graph_gen(self):
        # generate graph
        updated_itn_links = self.add_keys_to_itnlink_vertices()
        # First, build an empty graph
        graph = nx.Graph()
        # add edge to graph
        for link_fid, details in updated_itn_links.items():
            graph.add_edge(details['start'], details['end'], fid=link_fid, weight=details['walking_time'])
        return graph


class ShortestPath(object):
    def __init__(self, itn_file_path, dem_path):
        self.updated_itn_file_path = itn_file_path
        self.dem_path = dem_path

        with open(itn_file_path, 'r') as f:
            itn_data = json.load(f)
        self.itn_nodes = itn_data['roadnodes']
        self.itn_links = itn_data['roadlinks']
        self.road = itn_data['road']

        dm = DataManipulation(itn_file_path, dem_path)
        # Generate graphs with DataManipulation

        self.graph = dm.graph_gen()

    # find shorest path between user_itn_fid and evacu_itn_fid
    def find_path(self, user_itn_fid, evacu_itn_fid):
        # finding the shorest path by dijkstra:
        path = nx.dijkstra_path(self.graph, source=user_itn_fid, target=evacu_itn_fid, weight='weight')
        # time = nx.dijkstra_path_length(graph, source=user_itn_fid, target=evacu_itn_fid, weight='weight')
        return path

    # turn path to shapely.Linestring
    def path_to_linestring(self, path):
        links = []
        geom = []
        time = 0
        first_node = path[0]

        # set up a str to store the road names on path.
        path_names = ''
        last_road = None
        counter = 1
        for node in path[1:]:
            link_fid = self.graph.edges[first_node, node]['fid']

            # get the road name that contains the individual path links
            for road_fid, road_details in self.road.items():
                # check if the link_fid is in the road links
                if link_fid in road_details['links']:
                    current_road = road_details['roadName']
                    # if the current link is contained in the same road as the last, then not adding it
                    if current_road != last_road:
                        last_road = current_road
                        path_names += current_road + ", "

            links.append(link_fid)
            time += self.graph.edges[first_node, node]['weight']
            geom.append(LineString(self.itn_links[link_fid]['coords']))
            first_node = node
            counter += 1

        geom = MultiLineString(geom)

        return links, geom, time, path_names





