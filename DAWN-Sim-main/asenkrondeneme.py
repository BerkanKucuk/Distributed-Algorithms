import random
import sys
sys.path.insert(1, '.')
from source import DawnSimVis

SOURCE = 0

###########################################################
class Node(DawnSimVis.BaseNode):

    ###################
    def init(self):
        self.parent = None
        self.layer = float('inf')
        self.children = set()
        self.others = set()

    ###################
    def run(self):
        if self.id == SOURCE:
            self.layer = 0
            self.change_color(1, 0, 0)  # Color the source node red
            self.broadcast_layer(self.layer)

    ###################
    def on_receive(self, pck):
        msg_type = pck['type']
        sender_id = pck['sender_id']
        sender_layer = pck.get('sender_layer', None)

        if msg_type == 'layer':
            if sender_layer < self.layer:
                if self.parent is not None:
                    self.send_reject(self.parent)
                self.layer = sender_layer
                self.parent = sender_id
                self.send_ack(self.parent)
                self.broadcast_layer(self.layer + 1)
            else:
                self.send_reject(sender_id)
        
        elif msg_type == 'ack':
            self.others.discard(sender_id)
            self.children.add(sender_id)
        
        elif msg_type == 'reject':
            self.children.discard(sender_id)
            self.others.add(sender_id)
            
    ###################
    def send_ack(self, recipient_id):
        if recipient_id is not None:  #alıcı kimliği
            pck = {'type': 'ack', 'sender_id': self.id}
            self.send(recipient_id, pck)
            self.log(f'ACK sent to Node {recipient_id}.')

    ###################
    def send_reject(self, recipient_id):
        if recipient_id is not None:
            pck = {'type': 'reject', 'sender_id': self.id}
            self.send(recipient_id, pck)
            self.log(f'REJECT sent to Node {recipient_id}.')

    ###################
    def broadcast_layer(self, layer):
        pck = {'type': 'layer', 'sender_id': self.id, 'sender_layer': layer}
        self.send(DawnSimVis.BROADCAST_ADDR, pck)
        self.log(f'Layer {layer} broadcast sent.')

###########################################################
def create_network():
    # place nodes over 100x100 grids
    for x in range(10):
        for y in range(10):
            px = 50 + x*60 + random.uniform(-20, 20)
            py = 50 + y*60 + random.uniform(-20, 20)
            sim.add_node(Node, pos=(px, py), tx_range=75)
 
# setting the simulation
sim = DawnSimVis.Simulator(
    duration=100,
    timescale=1,
    visual=False,
    terrain_size=(650, 650),
    title='Asynchronous BFS with ACK and REJECT')


# creating network
create_network()


sim.run()
# start the simulation
print("hello")