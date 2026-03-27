#!/bin/bash
# Setup script for the Pathfinder 1e MCP server
# Usage: ./setup.sh [project-path]
#
# If project-path is given, adds the MCP server to that project's config.
# If omitted, just sets up the venv and builds the DB.

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SERVER_DIR="$SCRIPT_DIR/mcp-server"
VENV_DIR="$SERVER_DIR/.venv"
PYTHON="$VENV_DIR/bin/python3"
SERVER_SCRIPT="$SERVER_DIR/server.py"

echo "=== Pathfinder 1e MCP Server Setup ==="

# Step 1: Create venv and install mcp
if [ ! -f "$PYTHON" ] || ! "$PYTHON" -c "import mcp" 2>/dev/null; then
    echo "Creating Python venv..."
    rm -rf "$VENV_DIR"
    python3 -m venv "$VENV_DIR"
    echo "Installing mcp package..."
    "$PYTHON" -m pip install -q mcp
else
    echo "Python venv OK."
fi

# Step 2: Build DB if needed
DB_PATH="$SCRIPT_DIR/db/pathfinder.db"
if [ ! -f "$DB_PATH" ]; then
    echo "Building database..."
    "$PYTHON" "$SCRIPT_DIR/db/build.py"
else
    echo "Database already exists."
fi

echo ""
echo "=== Setup complete ==="
echo ""

# Step 3: Add to project if path given
if [ -n "$1" ]; then
    PROJECT_PATH="$(cd "$1" && pwd)"
    echo "Adding MCP server to project: $PROJECT_PATH"
    cd "$PROJECT_PATH"
    claude mcp add --scope project --transport stdio pathfinder-data -- "$PYTHON" "$SERVER_SCRIPT"
    echo "Done! MCP server added to $PROJECT_PATH/.mcp.json"
else
    echo "To add to a project, run:"
    echo "  claude mcp add --scope project --transport stdio pathfinder-data -- $PYTHON $SERVER_SCRIPT"
    echo ""
    echo "Or re-run this script with your project path:"
    echo "  ./setup.sh /path/to/your/project"
fi
