import networkx as nx
import matplotlib.pyplot as plt
import random

import warnings
warnings.filterwarnings("ignore", module="networkx")

# number of nodes
N = 10000
# probability that two nodes are connected
P_CONNECT = 0.005

# seed ~1% of population as sick
P_INIT_SICK = 0.01 

# Probability someone is sick tests positive and is isolated
TEST_POSITIVE = 0.8
# probability of infection from unidentified sick node to healthy neighbor
P_INFECT = 0.05 
# probability of infection from isolated sick node to healthy neighbor
P_INFECT_ISO = 0.01 
# number of iterations/days
NUM_ITERS = 10

# probability that a neighbor is isolated in strategy c
P_ISOLATE_NBR = 0.25

# ALL NODES THAT HAVE BEEN INFECTED
SICK_NODES = set()

# NODES THAT HAVE BEEN INFECTED, TESTED POSITIVE, AND ISOLATED
# TP_NODES is a subset of SICK_NODES
TP_NODES = set() 

def generate_graph():
	G = nx.binomial_graph(N, P_CONNECT)
	return G

def stepA(G):
	for node in SICK_NODES:
		if random.random() < TEST_POSITIVE:
			TP_NODES.add(node)

	sick_nodes = list(SICK_NODES.copy())
	for node in sick_nodes:
		for neighbor in G.neighbors(node):
			if node in TP_NODES:
				if random.random() < P_INFECT_ISO:
					SICK_NODES.add(neighbor)
			else:
				if random.random() < P_INFECT:
					SICK_NODES.add(neighbor)

def stepB(G):
	for node in SICK_NODES:
		if random.random() < TEST_POSITIVE:
			TP_NODES.add(node)
			# if someone tests positive, isolate all neighbors as well
			for neighbor in G.neighbors(node):
				TP_NODES.add(neighbor)
	
	sick_nodes = list(SICK_NODES.copy())
	for node in sick_nodes:
		for neighbor in G.neighbors(node):
			if node in TP_NODES:
				if random.random() < P_INFECT_ISO:
					SICK_NODES.add(neighbor)
			else:
				if random.random() < P_INFECT:
					SICK_NODES.add(neighbor)

def stepB(G):
	for node in SICK_NODES:
		if random.random() < TEST_POSITIVE:
			TP_NODES.add(node)
			# if someone tests positive, isolate SOME neighbors as well
			for neighbor in G.neighbors(node):
				if random.random() < P_ISOLATE_NBR:
					TP_NODES.add(neighbor)
	
	sick_nodes = list(SICK_NODES.copy())
	for node in sick_nodes:
		for neighbor in G.neighbors(node):
			if node in TP_NODES:
				if random.random() < P_INFECT_ISO:
					SICK_NODES.add(neighbor)
			else:
				if random.random() < P_INFECT:
					SICK_NODES.add(neighbor)

def stepD(G):
	sick_nodes = list(SICK_NODES.copy())
	for node in sick_nodes:
		for neighbor in G.neighbors(node):
			if random.random() < P_INFECT:
				SICK_NODES.add(neighbor)

def draw(G):
	color_map = ['green'] * G.number_of_nodes()
	for n in SICK_NODES:
		color_map[n] = "red"
	for n in TP_NODES:
		color_map[n] = "orange"
	nx.draw(G, node_color = color_map)
	plt.show()

def init_sick_nodes(G):
	for node in G:
		if random.random() < P_INIT_SICK:
			SICK_NODES.add(node)

if __name__ == "__main__":
	G = generate_graph()
	init_sick_nodes(G)
	for i in range(NUM_ITERS):
		print("Number of people infected at time " + str(i) + ": " + str(len(SICK_NODES)))
		stepB(G)
		#draw(G)
	print("Number of people infected at end: " + str(len(SICK_NODES)))
