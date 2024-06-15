from datetime import datetime
from enum import Enum
import random
import sys
sys.path.insert(1, '.')
from source import DawnSimVis

ROOT = 0

last_time = []
message_count = [0]
###########################################################
class Node(DawnSimVis.BaseNode):


    ###################
    def init(self):
        self.neighbors = []
        self.parent = None
        self.layer = None
        self.round = 1  
        self.children = set()  
        self.others = set()  
        self.received_upcasts = []
        
    ###################
    def run(self):
        self.send(DawnSimVis.BROADCAST_ADDR, {'source': self.id, 'type': 'HeartBeat'})
        if self.id == ROOT:
            self.layer = 0
            
            
            self.set_timer(5,self.cb_start)
            # self.send(DawnSimVis.BROADCAST_ADDR,)
            # while self.children != self.neighbors:
                

    ###################
    def cb_start(self):
        self.change_color(1, 0, 0)  # Color the source node red
        self.broadcast_layer(self.layer + 1)
        # if self.id == ROOT and self.children == set(self.neighbors):
        #     while self.children != set(self.neighbors):
        #         pass  # Wait until all neighbors send ACK
        #     print('while finish')
        #     self.broadcast_round(self.round)
            
    ###################
    def broadcast_layer(self, layer):
        pck = {'source': self.id, 'type': 'layer', 'sender_layer': layer}
        self.send(DawnSimVis.BROADCAST_ADDR, pck)
        self.log(f'Layer {layer} broadcast sent.')
        message_count[0] += 1

    def broadcast_round(self, roundi):
        pck = {'source': self.id, 'type': 'round', 'round': roundi}
        self.send(DawnSimVis.BROADCAST_ADDR, pck)
        self.log(f'Raoun {roundi} broadcast sent.')
        message_count[0] += 1
    ##########################
    def on_receive(self, pck):
        msg_type = pck['type']
        sender_id = pck['source']
        sender_layer = pck.get('sender_layer', None)
        
        # print(f'{self.id} nin neighbors : {self.neighbors}')
        
        if pck['type'] == 'HeartBeat':
            self.neighbors.append(pck['source'])
            
        elif msg_type == 'layer':
            if self.id != ROOT:
                if self.parent is None:
                    self.parent = sender_id
                    self.layer = sender_layer
                    self.send_ack(self.parent)
                else:
                    self.send_reject(sender_id)
            else:
                self.send_reject(sender_id)
        
        elif msg_type == 'ack':
            self.children.add(sender_id)
            # if(self.id == ROOT):
            #     print(self.id, 'root ', self.children)
            #     self.parent = -1
            #     return
            
            print(f'{self.id} => peren : {self.parent} neighbors : {self.neighbors} , children : {self.children}, others : {self.others}')
            print(self.children.union(self.others) == set(self.neighbors))
            print(len(self.children.union(self.others)) ==len(set(self.neighbors)))
            print(self.neighbors)
            if self.children.union(self.others) == set(self.neighbors):
                print('Eşitlik sağlandı ....')
                if self.id != ROOT:
                    if self.children is None :
                        print('doğru')
                        print(self.id,' perent : ', self.parent)
                        self.send_upcast(self.parent, True)
                    else:
                        self.send_upcast(self.parent, False)

                else:
                    if self.id is ROOT:
                        print('root ack aldı')
                        self.broadcast_round(self.round)
                 
            

        
        elif msg_type == 'reject':
            self.others.add(sender_id)
            if self.children.union(self.others) == set(self.neighbors):
                print(f'Receive Reject Eşitlk sağlandı')
                if not self.children:
                    self.send_upcast(self.parent, True)
                else:
                    self.send_upcast(self.parent, False)
            

        elif msg_type == 'round':
            r = pck['round']
            print(f'alınan round mesajı : ', r)
            if r == self.layer:
                print('broadcast layer', self.layer +1)
                self.broadcast_layer(self.layer + 1)
                print('broadcast layer', self.layer +1)
            else:
                if not self.children:
                    self.send_upcast(self.parent, True)
                else:
                    print("ELSE ROOundDDD")
                    self.send_round(self.children, r)


        elif msg_type == 'upcast':
            print('upcast geldi')
            print(self.received_upcasts)
            self.received_upcasts.append(pck['finished'])
            print('upcast eklendi')
            print(self.received_upcasts)
            if 1:
                print('upcast root')
                print(f"self.received_upcasts before len(): {len(self.received_upcasts)}")
                print(self.received_upcasts,self.children)
             
                if len(self.received_upcasts) == len(self.children):
                    print('received_upcasts = children')
                    if all(self.received_upcasts):
                        print(self.id," : ALL TRUE")
                        if self.id is not ROOT:
                            print(f'upcast : ', self.id)
                            self.send_upcast(self.parent, True)
                        # 30.05.2024
                        else:
                            print('Root geldi....')
                            print("UPCAST ROOOT, self.round :", self.round)
                            self.round = self.round + 1
                            print("UPCAST ROOOT ALL TRUE",self.received_upcasts)
                            # self.broadcast_round(self.round)
                
                    else:
                        if self.id is ROOT:
                            print("UPCAST ROOOT, self.round :", self.round)
                            self.round = self.round + 1
                            self.broadcast_round(self.round)
                        else:
                            self.send_upcast(self.parent, False)
                    self.received_upcasts = []
                    last_time.append(self.now)

    ###############################
    ###############################
    # round mesahjı ve upcast mesajı nasıl yazılmalı
    def send_round(self, recipient_id, r):
        pck = {'type': 'round', 'source': self.id, 'round': r}
        print(recipient_id,pck)
        for id in recipient_id:
            self.send(id, pck)
            message_count[0] += 1
        self.log(f'{self.id} : UPCAAST {r} sent to Node {recipient_id}.')
        

    ###############################
    def send_upcast(self, recipient_id, finished):
        print(recipient_id)
        if recipient_id is not None:
            pck = {'type': 'upcast', 'source': self.id, 'finished': finished}
            self.send(recipient_id, pck)
            self.log(f'{self.id} : UPCAST sent to Node {recipient_id}. => {finished}')
            message_count[0] += 1

    ###############################
    def send_ack(self, recipient_id):
        if recipient_id is not None:
            pck = {'type': 'ack', 'source': self.id}
            self.send(recipient_id, pck)
            self.log(f'{self.id} : ACK sent to Node {recipient_id}.')
            message_count[0] += 1

    ##################################
    def send_reject(self, recipient_id):
        if recipient_id is not None:
            pck = {'type': 'reject', 'source': self.id}
            self.send(recipient_id, pck)
            self.log(f'{self.id} : REJECT sent to Node {recipient_id}.')
            message_count[0] += 1

