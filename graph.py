import networkx as nx
import matplotlib.pyplot as plt
import random
import sys
import argparse
import numpy as np
import warnings
import os
import datetime


warnings.filterwarnings("ignore", module="networkx")

# testing and quarantine strategy. Default is unmitigated spread.
# Options are as follows:
# A: Test and Isolate: Whoever tests positive is isolated immediately. No initial lockdown.
# B: Test, Full Contact Trace, and Isolate. No initial lockdown.
# C: Test, Noisy Contact Trace, and Isolate. No initial lockdown.
# D: Unmitigated Spread. No lockdown.
# E: Complete Lockdown for full duration.
# F: Start with Complete Lockdown, then do Pooled testing With Overly Conservative Noisy Contact Tracing.
# G: Start with Complete Lockdown, then do Pooled testing with no Noisy Contact Tracing.
# H: Start with Complete Lockdown, then do individual testing without pooling, but with Noisy Contact Tracing.
STRATEGY = "D"
# Default is unmitigated spread.

# number of nodes in social network
N = 10000

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
TEST_POSITIVE = 0.75

# Number of simulation episodes to run
NUM_SIMULATIONS = 100

# number of iterations/days per simulation
NUM_ITERS = 30

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
TIMESTEP_TEST_CAPACITY = 100

# number of people to put in a group for pooled testing.
# https://www.medrxiv.org/content/10.1101/2020.03.26.20039438v1
POOL_SIZE = 8

# root location to store the data from the results of the simulations.
# each simulation will be stored in a subdirectory of this, including the hyperparameters.
SAVE_DIR = os.path.dirname(os.path.realpath(__file__)) + "/simulations"

LOAD_DIR = os.path.dirname(os.path.realpath(__file__)) + "/simulations"


# Whether or not to draw some visuals.
VISUALIZE = False

# Whether or not to draw some visuals.
VERBOSE = False

# ALL NODES THAT HAVE BEEN INFECTED
SICK_NODES = set()

# NODES THAT HAVE BEEN INFECTED, TESTED POSITIVE, AND ISOLATED
# ISOLATED_NODES is a subset of SICK_NODES
ISOLATED_NODES = set() 



def generateGraph():
	G = nx.binomial_graph(N, P_CONNECT, seed=1)
	return G

# Test and Isolate: Whoever tests positive is isolated immediately.
# Models universal testing when TIMESTEP_TEST_CAPACITY is equal to number of nodes.
# No initial lockdown.
def stepA(G):
	testCount = 0
	for node in random.sample(list(G),TIMESTEP_TEST_CAPACITY):
		if testCount < TIMESTEP_TEST_CAPACITY:
			if (node in SICK_NODES) and random.random() < TEST_POSITIVE:
				ISOLATED_NODES.add(node)
			testCount += 1

# Full Contact Tracing: isolate people who test positive as well as all neighbors.
# No initial lockdown.
def stepB(G):
	testCount = 0
	for node in random.sample(list(G),TIMESTEP_TEST_CAPACITY):
		if testCount < TIMESTEP_TEST_CAPACITY:
			if (node in SICK_NODES) and random.random() < TEST_POSITIVE:
				ISOLATED_NODES.add(node)
				# if someone tests positive, isolate all neighbors as well.
				for neighbor in G.neighbors(node):
					ISOLATED_NODES.add(neighbor)
			testCount += 1

# Noisy Contact Tracing: isolate people who test positive and some neighbors.
# No initial lockdown.
def stepC(G):
	testCount = 0
	for node in random.sample(list(G),TIMESTEP_TEST_CAPACITY):
		if testCount < TIMESTEP_TEST_CAPACITY:
			if (node in SICK_NODES) and random.random() < TEST_POSITIVE:
				ISOLATED_NODES.add(node)
				# if someone tests positive, isolate SOME neighbors as well.
				for neighbor in G.neighbors(node):
					if random.random() < P_ISOLATE_NBR:
						ISOLATED_NODES.add(neighbor)
			testCount += 1

# No Isolation: unmitigated spread of disease.
# No initial lockdown.
def stepD(G):
	# Nothing to do regarding testing and isolation.
	None

# Everyone Isolated: models lockdown with some noisy transmission.
# Has full initial lockdown.
def stepE(G):
	# Nothing to do regarding testing and isolation.
	None

