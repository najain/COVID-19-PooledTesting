import networkx as nx
import matplotlib.pyplot as plt
import random
import sys

import warnings
warnings.filterwarnings("ignore", module="networkx")

# number of nodes
N = 1000

# expected number of neighbors per node
# Chosen to be the median number of people met in a day by an individual:
# https://www.researchgate.net/figure/Daily-average-number-of-contacts-per-person-in-age-group-j-The-average-number-of_fig2_228649013
NUM_NEIGHBORS = 20

# probability that two nodes are connected
# Chosen so that the expected number of connections per node is NUM_NEIGHBORS
P_CONNECT = 1/N * NUM_NEIGHBORS

# seed ~1% of population as sick
P_INIT_SICK = 0.01 

# Probability someone is sick tests positive and is isolated
# https://www.acc.org/latest-in-cardiology/journal-scans/2020/05/18/13/42/variation-in-false-negative-rate-of-reverse
TEST_POSITIVE = 0.7

# number of iterations/days
NUM_ITERS = 60

# Median Reproductive Number for COVID-19
# https://wwwnc.cdc.gov/eid/article/26/7/20-0282_article
R_0 = 5.7

# probability of infection from unidentified sick node to healthy neighbor
P_INFECT =  R_0/(NUM_NEIGHBORS * NUM_ITERS)

# probability of infection from isolated sick node to healthy neighbor
# We reduce it to 10% of P_INFECT
P_INFECT_ISO = 0.1  * P_INFECT

# probability that a neighbor is isolated in strategy c
P_ISOLATE_NBR = 0.25

# number of tests you can perform in a time step.
TIMESTEP_TEST_CAPACITY = 1000

# ALL NODES THAT HAVE BEEN INFECTED
SICK_NODES = set()

# NODES THAT HAVE BEEN INFECTED, TESTED POSITIVE, AND ISOLATED
# ISOLATED_NODES is a subset of SICK_NODES
ISOLATED_NODES = set() 


def generate_graph():
	G = nx.binomial_graph(N, P_CONNECT, seed=1)
	return G

# Test and Isolate: Whoever gets sick is isolated immediately.
# Models universal testing when TIMESTEP_TEST_CAPACITY is equal to number of nodes.
def stepA(G):
	testCount = 0
	for node in random.sample(list(G),TIMESTEP_TEST_CAPACITY):
		if testCount < TIMESTEP_TEST_CAPACITY:
			if (node in SICK_NODES) and random.random() < TEST_POSITIVE:
				ISOLATED_NODES.add(node)
			testCount += 1

	sick_nodes = list(SICK_NODES.copy())
	for node in sick_nodes:
		for neighbor in G.neighbors(node):
			if node in ISOLATED_NODES:
				if random.random() < P_INFECT_ISO:
					SICK_NODES.add(neighbor)
			else:
				if random.random() < P_INFECT:
					SICK_NODES.add(neighbor)

# Full Contact Tracing: isolate people who test positive as well as all neighbors.
def stepB(G):
	testCount = 0
	for node in random.sample(list(G),TIMESTEP_TEST_CAPACITY):
		if testCount < TIMESTEP_TEST_CAPACITY:
			if (node in SICK_NODES) and random.random() < TEST_POSITIVE:
				ISOLATED_NODES.add(node)
				# if someone tests positive, isolate all neighbors as well
				for neighbor in G.neighbors(node):
					ISOLATED_NODES.add(neighbor)
			testCount += 1
	
	sick_nodes = list(SICK_NODES.copy())
	for node in sick_nodes:
		for neighbor in G.neighbors(node):
			if node in ISOLATED_NODES:
				if random.random() < P_INFECT_ISO:
					SICK_NODES.add(neighbor)
			else:
				if random.random() < P_INFECT:
					SICK_NODES.add(neighbor)

# Noisy Contact Tracing: isolate people who test positive and some neighbors.
def stepC(G):
	testCount = 0
	for node in random.sample(list(G),TIMESTEP_TEST_CAPACITY):
		if testCount < TIMESTEP_TEST_CAPACITY:
			if (node in SICK_NODES) and random.random() < TEST_POSITIVE:
				ISOLATED_NODES.add(node)
				# if someone tests positive, isolate SOME neighbors as well
				for neighbor in G.neighbors(node):
					if random.random() < P_ISOLATE_NBR:
						ISOLATED_NODES.add(neighbor)
			testCount += 1
	
	sick_nodes = list(SICK_NODES.copy())
	for node in sick_nodes:
		for neighbor in G.neighbors(node):
			if node in ISOLATED_NODES:
				if random.random() < P_INFECT_ISO:
					SICK_NODES.add(neighbor)
			else:
				if random.random() < P_INFECT:
					SICK_NODES.add(neighbor)

# No Isolation: unmitigated spread of disease.
def stepD(G):
	sick_nodes = list(SICK_NODES.copy())
	for node in sick_nodes:
		for neighbor in G.neighbors(node):
			if random.random() < P_INFECT:
				SICK_NODES.add(neighbor)

# Everyone Isolated: models lockdown with some noisy transmission.
def stepE(G):
	for node in G:
		ISOLATED_NODES.add(node)

	sick_nodes = list(SICK_NODES.copy())
	for node in sick_nodes:
		for neighbor in G.neighbors(node):
			if random.random() < P_INFECT_ISO:
				SICK_NODES.add(neighbor)

def draw(G):
	color_map = ['green'] * G.number_of_nodes()
	for n in SICK_NODES:
		color_map[n] = "red"
	for n in ISOLATED_NODES:
		if n in SICK_NODES:
			color_map[n] = "orange"
		else:
			color_map[n] = "yellow"
	nx.draw(G, node_color = color_map)
	plt.show()

def init_sick_nodes(G):
	for node in G:
		if random.random() < P_INIT_SICK:
			SICK_NODES.add(node)

if __name__ == "__main__":
	if len(sys.argv) != 2:
		print("Please enter a valid strategy.")
		exit()

	G = generate_graph()
	init_sick_nodes(G)
	for i in range(NUM_ITERS):
		print("Number of people infected at time " + str(i) + ": " + str(len(SICK_NODES)))
		print("Number of people isolated at time " + str(i) + ": " + str(len(ISOLATED_NODES)))

		if sys.argv[1] == 'A':
			stepA(G)
		elif sys.argv[1] == 'B':
			stepB(G)
		elif sys.argv[1] == 'C':
			stepC(G)
		elif sys.argv[1] == 'D':
			stepD(G)
		elif sys.argv[1] == 'E':
			stepE(G)
		else:
			print("Incorrect strategy entered.")
			exit()
	draw(G)
	print("Number of people infected at end: " + str(len(SICK_NODES)))
