#!/bin/bash
# PLAMOTO database setup script
# -------------------------------------------
# This script runs Flask-Migrate commands to
# initialize and migrate the database.
# -------------------------------------------

set -e

# Activate virtual environment
source .venv/bin/activate

# Load environment variables from .env
export $(grep -v '^#' .env | xargs)

echo "🚀 Running database migrations..."

# Initialize migration repo (only if it doesn't exist)
if [ ! -d "migrations" ]; then
    flask db init
    echo "✅ Migration repository initialized."
fi

# Create migration scripts
flask db migrate -m "Initial migration"
echo "✅ Migration scripts created."

# Apply migrations to database
flask db upgrade
echo "✅ Database upgraded."

echo "🎉 Database setup complete!"