TEST_SAYİSİ = 1
NODE_COUNT = 256
TX_RANGE = [75,100,125,150]

degerler = {
    "75":0,
    "100":0,
    "125":0,
    "150":0,
}

###########################################################
def create_network(txrange):
    # place nodes over 100x100 grids
    for x in range(16):
        for y in range(16):
            px = 50 + x*60 + random.uniform(-20,20)
            py = 50 + y*60 + random.uniform(-20,20)
            sim.add_node(Node, pos=(px,py), tx_range=txrange)

for txrange in TX_RANGE:
    ortalamasure = 0
    ortalamamesaj =0
    genelsureler=[]
    last_time=[]
    message_count = [0]
    for _ in range(TEST_SAYİSİ):
        print(f'Running test {_} of {txrange} tx_range...')
        sim = DawnSimVis.Simulator(
            duration=400,
            timescale=0.3,
            visual=False,
            terrain_size=(650, 650),
            title=f'SYNC BFS Test: {txrange} tx_range'
        )
# setting the simulation
    
    create_network(txrange)
    sim.run()
    last_time2=last_time.pop()
    genelsureler.append(last_time2)
    print(genelsureler)
    ortalamamesaj=message_count[0]
    # ortalamasure = genelsureler[0]/ TEST_SAYİSİ
    # print(genelsureler)
    degerler[str(txrange)] ='avg_time:'+str(genelsureler)+' message_count:'+str(ortalamamesaj)

    # print(f'TX_RANGE: {txrange}, degerler : {degerler}')

now = datetime.now()
timestamp = now.strftime("%Y-%m-%d %H-%M-%S")
filename = 'senk_ort_MaT' + timestamp + '.txt'

with open(filename, 'w', encoding='utf-8') as dosya:
    # Sözlükteki her bir anahtar-değer çifti için döngü
    for key, value in degerler.items():
        # Anahtar ve değeri yaz
        dosya.write(f"{key}:{value}\r\n")
# start the simulation 
