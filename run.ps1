# Set the default version to 'main'.
$version = "main"
$extraArgs = @()
$expectVersionVal = $false

# Process command line arguments to extract a version and store additional arguments.
foreach ($arg in $args) {
	if ($arg -eq "--version") {
		$expectVersionVal = $true
	}
	elseif ($expectVersionVal) {
		$version = $arg
		$expectVersionVal = $false
	}
	else {
		$extraArgs += $arg
	}
}

# Perform a git checkout to the specified version.
git checkout $version
Write-Host "Checked out to $version"

# Check for the existence of the 'traces/' directory and create it if it doesn't exist.
if (-Not (Test-Path "traces/")) {
	New-Item -ItemType Directory -Path "traces/"
}

# Run a Python web server with the directory 'traces/' on port 8000 in the background.
Start-Job { python -m http.server -d traces/ 8000 }

# Infinite loop: pull updates from git, install requirements, run Python script, print success message, wait 20 seconds.
do {
	git pull
	pip install -r requirements.txt
	python src/main.py $extraArgs

	Write-Host -ForegroundColor Magenta "execution successful"

	Start-Sleep -Seconds 20
} while ($true)