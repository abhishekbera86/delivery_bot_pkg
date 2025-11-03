# Installation Guide - Gazebo Simulation

This guide will help you install all the dependencies required for the Delivery Bot project **running in Gazebo simulation**. Follow these steps before starting the simulation.

## System Architecture

This simulation project runs **entirely on a single computer** using Gazebo:

- **Gazebo Simulation** - TurtleBot 4 robot simulation
- **SLAM and Mapping** - SLAM Toolbox
- **Navigation Stack** - Nav2
- **Delivery Bot Nodes** - GUI, navigator, location manager, map manager

> **⚠️ Important:** This is a **simulation-only** setup. No physical robot hardware is required. All components run on a single computer.

## Prerequisites

### System Requirements:
- **Operating System**: Ubuntu 24.04 (Noble)
- **Architecture**: AMD64 (x86_64)
- **RAM**: At least 4GB recommended (8GB+ for better performance)
- **Graphics**: 3D graphics acceleration recommended
- **Internet connection** for package downloads

## Step 1: Install ROS2 Jazzy (if not already installed)

If ROS2 Jazzy is not already installed on your system:

### 1.1 Set up locale
```bash
sudo apt update && sudo apt install locales
sudo locale-gen en_US en_US.UTF-8
sudo update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8
export LANG=en_US.UTF-8
```

### 1.2 Add ROS2 apt repository
```bash
sudo apt install software-properties-common
sudo add-apt-repository universe
sudo apt update && sudo apt install curl -y
sudo curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key -o /usr/share/keyrings/ros-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu $(. /etc/os-release && echo $UBUNTU_CODENAME) main" | sudo tee /etc/apt/sources.list.d/ros2-latest.list > /dev/null
```

### 1.3 Install ROS2 Jazzy
```bash
sudo apt update
sudo apt install ros-jazzy-desktop -y
```

### 1.4 Source ROS2 environment (add to .bashrc)
```bash
echo "source /opt/ros/jazzy/setup.bash" >> ~/.bashrc
source ~/.bashrc
```

## Step 2: Install Gazebo

### 2.1 Install Gazebo Classic
```bash
sudo apt update
sudo apt install gazebo11 libgazebo11-dev -y
```

### 2.2 Verify Gazebo installation
```bash
gazebo --version
# Should show: gazebo11 version
```

## Step 3: Install TurtleBot 4 Packages

Install TurtleBot 4 packages (needed for robot model and launch files):

```bash
sudo apt update
sudo apt install ros-jazzy-turtlebot4-* -y
```

This will install:
- `ros-jazzy-turtlebot4-base` - Base node
- `ros-jazzy-turtlebot4-bringup` - Robot bringup launch files
- `ros-jazzy-turtlebot4-description` - Robot description (URDF)
- `ros-jazzy-turtlebot4-desktop` - Desktop metapackage
- `ros-jazzy-turtlebot4-diagnostics` - Diagnostics
- `ros-jazzy-turtlebot4-msgs` - TurtleBot 4 messages
- `ros-jazzy-turtlebot4-navigation` - Navigation stack
- `ros-jazzy-turtlebot4-node` - TurtleBot 4 node
- `ros-jazzy-turtlebot4-viz` - Visualization tools

## Step 4: Install Teleop Keyboard (for mapping)

Install the teleop keyboard package for manual robot control during mapping:

```bash
sudo apt install ros-jazzy-teleop-twist-keyboard -y
```

## Step 5: Install Nav2 Navigation Stack

Install Nav2 and related packages for navigation:

```bash
sudo apt install ros-jazzy-navigation2 ros-jazzy-nav2-* -y
```

This includes:
- Nav2 core packages
- Nav2 bringup
- Nav2 planners
- Nav2 controllers
- Nav2 recovery behaviors
- Nav2 map server
- Nav2 lifecycle manager
- And other Nav2 components

## Step 6: Install SLAM Toolbox

Install SLAM Toolbox for mapping:

```bash
sudo apt install ros-jazzy-slam-toolbox -y
```

## Step 7: Install Python Dependencies

### 7.1 Install tkinter (required for GUI)
```bash
sudo apt install python3-tk -y
```

### 7.2 Verify Python3 is installed
```bash
python3 --version
# Should show Python 3.12 or later
```

## Step 8: Install ROS2 Development Tools (optional but recommended)

For building and developing ROS2 packages:

```bash
sudo apt install python3-colcon-common-extensions -y
sudo apt install python3-rosdep -y
sudo rosdep init
rosdep update
```

## Step 9: Verify Installation

### 9.1 Check ROS2 installation
```bash
ros2 --help
echo $ROS_DISTRO
# Should output: jazzy
```

### 9.2 Verify TurtleBot 4 packages
```bash
ros2 pkg list | grep turtlebot4
# Should show multiple turtlebot4 packages
```

### 9.3 Verify Nav2 packages
```bash
ros2 pkg list | grep nav2
# Should show multiple nav2 packages
```

### 9.4 Verify Gazebo
```bash
gazebo --version
# Should show gazebo11 version
```

### 9.5 Verify launch files exist
```bash
ls /opt/ros/jazzy/share/turtlebot4_bringup/launch/
ls /opt/ros/jazzy/share/turtlebot4_navigation/launch/
```

## Step 10: Set Up Workspace and Build

### 10.1 Navigate to simulation directory
```bash
cd ~/delivery_bot_ws/gazebo_simulation
```

### 10.2 Install workspace dependencies (if rosdep is set up)
```bash
rosdep install --from-paths src --ignore-src -r -y
```

