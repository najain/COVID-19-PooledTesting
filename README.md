# README

Nishant Jain, Amay Aggarwal, Andrew Hwang

Stanford University

## Introduction
We have implemented an agent-based simulator for modeling the spread of a disease through a population. Our simulator uses a social network graph to describe the spread of COVID-19, through a population as a function of time under different testing and isolation strategies. The parameters of the model are calibrated based on published data regarding COVID-19, with relevant papers referenced in the source code.

## Environment Setup
Run the following commands to set up a virtual environment which has the dependencies needed to run the model.

```
sudo pip install virtualenv          # This may already be installed
virtualenv .env --python=python3.6   # Create a virtual environment
source .env/bin/activate             # Activate the virtual environment
pip install -r requirements.txt      # Install dependencies


# Run the model
python graph.py

# Work on the code for a while ... then
# Exit the virtual environment
deactivate                           
```

## Help
The parameters are documented and can be accessed by running the following command:
```
>python graph.py -h

usage: graph.py [-h] [--strategy STRATEGY] [--save_dir SAVE_DIR]
                [--population POPULATION] [--test_capacity TEST_CAPACITY]
                [--pool_size POOL_SIZE] [--iterations ITERATIONS]
                [--num_simulations NUM_SIMULATIONS] [--r_0 R_0]
                [--test_positive TEST_POSITIVE] [--visualize] [--verbose]
                [--p_init_sick P_INIT_SICK]

An agent based simulator for COVID-19 using a social network graph.

optional arguments:
  -h, --help            show this help message and exit
  --strategy STRATEGY   testing and quarantine strategy
  --save_dir SAVE_DIR   directory to save data
  --population POPULATION
                        number of nodes in the graph
  --test_capacity TEST_CAPACITY
                        number of tests that can be performed at each
                        iteration
  --pool_size POOL_SIZE
                        number of nodes to pool in one test for pooled
                        strategies
  --iterations ITERATIONS
                        number of time steps to iterate in a simulation
  --num_simulations NUM_SIMULATIONS
                        number of simulation episodes to run
  --r_0 R_0             viral reproductive number. Expected number of
                        neighbors that a node should infect over the time
                        duration
  --test_positive TEST_POSITIVE
                        probability that someone who is sick will test
                        positive
  --visualize           draws the final social network for the last simulation
  --verbose             adds additional logging
  --p_init_sick P_INIT_SICK
                        proportion of the population to seed as sick at
                        initialization. Decimal value betwen 0 and 1

```
To see default values, look at the constants defined at the top of graph.py.

## Strategies
There are several different strategies implemented to model different scenarios. They can be specified using the --strategy argument with one of the following capital letter choices:

* A: Test and Isolate: Whoever tests positive is isolated immediately. No initial lockdown.
* B: Test, Full Contact Trace, and Isolate. No initial lockdown.
* C: Test, Noisy Contact Trace, and Isolate. No initial lockdown.
* D: Unmitigated Spread. No lockdown.
* E: Complete Lockdown for full duration.
* F: Start with Complete Lockdown, then do Pooled testing With Overly Conservative Noisy Contact Tracing.
* G: Start with Complete Lockdown, then do Pooled testing with no Noisy Contact Tracing.
* H: Start with Complete Lockdown, then do individual testing without pooling, but with Noisy Contact Tracing.

