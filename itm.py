from topological_map import TopologicalMap

import numpy as np

from util.example_data import circle

class ITM(TopologicalMap):

    def __init__(self, *args, **kwargs):
        self.name = "ITM - Instantaneous Topological Map"
        super(ITM, self).__init__(*args, **kwargs)
        self.eta = kwargs.get('eta', 0.1) # map breaks if eta > 0.1 ?!
        self.r_max = kwargs.get('r_max', None)
        self.node_min = 2


    def prepare(self):
        # determine average distance between two consecutive data points
        if self.r_max is None:
            dist = 0
            for x in zip(self.data[:-1],self.data[1:]):
                dist += self.dist(x[0], x[1])
            self.r_max = 0.5*(dist/len(self.data))
            self.logger.debug("r_max: %f" %self.r_max)
        new_nodes = []
        stimulus_idxs = []
        for i in range(2):
            # add two initial nodes
            stimulus, stimulus_idx = self.data[i], i
            n = self.add_node(stimulus)
            new_nodes.append(n)
            stimulus_idxs.append(stimulus_idx)
        self.timestep += 2
        return new_nodes, stimulus_idxs

    def adapt(self, node, stimulus):
        # for llm, store delta w and w
        delta_w_list = []

        dw = self.eta * np.subtract(stimulus, node.pos)
        node.pos += dw

        delta_w_list.append((node, dw))

        return delta_w_list

    def edge_update(self, n, s):
        self.add_edge(n, s)
        dead_edges = set([])
        for c in n.neighbors:
            if np.dot(np.subtract(n.pos, s.pos), np.subtract(c.pos, s.pos)) < 0:
                dead_edges.add(n.get_edge_to_neighbor(c))

        for d in dead_edges:
            self.remove_edge(d)


        dead_nodes = set([])

        for node in self.nodes:
            if len(node.neighbors) == 0:
                dead_nodes.add(node)
        for node in dead_nodes:
            self.remove_node(node)

    def node_update(self, n, s, stimulus):

        thales = np.dot(np.subtract(n.pos, stimulus), np.subtract(s.pos, stimulus))
        dns = self.dist(stimulus, n.pos)
        new_node = None
        if  thales > 0 and dns > self.r_max:
            node = self.add_node(position=stimulus)
            self.add_edge(node, n)
            new_node = node


        if self.dist(n.pos, s.pos) < 0.5*self.r_max:
            self.remove_node(s)
        return new_node

    def train(self):

        x, x_idx = self.data[self.timestep % self.timestep-1], self.timestep % self.timestep-1
        # matching
        nearest, second = self.find_nearest(x)

        # adapt winner
        delta_w = self.adapt(nearest, x)

        # update edges
        self.edge_update(nearest, second)

        # update nodes
        new_node = self.node_update(nearest, second, x)

        return delta_w, x, nearest, second, new_node, x_idx

if __name__=='__main__':
    itm = ITM(loggerlevel='DEBUG', visualization=True)
    data, labels = circle(samples_per_class=666, numclasses=1, shift_rad=2)
    data = np.append(data, labels, axis=1)
    itm.run(data)