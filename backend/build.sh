#!/usr/bin/env bash
# Exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# You can add more build steps here (like database migrations)
echo "Backend build complete!"
