#!/bin/bash

# Ensure the repository is not on a detached head or checkout to the tag if provided
if [ ! -z "$1" ]; then
	git checkout "$1"
	echo "Checked out to tag $1"
else
	# Check if the repository is in a detached head state
	HEAD_REF=$(git symbolic-ref -q HEAD)
	if [ -z "$HEAD_REF" ]; then
		git checkout main
		echo "Checked out to main branch due to detached head"
	fi
fi

# Create a new traces/ directory
mkdir -p traces/

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