# Initial lockdown, followed by pooled testing with overly conservative noisy contact tracing.
# Slowly opens up. The idea is that if a pool tests positive, you lock them all down as well as some subset
# of their neighbors. But if a pool tests negative, they are removed from isolation.
def stepF(G):
	# Number of tests we can do in one iteration.
	for test in range(TIMESTEP_TEST_CAPACITY):
		# Boolean on whether we should quarantine the whole group.
		quarWholeGroup = False
		poolGroup = random.sample(list(G), POOL_SIZE)
		# If you find a sick person in your group, quarantine the whole group and their neighbors.
		for node in poolGroup:
			if (node in SICK_NODES):
				quarWholeGroup = True
		if quarWholeGroup and random.random() < TEST_POSITIVE:
			for node in poolGroup:
				ISOLATED_NODES.add(node)
				# noisy contact trace of positively identified sick node.
				for neighbor in G.neighbors(node):
					if random.random() < P_ISOLATE_NBR:
						ISOLATED_NODES.add(neighbor)
		# If test is not positive, remove group from isolation.
		if not quarWholeGroup:
			for node in poolGroup:
				if node in ISOLATED_NODES:
					ISOLATED_NODES.remove(node)

# Initial lockdown, followed by pooled testing with no contact tracing.
# Slowly opens up. Similar to strategy F, except quarantine actions are only taken on the pool, not
# on neighbors.
def stepG(G):
	# Number of tests we can do in one iteration.
	for test in range(TIMESTEP_TEST_CAPACITY):
		# Boolean on whether we should quarantine the whole group.
		quarWholeGroup = False
		poolGroup = random.sample(list(G), POOL_SIZE)
		# If you find a sick person in your group, quarantine the whole group only.
		for node in poolGroup:
			if (node in SICK_NODES):
				quarWholeGroup = True
		if quarWholeGroup and random.random() < TEST_POSITIVE:
			for node in poolGroup:
				ISOLATED_NODES.add(node)
		# If test is not positive, remove group from isolation.
		if not quarWholeGroup:
			for node in poolGroup:
				if node in ISOLATED_NODES:
					ISOLATED_NODES.remove(node)

# Initial lockdown, followed by individual testing with noisy contact tracing of tested participants.
# Slowly opens up.
def stepH(G):
	testCount = 0
	for node in random.sample(list(G),TIMESTEP_TEST_CAPACITY):
		if testCount < TIMESTEP_TEST_CAPACITY:
			if (node in SICK_NODES) and random.random() < TEST_POSITIVE:
				ISOLATED_NODES.add(node)
				# noisy contact trace of positively identified sick node.
				for neighbor in G.neighbors(node):
					if random.random() < P_ISOLATE_NBR:
						ISOLATED_NODES.add(neighbor)
			else: 
				if node in ISOLATED_NODES:
					ISOLATED_NODES.remove(node)
			testCount += 1

# To visualize the graph with colors
# Green is healthy and unisolated
# Red is sick and unisolated
# Yellow if healthy and isolated
# Orange is sick and isolated
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

# Calculate statistics and print out values.
def spreadStatistics(G):
	count = G.number_of_nodes()
	healthyFree = 0
	healthyIsolated = 0
	sickFree = 0
	sickIsolated = 0

	for n in G:
		if n in SICK_NODES:
			if n in ISOLATED_NODES:
				sickIsolated += 1
			else:
				sickFree += 1
		else:
			if n in ISOLATED_NODES:
				healthyIsolated += 1
			else:
				healthyFree += 1
	myLog("Number of healthy people free: " + str(healthyFree), False)
	myLog("Number of infected people free: " + str(sickFree), False)
	myLog("Number of infected people isolated: " + str(sickIsolated), False)
	myLog("Number of healthy people isolated: " + str(healthyIsolated), False)
	return (healthyFree, sickFree, sickIsolated, healthyIsolated)



def initSickNodes(G):
	for node in G:
		if random.random() < P_INIT_SICK:
			SICK_NODES.add(node)

# Wrapper to change amount of information logged. 
# val is the string that should be logged.
# overrideVERBOSE allows you to set a boolean to print the information anyways.
def myLog(val, overrideVERBOSE):
	if VERBOSE or overrideVERBOSE:
		print(val)

def plotHistogram(plotData, title):
	plt.hist(plotData, bins='auto') 
	plt.title(title) 
	plt.show()

