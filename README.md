# README


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