### 10.3 Build the workspace
```bash
colcon build --symlink-install
```

### 10.4 Source the workspace
```bash
source install/setup.bash
```

### 10.5 Add to .bashrc (optional)
```bash
echo "source ~/delivery_bot_ws/gazebo_simulation/install/setup.bash" >> ~/.bashrc
```

## Step 11: Verify Complete Setup

### 11.1 Test package visibility
```bash
ros2 pkg list | grep -E "(delivery_bot|map_manager|location_manager|delivery_navigator|delivery_bot_gui)"
```

### 11.2 Test executables
```bash
ros2 pkg executables map_manager
ros2 pkg executables location_manager
ros2 pkg executables delivery_navigator
ros2 pkg executables delivery_bot_gui
```

### 11.3 Test GUI dependency
```bash
python3 -c "import tkinter; print('tkinter OK')"
```

### 11.4 Verify world file exists
```bash
ls ~/delivery_bot_ws/gazebo_simulation/worlds/office_world_8desks.world
```

### 11.5 Test Gazebo launch
```bash
cd ~/delivery_bot_ws/gazebo_simulation
source install/setup.bash
# This should open Gazebo with the simulation (you can close it after verification)
ros2 launch turtlebot4_bringup gazebo.launch.py world:=~/delivery_bot_ws/gazebo_simulation/worlds/office_world_8desks.world
```

Press Ctrl+C to stop after verification.

## Common Installation Issues

### Issue: Package not found
If you get errors about missing packages:
```bash
sudo apt update
sudo apt upgrade
```

### Issue: ROS2 not sourced
```bash
source /opt/ros/jazzy/setup.bash
echo "source /opt/ros/jazzy/setup.bash" >> ~/.bashrc
```

### Issue: Gazebo not found
```bash
sudo apt install gazebo11 libgazebo11-dev -y
```

### Issue: tkinter import error
```bash
sudo apt install python3-tk -y
```

### Issue: Build errors
Make sure all dependencies are installed:
```bash
sudo apt install ros-jazzy-turtlebot4-* ros-jazzy-navigation2 ros-jazzy-nav2-* ros-jazzy-slam-toolbox ros-jazzy-teleop-twist-keyboard gazebo11 libgazebo11-dev -y
```

### Issue: World file not found
Ensure you're in the correct directory:
```bash
cd ~/delivery_bot_ws/gazebo_simulation
ls worlds/office_world_8desks.world
```

### Issue: Launch file not found
Verify turtlebot4 packages are installed:
```bash
sudo apt install ros-jazzy-turtlebot4-* -y
ros2 pkg list | grep turtlebot4
```

## Quick Install Script

For convenience, here's a script that installs everything for simulation:

```bash
#!/bin/bash
set -e

echo "Installing all Delivery Bot Simulation dependencies..."

# Update package lists
sudo apt update

# Install ROS2 Jazzy desktop (if not installed)
if [ -z "$ROS_DISTRO" ]; then
    echo "ROS2 not found. Please install ROS2 Jazzy first (see Step 1)"
    exit 1
fi

# Install Gazebo
echo "Installing Gazebo..."
sudo apt install gazebo11 libgazebo11-dev -y

# Install TurtleBot 4 packages
echo "Installing TurtleBot 4 packages..."
sudo apt install ros-jazzy-turtlebot4-* -y

# Install teleop keyboard
echo "Installing teleop keyboard..."
sudo apt install ros-jazzy-teleop-twist-keyboard -y

# Install Nav2
echo "Installing Nav2..."
sudo apt install ros-jazzy-navigation2 ros-jazzy-nav2-* -y

# Install SLAM Toolbox
echo "Installing SLAM Toolbox..."
sudo apt install ros-jazzy-slam-toolbox -y

# Install Python dependencies
echo "Installing Python dependencies..."
sudo apt install python3-tk -y

# Install build tools
echo "Installing build tools..."
sudo apt install python3-colcon-common-extensions -y

echo "Installation complete!"
echo "Now run: cd ~/delivery_bot_ws/gazebo_simulation && colcon build && source install/setup.bash"
```

Save this as `install_simulation.sh`, make it executable, and run it:
```bash
chmod +x install_simulation.sh
./install_simulation.sh
```

## Next Steps

Once all dependencies are installed:

1. **Verify installation** using Step 11 above
2. **Build the workspace**: `cd ~/delivery_bot_ws/gazebo_simulation && colcon build && source install/setup.bash`
3. **Start simulation**: See the README.md for quick start instructions

## Summary of Installed Packages

### Core ROS2
- `ros-jazzy-desktop` - ROS2 Jazzy desktop installation

### Simulation
- `gazebo11` - Gazebo Classic simulator
- `libgazebo11-dev` - Gazebo development libraries

### TurtleBot 4
- `ros-jazzy-turtlebot4-*` - All TurtleBot 4 packages

### Teleoperation
- `ros-jazzy-teleop-twist-keyboard` - Keyboard teleoperation

### Navigation
- `ros-jazzy-navigation2` - Nav2 core
- `ros-jazzy-nav2-*` - All Nav2 packages

### Mapping
- `ros-jazzy-slam-toolbox` - SLAM Toolbox

### Python
- `python3-tk` - Tkinter for GUI

### Build Tools
- `python3-colcon-common-extensions` - Colcon build system
- `python3-rosdep` - ROS dependency management

---

**After completing this installation guide, proceed to README.md to start using the Delivery Bot simulation.**
