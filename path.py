import rasterio
import networkx as nx
import json


class ShortestPath(object):

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
            for link, details in self.itn_links.items():
                start_coords = [tuple([details['start_coords'][0], details['start_coords'][1]])]
                elev_start = [x for x in src.sample(start_coords)]
                end_coords = [tuple([details['start_coords'][0], details['start_coords'][1]])]
                elev_end = [x for x in src.sample(start_coords)]
                details['elev_diff'] = elev_end[0] - elev_start[0]

        speed_in_mins = 5000 / 60
        for link_fid, details in self.itn_links.items():
            distance = details['length']
            total_time = distance / speed_in_mins
            if details['elev_diff'] > 0:
                additional_time = details['elev_diff'] / 10
                total_time += additional_time
            details['walking_time'] = total_time

        return self.itn_links

    def find_path(self, user_itn_fid, evacu_itn_fid):

        # update itn_links
        updated_itn_links = self.add_keys_to_itnlink_vertices()

        # graph generating:
        g = nx.Graph()
        for link_fid, details in updated_itn_links.items():
            g.add_edge(details['start'], details['end'], fid=link_fid, weight=details['walking_time'])

        # finding the shorest path by dijkstra:
        path = nx.dijkstra_path(g, source=user_itn_fid, target=evacu_itn_fid, weight='weight')

        return path



