from enum import Enum
import random
import sys
sys.path.insert(1, '.')
from source import DawnSimVis
import re
ROOT = 0
import datetime


timessss= []
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
            
            
            self.set_timer(1,self.cb_start)
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
                    timessss.append(self.now)

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

NUM_TESTS = 1
NODE_COUNTS = [49,100,144,196,256]
TX_RANGE = 75


degerler = {
    "49":0,
    "100":0,
    "144":0,
    "196":0,
    "256":0,
}


filename = 'asenkrondegerler2024-06-01 18-44-47.txt'
def extract_coordinates(filename):
    coordinates = []
    with open(filename, 'r') as f:
        for line in f:
            match = re.search(r'\(([^)]+)\)', line)
            if match:
                coords = match.group(1).split(', ')
                x, y = float(coords[0]), float(coords[1])
                coordinates.append((x, y))
    return coordinates

coordinates = extract_coordinates(filename)
#print("Coordinates:")

# for i in range (1,3):
#     liste49= []
#     konum = i*49-1
#     for k in range(0,konum+1):
#         liste49.append(coordinates[k]) #48 - 97

# for j in range(1,3):       
#     liste100= []                     
#     yenikonum = konum + j*100-1

#     for c in range(konum+1,yenikonum+1):#49+49+100-1=197 98-197
#         liste100.append(coordinates[c])
###########################################################
sinir = [0]
yenisinir = [0]
yenisinir144 = [0]
yenisinir196 = [0]
yenisinir256 = [0]
def create_network(nd,i):

    if nd == 49:

        sinir.append(i*49)
        for k in range(sinir[i-1],sinir[i]):
            pos = coordinates[k]
            sim.add_node(Node,pos=pos,tx_range=TX_RANGE)
            

    if nd == 100:
        yenisinir[0] = sinir[-1]
        yenisinir.append(yenisinir[i-1]+100)
        for c in range(yenisinir[i-1],yenisinir[i]):
            pos = coordinates[c]
            sim.add_node(Node,pos=pos,tx_range=TX_RANGE)

    if nd == 144:
        yenisinir144[0] = yenisinir[-1]
        yenisinir144.append(yenisinir144[i-1]+144)
        for d in range(yenisinir144[i-1],yenisinir144[i]):
            pos = coordinates[d]
            sim.add_node(Node,pos=pos,tx_range=TX_RANGE)

    if nd == 196:
        yenisinir196[0] = yenisinir144[-1]
        yenisinir196.append(yenisinir196[i-1]+196)
        for e in range(yenisinir196[i-1],yenisinir196[i]):
            pos = coordinates[e]
            sim.add_node(Node,pos=pos,tx_range=TX_RANGE)

    if nd == 256:
        yenisinir256[0] = yenisinir196[-1]
        yenisinir256.append(yenisinir256[i-1]+256)
        for y in range(yenisinir256[i-1],yenisinir256[i]):
            pos = coordinates[y]
            sim.add_node(Node,pos=pos,tx_range=TX_RANGE)

    # place nodes over 100x100 grids
    
for nd in NODE_COUNTS:
    
    avg_msg_count = 0
    avg_process_time = 0
    times = []
    timessss = []
    message_count = [0]
    if nd == 49:
        duration = 150
    elif nd == 100:
        duration = 200
    elif nd == 144:
        duration = 300
    elif nd == 196:
        duration = 400
    elif nd == 256:
         duration == 500   
         
    for i in range(NUM_TESTS):
# setting the simulation
        sim = DawnSimVis.Simulator(
            duration=duration,
            timescale=0.1,
            visual=False,
            terrain_size=(650, 650),
            title='Flooding')
        create_network(nd,i+1)
        sim.run()
        times_spent = timessss.pop()
        print('times spend:',times_spent)
        times.append(times_spent)
        print('Test completed.')

    avg_msg_count = message_count[0]/NUM_TESTS
    tümsüreler = sum(times)
    avg_process_time = tümsüreler / NUM_TESTS
    degerler[str(nd)] ='avg_time:'+str(avg_process_time)+' message_count:'+str(avg_msg_count)
    print(f'Düğüm Sayısı: {nd}, Ortalama Mesaj Sayısı: {avg_msg_count}, Ortalama İşlem Süresi: {avg_process_time}')

    # creating network
    # start the simulation
now = datetime.datetime.now()
timestamp = now.strftime("%Y-%m-%d %H-%M-%S")
filename = 'senkron_avg' + timestamp + '.txt'


with open(filename, 'w', encoding='utf-8') as dosya:
    # Sözlükteki her bir anahtar-değer çifti için döngü
    for key, value in degerler.items():
        # Anahtar ve değeri yaz
        dosya.write(f"{key}:{value}\r\n")      
