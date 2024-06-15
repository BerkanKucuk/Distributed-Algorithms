import re
filename = 'asenkrondegerler2024-05-31 23-01-42txt'
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
print("Coordinates:")

for i in range (1,3):
    liste49= []
    konum = i*49-1
    for k in range(0,konum+1):
        liste49.append(coordinates[k]) #48 - 97

for j in range(1,3):       
    liste100= []                     
    yenikonum = konum + j*100-1

    for c in range(konum+1,yenikonum+1):#49+49+100-1=197 98-197
        liste100.append(coordinates[c])

print(liste49)
print('------------')
print('------------')
print(liste100)

# for i, (x, y) in enumerate(coordinates):

#     print(f"Value {i}: x={x}, y={y}")