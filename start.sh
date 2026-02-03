#!/usr/bin/env bash
# Exit on error
set -o errexit

# Install dependencies from the Render-specific requirements file
pip install -r requirements-render.txt

# Run migrations (if you have them, uncomment below)
# alembic upgrade head
