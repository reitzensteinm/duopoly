# Default to the main branch if no version is specified
$version = "main"
# Initialize an empty array for additional arguments
$extra_args = @()

# Iterate over arguments to find a version and collect additional arguments
foreach ($arg in $args) {
	if ($arg -eq "--version") {
		$expect_version_val = $true
	} elseif ($expect_value_val) {
		$version = $arg
		$expect_version_val = $false
	} else {
		$extra_args += $arg
	}
}

# Checkout to the specified version or main if version is not set
git checkout $version
Write-Host "Checked out to $version"

# Check if the traces/ directory already exists
if (Test-Path "traces/") {
	Write-Host "The traces/ directory already exists."
} else {
	# Create a new traces/ directory
	New-Item -ItemType Directory -Path "traces/"
}

# Run a python web server on port 8000 in the background
Start-Job { python -m http.server -d traces/ 8000 }

while ($true) {
	# Update git repo
	git pull

	# Install requirements
	python -m pip install -q -r requirements.txt

	# Run the python script with additional arguments
	python src/main.py $extra_args

	Write-Host "execution successful" -ForegroundColor Magenta

	# Sleep for 20 seconds
	Start-Sleep -Seconds 20
}