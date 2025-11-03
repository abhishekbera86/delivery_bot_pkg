#!/bin/bash
# Setup script for Delivery Bot Gazebo Simulation
# This script builds the workspace and sets up the environment

set -e

echo "=========================================="
echo "Delivery Bot Simulation Setup"
echo "=========================================="

# Check if ROS2 is sourced
if [ -z "$ROS_DISTRO" ]; then
    echo "ERROR: ROS2 is not sourced!"
    echo "Please run: source /opt/ros/jazzy/setup.bash"
    echo "Or add it to your ~/.bashrc"
    exit 1
fi

echo "ROS2 Distro: $ROS_DISTRO"

# Get the directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo ""
echo "Workspace directory: $SCRIPT_DIR"

# Create data directories
echo ""
echo "Creating data directories..."
mkdir -p data/maps
mkdir -p data
echo "Data directories created"

# Build the workspace
echo ""
echo "Building workspace..."
colcon build --symlink-install

# Check build result
if [ $? -eq 0 ]; then
    echo ""
    echo "✓ Build successful!"
else
    echo ""
    echo "✗ Build failed!"
    exit 1
fi

# Source the workspace
echo ""
echo "Sourcing workspace..."
source install/setup.bash

# Check if setup.bash exists
if [ -f install/setup.bash ]; then
    echo "✓ Workspace sourced successfully"
else
    echo "✗ setup.bash not found!"
    exit 1
fi

# Add to .bashrc if not already there
if ! grep -q "source.*gazebo_simulation/install/setup.bash" ~/.bashrc; then
    echo ""
    echo "Adding workspace to ~/.bashrc..."
    echo "" >> ~/.bashrc
    echo "# Delivery Bot Simulation Workspace" >> ~/.bashrc
    echo "source $SCRIPT_DIR/install/setup.bash" >> ~/.bashrc
    echo "✓ Added to ~/.bashrc"
else
    echo ""
    echo "✓ Workspace already in ~/.bashrc"
fi

# Verify packages
echo ""
echo "Verifying packages..."
packages=("map_manager" "location_manager" "delivery_navigator" "delivery_bot_gui")
all_found=true

for pkg in "${packages[@]}"; do
    if ros2 pkg list | grep -q "^${pkg}$"; then
        echo "  ✓ $pkg found"
    else
        echo "  ✗ $pkg not found"
        all_found=false
    fi
done

if [ "$all_found" = true ]; then
    echo ""
    echo "✓ All packages found"
else
    echo ""
    echo "✗ Some packages not found. Build may have issues."
fi

# Verify world file
echo ""
echo "Verifying world file..."
if [ -f "worlds/office_world_8desks.world" ]; then
    echo "  ✓ World file found: worlds/office_world_8desks.world"
else
    echo "  ✗ World file not found: worlds/office_world_8desks.world"
fi

# Final message
echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Read INSTALLATION.md for dependencies"
echo "2. Read README.md for overview"
echo "3. Follow docs/MAPPING_GUIDE.md to create a map"
echo "4. Follow docs/LOCATION_TAGGING_GUIDE.md to tag 8 desks"
echo "5. Follow docs/DELIVERY_BOT_GUIDE.md to use the system"
echo ""
echo "To start simulation:"
echo "  cd $SCRIPT_DIR"
echo "  source install/setup.bash"
echo "  ros2 launch simulation simulation.launch.py"
echo ""

