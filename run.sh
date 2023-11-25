#!/bin/bash

# Default to the main branch if no version is specified
version="main"
# Initialize an empty array for additional arguments
extra_args=()

# Iterate over arguments to find a version and collect additional arguments
for arg in "$@"; do
	if [[ $arg == "--version" ]]; then
		expect_version_val=true
	elif [[ $expect_version_val == true ]]; then
		version=$arg
		expect_version_val=false
	else
		extra_args+=("$arg")
	fi
done

# Checkout to the specified version or main if version is not set
git checkout "$version"
echo "Checked out to $version"

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

	# Run the python script with additional arguments
	python3 src/main.py "${extra_args[@]}"

	echo -e '\033[95mexecution successful\033[0m'

	# Sleep for 100 hours
	sleep 360000

	# Exit the loop
	break
done