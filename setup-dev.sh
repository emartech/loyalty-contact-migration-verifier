#!/bin/sh
# Setup script for development environment

echo "Setting up development environment..."

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate 2>/dev/null || . .venv/bin/activate

# Install dependencies
echo "Installing pytest..."
pip install pytest -q

# Configure git hooks
echo "Configuring git hooks..."
git config core.hooksPath .githooks

echo ""
echo "✅ Setup complete!"
echo ""
echo "To activate the virtual environment, run:"
echo "  source .venv/bin/activate"
echo ""
echo "To run tests:"
echo "  pytest -v"
echo ""
echo "Git hooks are now enabled - tests will run automatically on commit and push."
