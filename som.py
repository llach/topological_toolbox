# -*- coding: utf-8 -*-

from topological_map import TopologicalMap

import numpy as np
import random
import math
import sys


class SOM(TopologicalMap):

    def __init__(self, *args, **kwargs):

        self.name = 'SOM - Self Organizing Map'

        # init from superclass
        super(SOM, self).__init__(*args, **kwargs)

        # network parameter
        self.network_size = kwargs.get('network_size', 7)
        self.dim = kwargs.get('dim', 3)
        self.sigma = kwargs.get('sigma', 7.5)
        self.eta = kwargs.get('eta', .8)
        self.max_iterations = kwargs.get('max_iterations', 1000)

        if self.dim > 3:
            raise Exception('Maximum dimension for SOM is 3!')

    # finds a node with a given grid position
    def find_grid_node(self, grid_position):

        # grid indices can not be negative
        for z in grid_position:
            if z < 0:
                return None

        # find node with given grid position
        for node in self.nodes:
            if node.grid_position == grid_position:
                return node

        return None

    # nodes edges will be added to its topological predecessors
    def connect_grid_node(self, n):

        # nodes grid position
        gp = n.grid_position

        neigh_list = []

        # add neighbors based on networks dimensionality
        # first, collect neighbors
        if(len(gp) == 1):
            neigh_list.append(self.find_grid_node([gp[0] - 1]))

        elif (len(gp) == 2):

            neigh_list.append( self.find_grid_node([gp[0] - 1, gp[1]]))
            neigh_list.append(self.find_grid_node([gp[0], gp[1] - 1]))

        elif (len(gp) == 3):

            neigh_list.append(self.find_grid_node([gp[0] - 1, gp[1], gp[2]]))
            neigh_list.append(self.find_grid_node([gp[0], gp[1] - 1, gp[2]]))
            neigh_list.append(self.find_grid_node([gp[0], gp[1], gp[2] - 1]))

        # second, add their edges
        for node in neigh_list:
            if node is not None:
                self.add_edge(n, node)

    # wraps super.add_node for randomly initialized grids
    def add_grid_node(self, grid_position):

        # sample random 3D position, project in data space
        position = np.multiply(np.random.rand(3), random.choice(self.data))

        # create node and edges
        n = self.add_node(position, grid_position)
        self.connect_grid_node(n)

    def prepare(self):

        if self.dim > self.data_dim:
            print('DIM(SOM) <= DIM(DATA)!')
            self.dim = self.data_dim

        # construct initial map based on grid dimension
        for i in range(self.network_size):

            if self.dim > 1:
                for j in range(self.network_size):

                    if self.dim > 2:
                        for k in range(self.network_size):
                            self.add_grid_node([i, j, k])

                    else:
                        self.add_grid_node([i, j])
            else:
                self.add_grid_node([i])

    def adapt(self, node, stimulus):

        # for llm, store delta w and w
        delta_w_list = []

        # ... or let r = 0?
        radius = int(max(math.floor(self.sigma), 0))

        # find neighbors
        neighbors = node.get_grid_neighbors(radius=radius)

        # adapt weights
        for c in neighbors:
            h = math.exp( -((self.dist(c.grid_position, node.grid_position) ** 2) / (2*self.sigma**2)) )

            dw = self.eta * h * np.subtract(stimulus, c.pos)
            c.pos += dw

            delta_w_list.append((c, dw))

        return delta_w_list



    def edge_update(self, n, s):
        pass

    def node_update(self, n, stimulus):
        pass

    def train(self):

        # SOMs stop criterium
        if self.timestep > self.max_iterations:
            return

        # randomly select datapoint
        stimulus = random.choice(self.data)

        # SOM only needs winner
        n, _ = self.find_nearest(stimulus)

        # adapt winner and neighbors
        delta_w = self.adapt(n, stimulus)

        # decrease eta and sigma
        self.eta -= 0.005 * self.eta
        self.sigma -= 0.005 * self.sigma

        return delta_w, stimulus, n, None

if __name__ == '__main__':
    data = np.random.rand(200, 3)

    som = SOM(dim=2, max_iterations=10000, visualization=True)
    som.run(data)



