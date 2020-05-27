import networkx as nx
import matplotlib.pyplot as plt
import random

import warnings
warnings.filterwarnings("ignore", module="networkx")

# number of nodes
N = 10000
# probability that two nodes are connected
P_CONNECT = 0.05
# seed ~1% of population as sick
P_INIT_SICK = 0.01 
# probability of infection from sick node to healthy neighbor
P_INFECT = 0.001 
# number of iterations/days
NUM_ITERS = 10

def generate_graph():
    G = nx.binomial_graph(N, P_CONNECT)
    return G

def step(G, color_map):
    for node in G:
        if color_map[node] == 'red': 
            for neighbour in G.neighbors(node):
                if color_map[neighbour] == 'green':
                    if random.random() < P_INFECT:
                        color_map[neighbour] = 'red'

def draw(G, color_map):
    nx.draw(G, node_color = color_map)
    plt.show()

def init_sick_nodes(G):
    color_map = []
    for node in G:
        if random.random() < P_INIT_SICK:
            color_map.append('red')
        else: 
            color_map.append('green')
    return color_map    

if __name__ == "__main__":
    G = generate_graph()
    color_map = init_sick_nodes(G)
    for i in range(NUM_ITERS):
        print("Number of people infected at time " + str(i) + ": " + str(color_map.count('red')))
        #draw(G, color_map)
        step(G, color_map)
    print("Number of people infected at end: " + str(color_map.count('red')))
