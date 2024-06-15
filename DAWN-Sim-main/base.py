import random
import sys
sys.path.insert(1, '.')
from source import DawnSimVis

ROOT = 0


###########################################################
class Node(DawnSimVis.BaseNode):

    ###################
    def init(self):
        self.neighbors = []

    ###################
    def run(self):
        self.send(DawnSimVis.BROADCAST_ADDR, {'source': self.id, 'type': 'HeartBeat'})
        if self.id == ROOT:
            self.set_timer(5,self.cb_start)

    ###################
    def cb_start(self):
        pass

    ###################
    def on_receive(self, pck):
        if pck['type'] == 'HeartBeat':
            self.neighbors.append(pck['source'])


###########################################################
def create_network():
    # place nodes over 100x100 grids
    for x in range(10):
        for y in range(10):
            px = 50 + x*60 + random.uniform(-20,20)
            py = 50 + y*60 + random.uniform(-20,20)
            sim.add_node(Node, pos=(px,py), tx_range=75)


# setting the simulation
sim = DawnSimVis.Simulator(
    duration=100,
    timescale=1,
    visual=True,
    terrain_size=(650, 650),
    title='Flooding')

# creating network
create_network()

# start the simulation
sim.run()