from rtree import index
import json


class IntegratedTransportNetwork:
    def __init__(self, itn_file_path, input_point: list):
        self.itn_file_path = itn_file_path
        self.input_point = input_point

        # Create dictionary to store ITN nodes data
        self.itn_nodes_dict = {}

        """
        Referenced from Week 8 Practical: RTree and NetworkX
        Author: Aldo Lipani, 2022
        """
        # Read JSON file
        with open(self.itn_file_path, 'r') as f:
            input_itn = json.load(f)

        self.road_nodes = input_itn['roadnodes']

        # Build a RTree index
        self.itn_idx = index.Index()

        # For loop for each node
        """
        Adapted from Lecture 8: Tree and Graph Representations, Slide 15
        Author: Aldo Lipani, 2022
        """
        for node_count_no, node in enumerate(self.road_nodes):
            node_id = str(node)
            node_x = float(self.road_nodes[node]['coords'][0])
            node_y = float(self.road_nodes[node]['coords'][1])

            self.itn_idx.insert(node_count_no, (node_x, node_y))
            self.itn_nodes_dict.update({node_count_no: node_id})

    def get_nearest_node_fid(self):
        # If distances are the same, may get more than one results
        nearest_node_fid = []
        x, y = self.input_point
        node = (x, y)
        node_idx_list = list(self.itn_idx.nearest(node, num_results=1))
        for i in node_idx_list:
            nearest_node_fid.append(self.itn_nodes_dict.get(i))
        return nearest_node_fid

    def get_nearest_node_coords(self):
        node_coords_list = []
        nearest_node_fid = self.get_nearest_node_fid()
        for i in nearest_node_fid:
            node_coords_list.append(self.road_nodes[i]['coords'])
        return node_coords_list
