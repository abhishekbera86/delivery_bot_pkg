#!/bin/bash

# Setup script for Delivery Bot project
# This script sets up the workspace and builds the packages

set -e

echo "=========================================="
echo "Delivery Bot Project Setup"
echo "=========================================="

# Check if ROS2 is sourced
if [ -z "$ROS_DISTRO" ]; then
    echo "Error: ROS2 is not sourced. Please run:"
    echo "  source /opt/ros/jazzy/setup.bash"
    exit 1
fi

echo "ROS2 Distribution: $ROS_DISTRO"

# Navigate to workspace
cd ~/delivery_bot_ws

# Create data directories if they don't exist
echo "Creating data directories..."
mkdir -p data/maps
mkdir -p data

# Build the workspace
echo "Building workspace..."
colcon build --symlink-install

# Source the workspace
echo "Sourcing workspace..."
source install/setup.bash

# Add mandatory sources to .bashrc if not already present
echo "Configuring .bashrc for automatic environment setup..."
BASHRC_FILE="$HOME/.bashrc"
ROS_SETUP_LINE="source /opt/ros/$ROS_DISTRO/setup.bash"
WS_SETUP_LINE="source ~/delivery_bot_ws/install/setup.bash"

# Check and add ROS2 source
if ! grep -qF "$ROS_SETUP_LINE" "$BASHRC_FILE" 2>/dev/null; then
    echo "" >> "$BASHRC_FILE"
    echo "# ROS2 setup (added by delivery_bot_ws setup.sh)" >> "$BASHRC_FILE"
    echo "$ROS_SETUP_LINE" >> "$BASHRC_FILE"
    echo "Added ROS2 source to .bashrc"
else
    echo "ROS2 source already in .bashrc"
fi

# Check and add workspace source
if ! grep -qF "$WS_SETUP_LINE" "$BASHRC_FILE" 2>/dev/null; then
    echo "" >> "$BASHRC_FILE"
    echo "# Delivery Bot workspace setup (added by delivery_bot_ws setup.sh)" >> "$BASHRC_FILE"
    echo "$WS_SETUP_LINE" >> "$BASHRC_FILE"
    echo "Added workspace source to .bashrc"
else
    echo "Workspace source already in .bashrc"
fi

echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "Environment will be automatically set when you open a new terminal."
echo "If you want to use it in the current terminal, run:"
echo "  source ~/delivery_bot_ws/install/setup.bash"
echo ""
echo "Available commands:"
echo "  ros2 run map_manager map_saver_node"
echo "  ros2 run location_manager location_tag_node"
echo "  ros2 run delivery_bot_gui delivery_gui"
echo "  ros2 run delivery_navigator goal_navigator_node"
echo ""

