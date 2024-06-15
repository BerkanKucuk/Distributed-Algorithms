import random
import sys
sys.path.insert(1, '.')
from source import DawnSimVis

SOURCE = 0

class Node(DawnSimVis.BaseNode):

    def init(self):
        self.neighbors = set()  # Düğümün komşularını saklamak için bir küme oluştur
        self.parent = None
        self.layer = float('inf')
        self.children = set()
        self.others = set()
        self.processed = False  # Düğümün işlenip işlenmediğini izlemek için
        self.received_rounds = set()

    def run(self):
        if self.id == SOURCE:
            self.layer = 0
            self.change_color(1, 0, 0)  # Kaynak düğümü kırmızıya boyar
            self.broadcast_layer(self.layer)
            self.processed = True

    def on_receive(self, pck):
        msg_type = pck['type']
        sender_id = pck['sender_id']
        sender_layer = pck.get('sender_layer', None)
        round_number = pck.get('round', None)

        if msg_type == 'layer':
            if sender_layer < self.layer:
                if self.parent is not None:
                    self.send_reject(self.parent)
                self.layer = sender_layer
                self.parent = sender_id
                self.send_ack(self.parent)
                self.broadcast_layer(self.layer + 1)
                self.processed = True
            else:
                self.send_reject(sender_id)

        elif msg_type == 'ack':
            self.others.discard(sender_id)
            self.children.add(sender_id)
        
        elif msg_type == 'reject':
            self.children.discard(sender_id)
            self.others.add(sender_id)

        elif msg_type == 'round':
            if round_number not in self.received_rounds:
                self.received_rounds.add(round_number)
                self.check_processed()

        self.check_processed()

    def check_processed(self):
        if self.parent is not None and len(self.children) + len(self.others) == len(self.neighbors):
            if not self.processed:
                self.processed = True
                self.broadcast_round(self.layer + 1)
                self.broadcast_upcast()

    def broadcast_round(self, round_number):
        pck = {'type': 'round', 'sender_id': self.id, 'round': round_number}
        self.send(DawnSimVis.BROADCAST_ADDR, pck)
        self.log(f'Round {round_number} broadcast sent.')

    def broadcast_upcast(self):
        pck = {'type': 'upcast', 'sender_id': self.id}
        self.send(self.parent, pck)
        self.log('Upcast broadcast sent.')

    def send_ack(self, recipient_id):
        if recipient_id is not None:
            pck = {'type': 'ack', 'sender_id': self.id}
            self.send(recipient_id, pck)
            self.log(f'ACK sent to Node {recipient_id}.')

    def send_reject(self, recipient_id):
        if recipient_id is not None:
            pck = {'type': 'reject', 'sender_id': self.id}
            self.send(recipient_id, pck)
            self.log(f'REJECT sent to Node {recipient_id}.')

    def broadcast_layer(self, layer):
        pck = {'type': 'layer', 'sender_id': self.id, 'sender_layer': layer}
        self.send(DawnSimVis.BROADCAST_ADDR, pck)
        self.log(f'Layer {layer} broadcast sent.')

def create_network():
    for x in range(6):
        for y in range(6):
            px = 50 + x*60 + random.uniform(-20, 20)
            py = 50 + y*60 + random.uniform(-20, 20)
            sim.add_node(Node, pos=(px, py), tx_range=75)

sim = DawnSimVis.Simulator(
    duration=100,
    timescale=1,
    visual=True,
    terrain_size=(650, 650),
    title='Synchronous BFS with ACK, REJECT, Round, and Upcast')

create_network()

sim.run()





