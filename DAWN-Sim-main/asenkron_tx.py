import random
import sys
sys.path.insert(1, '.')
from source import DawnSimVis
import time
from datetime import datetime

SOURCE = 0
timessss= []
message_count = [0]
class Node(DawnSimVis.BaseNode):

    def init(self):
        self.parent = None
        self.layer = float('inf')
        self.children = set()
        self.others = set()

    def run(self):
        if self.id == SOURCE:
            self.layer = 0
            self.change_color(1, 0, 0)  # Color the source node red
            self.broadcast_layer(self.layer)

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

    def send_ack(self, recipient_id):
        if recipient_id is not None:
            pck = {'type': 'ack', 'sender_id': self.id}
            self.send(recipient_id, pck)
            message_count[0] += 1
            # self.log(f'ACK sent to Node {recipient_id}.')cle

    def send_reject(self, recipient_id):
        if recipient_id is not None:
            pck = {'type': 'reject', 'sender_id': self.id}
            self.send(recipient_id, pck)
            message_count[0] += 1
            # self.log(f'REJECT sent to Node {recipient_id}.')
            timessss.append(self.now)
            

    def broadcast_layer(self, layer):
        pck = {'type': 'layer', 'sender_id': self.id, 'sender_layer': layer}
        self.send(DawnSimVis.BROADCAST_ADDR, pck)
        message_count[0] += 1
        # self.log(f'Layer {layer} broadcast sent.')
       
        
        # # Check if this is the last broadcast message
        # if layer == 99:  # Assuming 100 layers
        #     self.finish()  # Finish the simulation after broadcasting the last layer

    def getMessageCount(self):
        return self.message_count


NUM_TESTS = 1
NODE_COUNT = 256
TX_RANGE = [75,100,125,150]


avg_times_and_message = {
    "75":0,
    "100":0,
    "125":0,
    "150":0,
}


def create_network(tx_range):
    # square to node count 
    nodes = []
    terrain_margin = 50
    node_distance = 60

    for x in range(16):
        for y in range(16):

             while True:
                px = terrain_margin + x * node_distance + random.uniform(-20, 20)
                py = terrain_margin + y * node_distance + random.uniform(-20, 20)

                # Ensure the new node has at least one neighbor
                if any((px - nx)**2 + (py - ny)**2 <= tx_range**2 for nx, ny in nodes):
                    nodes.append((px, py))
                    sim.add_node(Node, pos=(px, py), tx_range=tx_range)
                    break
                elif len(nodes) == 0:
                    nodes.append((px, py))
                    sim.add_node(Node, pos=(px, py), tx_range=tx_range)
                    break

for tx_range in TX_RANGE:
    avg_msg_count = 0
    avg_process_time = 0
    # clear avarage times list for each tx_range
    times = []
    # clear times list for each test
    timessss = []
    print(timessss)
    message_count = [0]
    for _ in range(NUM_TESTS):
        print(f'Running test {_} of {tx_range} tx_range...')
        sim = DawnSimVis.Simulator(
            duration=60,
            timescale=0.3,
            visual=True,
            terrain_size=(650, 650),
            title=f'AsyncBFS Test: {tx_range} tx_range'
        )

        create_network(tx_range)
        start_time = time.time()
        sim.run()
        # print(timessss)
        times_spent = timessss.pop()
        print('TIMES SPEND:',times_spent)
        times.append(times_spent) #ortalama zamanı bulmak için zamanların son hali
        print('Test completed.')
        end_time = time.time()
        
        print(f'Time taken: {end_time - start_time} seconds')
      

        # Simülasyon sonuçlarını analiz etmek için burada kod ekleyin

        # Ortalama mesaj sayısı ve işlem süresini hesaplayın
        # avg_msg_count += ...
        # avg_process_time += ...
    # print(Node.getMessageCount())
    avg_msg_count = message_count[0]/NUM_TESTS
    print("Times:",times)
    tümsüreler = sum(times)
    print("Tüm",tümsüreler)
    # Ortalama işlem süresini saniyeye çevirin
    avg_process_time = tümsüreler / NUM_TESTS
    avg_times_and_message[str(tx_range)] ='avg_time:'+str(avg_process_time)+' message_count:'+str(avg_msg_count)
    print(f'TX_RANGE: {tx_range}, Ortalama Mesaj Sayısı: {avg_msg_count}, Ortalama İşlem Süresi: {avg_process_time}')


now = datetime.now()
timestamp = now.strftime("%Y-%m-%d %H-%M-%S")
filename = 'ortalamamesaj_vesure_TX_RANGE_' + timestamp + '.txt'

with open(filename, 'w', encoding='utf-8') as dosya:
    # Sözlükteki her bir anahtar-değer çifti için döngü
    for key, value in avg_times_and_message.items():
        # Anahtar ve değeri yaz
        dosya.write(f"{key}:{value}\r\n")

