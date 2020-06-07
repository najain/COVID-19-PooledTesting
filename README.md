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
python graph.py -h
```
To see default values, look at the constants defined at the top of graph.py.

## Strategies
There are 6 different strategies implemented to model different scenarios. They can be specified using the --strategy argument with one of the following capital letter choices:

* A: Test and Isolate: Whoever tests positive is isolated immediately.
* B: Test, Full Contact Trace, and Isolate: Whoever tests positive is isolated and has all of their neighbors isolated as well.
* C: Test, Noisy Contact Trace, and Isolate: Whoever tests positive is isolated and has a subset of their neighbors isolated as well.
* D: Unmitigated Spread
* E: Complete Lockdown
* F: Start with Complete Lockdown, then do Pooled testing With Overly Conservative Contact Tracing.

