#!/bin/bash

# Check if a git tag is provided as a command-line argument and checkout that tag before running the script
if [ ! -z "$1" ]; then
	git checkout "$1"
	echo "Checked out to tag $1"
else
	git checkout main
	echo "Checked out to main branch"
fi

# Check if the traces/ directory already exists
if [ -d "traces/" ]; then
	echo "The traces/ directory already exists."
else
	# Create a new traces/ directory
	mkdir traces/
fi

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