# README


## Environment Setup
Run the following commands to set up a virtual environment.

```
sudo pip install virtualenv          # This may already be installed
virtualenv .env --python=python3.6   # Create a virtual environment
source .env/bin/activate             # Activate the virtual environment
pip install -r requirements.txt      # Install dependencies
# Work on the code for a while ...
deactivate                           # Exit the virtual environment
```
