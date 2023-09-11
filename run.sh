#!/bin/bash

# Check if traces/ directory exists. If it does, delete it.
if [ -d "traces/" ]; then
	rm -rf traces/
fi

# Create a new traces/ directory
mkdir traces/

# Run a python web server on port 8000 in the background
nohup python3 -m http.server -d traces/ 8000 > /dev/null 2>&1 &

while true
do
	# Update git repo
	git pull
	
	# Install requirements
	pip3 install -q -r requirements.txt
	
	# Run the python script
	python3 src/main.py
	
	echo -e '\033[95mexecution successful\033[0m'
	
	# Sleep for 100 hours
	sleep 360000
	
	# Exit the loop
	break
done