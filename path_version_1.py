import rasterio
import networkx as nx
import json
from shapely.geometry import Point, LineString, MultiLineString

class DataManipulation(object):

    def __init__(self, itn_file_path, dem_path):

        self.itn_file_path = itn_file_path
        self.dem_path = dem_path

        with open(itn_file_path, 'r') as f:
            itn_data = json.load(f)
            self.itn_nodes = itn_data['roadnodes']
            self.itn_links = itn_data['roadlinks']

    def add_keys_to_itnlink_vertices(self):
        # adding colums: start_coords, end_coords, elev_diff, walking_time to itn_links
        # which are necessary for weight calculation of graph edges

        for link_fid, details in self.itn_links.items():
            details['start_coords'] = self.itn_nodes[details['start']]['coords']
            details['end_coords'] = self.itn_nodes[details['end']]['coords']

        with rasterio.open(self.dem_path) as src:
            elev_data = src.read(1)
            for link, details in self.itn_links.items():

                start_coords = Point([tuple([details['start_coords']])])
                start_row_idx, start_col_idx = src.index(start_coords.x, start_coords.y)
                elev_start = elev_data[start_row_idx, start_col_idx]

                end_coords = Point([tuple([details['end_coords']])])
                end_row_idx, end_col_idx = src.index(end_coords.x, end_coords.y)
                elev_end = elev_data[end_row_idx, end_col_idx]

                details['elev_diff'] = elev_end - elev_start

        speed_in_mins = 5000 / 60
        for link_fid, details in self.itn_links.items():
            distance = details['length']
            total_time = distance / speed_in_mins
            if details['elev_diff'] > 0:
                additional_time = details['elev_diff'] / 10
                total_time += additional_time
            details['walking_time'] = total_time


        return self.itn_links


    def graph_gen(self):
        '''generate graph'''
        updated_itn_links = self.add_keys_to_itnlink_vertices()
        graph = nx.Graph()
        for link_fid, details in updated_itn_links.items():
            graph.add_edge(details['start'], details['end'], fid=link_fid, weight=details['walking_time'])
        return graph


class ShortestPath(object):
    def __init__(self, itn_file_path, dem_path):
        self.itn_file_path = itn_file_path
        self.dem_path = dem_path

        with open(itn_file_path, 'r') as f:
            itn_data = json.load(f)
            self.itn_nodes = itn_data['roadnodes']
            self.itn_links = itn_data['roadlinks']

        DM = DataManipulation(self.itn_file_path, self.dem_path)
        self.graph = DM.graph_gen()

    def find_path(self, user_itn_fid, evacu_itn_fid):
        # finding the shorest path by dijkstra:
        path = nx.dijkstra_path(self.graph, source=user_itn_fid, target=evacu_itn_fid, weight='weight')
        # time = nx.dijkstra_path_length(g, source=user_itn_fid, target=evacu_itn_fid, weight='weight')
        return path

    def path_to_linestring(self, path):
        links = []
        geom = []
        time = 0
        first_node = path[0]
        for node in path[1:]:
            link_fid = self.graph.edges[first_node, node]['fid']
            links.append(link_fid)
            time += self.graph.edges[first_node, node]['weight']
            geom.append(LineString(self.itn_links[link_fid]['coords']))
            first_node = node

        geom = MultiLineString(geom)

        return links, geom, time



