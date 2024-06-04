# PowerShell script equivalent to run.sh

# Default to the main branch if no version is specified
$version = "main"
# Initialize an empty array for additional arguments
$extraArgs = @()

# Iterate over arguments to find a version and collect additional arguments
for ($i = 0; $i -lt $args.Count; $i++) {
    if ($args[$i] -eq "--version") {
        $expectVersionVal = $true
    }
    elseif ($expectVersionVal) {
        $version = $args[$i]
        $expectVersionVal = $false
    }
    else {
        $extraArgs += $args[$i]
    }
}

# Checkout to the specified version or main if version is not set
git checkout $version
Write-Host "Checked out to $version"

# Check if the traces/ directory already exists
if (Test-Path -Path "traces/") {
    Write-Host "The traces/ directory already exists."
}
else {
    # Create a new traces/ directory
    New-Item -ItemType Directory -Path "traces/"
}

# Run a python web server on port 8000 in the background
Start-Job { python -m http.server -d traces/ 8000 }

while ($true) {
    # Update git repo
    git pull

    # Install requirements
    pip install -q -r requirements.txt

    # Run the python script with additional arguments
    python src/main.py @extraArgs

    Write-Host "execution successful" -ForegroundColor Magenta

    # Sleep for 20 seconds
    Start-Sleep -Seconds 20
}