if __name__ == "__main__":
	# Process arguments.
	parser = argparse.ArgumentParser(description='An agent based simulator for COVID-19 using a social network graph.')
	parser.add_argument('--strategy', help='testing and quarantine strategy', required=False)
	parser.add_argument('--save_dir', help='directory to save data', required=False)
	parser.add_argument('--load_dir', help='directory to load data. Use --plot with this', required=False)
	parser.add_argument('--population', type=int, help='number of nodes in the graph', required=False)
	parser.add_argument('--test_capacity', type=int, help='number of tests that can be performed at each iteration', required=False)
	parser.add_argument('--pool_size', type=int, help='number of nodes to pool in one test for pooled strategies', required=False)
	parser.add_argument('--iterations', type=int, help='number of time steps to iterate in a simulation', required=False)
	parser.add_argument('--num_simulations', type=int, help='number of simulation episodes to run', required=False)
	parser.add_argument('--r_0', type=float, help='viral reproductive number. Expected number of neighbors that a node should infect over the time duration',
	 required=False)
	parser.add_argument('--test_positive', type=float, help='probability that someone who is sick will test positive',
	 required=False)
	parser.add_argument('--visualize', help='draws the final social network for the last simulation', action='store_true', required=False)
	parser.add_argument('--plot', help='draws the graphs of the simulations. Set --load_dir to provide directory to load from', action='store_true', required=False)
	parser.add_argument('--verbose', help='adds additional logging', action='store_true', required=False)
	parser.add_argument('--p_init_sick', type=float, help='proportion of the population to seed as sick at initialization. Decimal value betwen 0 and 1',
	 required=False)
	args = parser.parse_args()

	# Override defaults if flags given.
	if args.population is not None:
		N = args.population
	if args.test_capacity is not None:
		TIMESTEP_TEST_CAPACITY = args.test_capacity
	if args.pool_size is not None:
		POOL_SIZE = args.pool_size
	if args.iterations is not None:
		NUM_ITERS = args.iterations
	if args.num_simulations is not None:
		NUM_SIMULATIONS = args.num_simulations
	if args.strategy is not None:
		STRATEGY = args.strategy
	if args.save_dir is not None:
		SAVE_DIR = args.save_dir
	if args.load_dir is not None:
		LOAD_DIR = args.load_dir
	if args.r_0 is not None:
		R_0 = args.r_0
	if args.test_positive is not None:
		if args.test_positive >= 0 and args.test_positive <= 1:
			TEST_POSITIVE = args.test_positive
		else:
			sys.exit("Error: test_positive = " + str(args.test_positive) + ". Please provide a test_positive probability between 0 and 1.")
	if args.p_init_sick is not None:
		if args.p_init_sick  >= 0 and args.p_init_sick  <= 1:
			P_INIT_SICK = args.p_init_sick 
		else:
			sys.exit("Error: p_init_sick = " + str(args.p_init_sick ) + ". Please provide a p_init_sick probability between 0 and 1.")
	VISUALIZE = args.visualize
	VERBOSE = args.verbose

	# Handle load_dir validation
	if args.plot:
		if not os.path.exists(LOAD_DIR):
			sys.exit("load_dir does not exist: " + LOAD_DIR)
		else:
			now = datetime.datetime.now()
			myLog(now.strftime("%Y-%m-%d %H:%M:%S") +": Load and plot mode enabled. Loading data to visualize from: " + LOAD_DIR, True)
			simsInfected = np.load(LOAD_DIR+"/infected.npy")
			simsIsolated = np.load(LOAD_DIR+"/isolated.npy")
			simsHealthyFree = np.load(LOAD_DIR+"/healthyFree.npy")
			simsSickFree = np.load(LOAD_DIR+"/sickFree.npy")
			simsSickIsolated = np.load(LOAD_DIR+"/sickIsolated.npy")
			simsHealthyIsolated = np.load(LOAD_DIR+"/healthyIsolated.npy")
			plotHistogram(simsInfected, "Final Infected Populations")
			plotHistogram(simsIsolated, "Final Isolated Populations")
			plotHistogram(simsHealthyFree, "Final Healthy Non-Isolated Populations")
			plotHistogram(simsHealthyIsolated, "Final Healthy Isolated Populations")
			plotHistogram(simsSickFree, "Final Sick Non-Isolated Populations")
			plotHistogram(simsSickIsolated, "Final Sick Isolated Populations")
			now = datetime.datetime.now()
			sys.exit(now.strftime("%Y-%m-%d %H:%M:%S") +": Finished plotting graphs.")
		

	# Handle save_dir creation and validation.
	if not os.path.exists(SAVE_DIR):
		os.mkdir(SAVE_DIR)
	else:
		myLog("root save_dir already exists: " + SAVE_DIR, False)
	# Handle simulation subdirectory creation and validation within save_dir.
	# Creates a subdirectory with hyperparameter values in its title.
	simSubPath = "Strategy_" + STRATEGY + "-" + "Pop_" + str(N) + "-" + "NumSims_" + str(NUM_SIMULATIONS) + "-" + "NumIters_" + str(NUM_ITERS) + "-" + "TestCapacity_" + str(TIMESTEP_TEST_CAPACITY)
	simDirPath = SAVE_DIR + "/" + simSubPath
	if not os.path.exists(simDirPath):
		os.mkdir(simDirPath)
	else:
		myLog("directory to save simulation already exists: " + simDirPath, False)

	# Function pointer that specifies what modification should occur at each step based on 
	# the chosen strategy.
	stepFunction = stepA
	if STRATEGY == 'A':
		stepFunction = stepA
	elif STRATEGY == 'B':
		stepFunction = stepB
	elif STRATEGY == 'C':
		stepFunction = stepC
	elif STRATEGY == 'D':
		stepFunction = stepD
	elif STRATEGY == 'E':
		stepFunction = stepE
	elif STRATEGY == 'F':
		stepFunction = stepF
	elif STRATEGY == 'G':
		stepFunction = stepG
	elif STRATEGY == 'H':
		stepFunction = stepH
	else:
		sys.exit("Incorrect strategy entered.")
		exit()


	# Arrays that contain all the final data for each simulation.
	simsInfected = np.zeros(NUM_SIMULATIONS)
	simsIsolated = np.zeros(NUM_SIMULATIONS)
	simsHealthyFree = np.zeros(NUM_SIMULATIONS)
	simsSickFree = np.zeros(NUM_SIMULATIONS)
	simsSickIsolated = np.zeros(NUM_SIMULATIONS)
	simsHealthyIsolated = np.zeros(NUM_SIMULATIONS)

	now = datetime.datetime.now()
	myLog(now.strftime("%Y-%m-%d %H:%M:%S") +": Starting simulations with Strategy: " + STRATEGY, True)
	# Run a number of simulation episodes.
	for sim in range(NUM_SIMULATIONS):
		myLog("Simulation: " + str(sim), False)

		# Initialize the grap
		G = generateGraph()
		SICK_NODES = set()
		ISOLATED_NODES = set() 
		initSickNodes(G)

		# For certain scenarios, we need full lockdown at initialization.
		if STRATEGY == "E" or STRATEGY == 'F' or STRATEGY == 'G' or STRATEGY == 'H':
			for node in G:
				ISOLATED_NODES.add(node)

		# Run all time step iterations.
		for i in range(NUM_ITERS):
			myLog("Time: " + str(i), False)
			myLog("Time: " + str(i) + ": Number of people infected: " + str(len(SICK_NODES)), False)
			myLog("Time: " + str(i) + ": Number of people isolated: " + str(len(ISOLATED_NODES)), False)
			spreadStatistics(G)
			# Run strategy specific logic for time step.
			stepFunction(G)

			# Spread disease based on stage of model.
			# Sick, unisolated people spread at a high
			sick_nodes = list(SICK_NODES.copy())
			for node in sick_nodes:
				for neighbor in G.neighbors(node):
					if node in ISOLATED_NODES:
						if random.random() < P_INFECT_ISO:
							SICK_NODES.add(neighbor)
					else:
						if random.random() < P_INFECT:
							SICK_NODES.add(neighbor)

		# Calculate final statistics for this simulation.
		stats = spreadStatistics(G)
		healthyFree = stats[0]
		sickFree = stats[1]
		sickIsolated = stats[2]
		healthyIsolated = stats[3]

		simsInfected[sim] = sickFree + sickIsolated
		simsIsolated[sim] = healthyIsolated + sickIsolated
		simsHealthyFree[sim] = healthyFree
		simsSickFree[sim] = sickFree
		simsSickIsolated[sim] = sickIsolated
		simsHealthyIsolated[sim] = healthyIsolated
		myLog("Number of people infected at end: " + str(simsInfected[sim]), False)

	# Only draw final graph of the last simulation if argument is specified. 
	# for visualizing just to get an intuition.
	if VISUALIZE:
		draw(G)

	# Once all simulations are finished, save the data.
	now = datetime.datetime.now()
	myLog(now.strftime("%Y-%m-%d %H:%M:%S") +": Simulations complete. Saving data to: " + simDirPath, True)
	np.save(simDirPath+"/infected", simsInfected)
	np.save(simDirPath+"/isolated", simsIsolated)
	np.save(simDirPath+"/healthyFree", simsHealthyFree)
	np.save(simDirPath+"/sickFree", simsSickFree)
	np.save(simDirPath+"/sickIsolated", simsSickIsolated)
	np.save(simDirPath+"/healthyIsolated", simsHealthyIsolated)



