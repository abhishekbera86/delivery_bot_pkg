# Installation Guide

This guide will help you install all the dependencies required for the Delivery Bot project. **Follow these steps before starting the Quick Start guide.**

## System Architecture

This project uses a **distributed setup** with two components:

1. **TurtleBot 4 (Raspberry Pi)** - Onboard computer
   - Runs TurtleBot 4 base node and hardware drivers
   - Needs ROS2 Jazzy and TurtleBot 4 packages

2. **Host Computer (Intel NUC)** - High-level computer
   - Runs SLAM, navigation, GUI, and delivery bot nodes
   - Needs ROS2 Jazzy, Nav2, SLAM Toolbox, and all TurtleBot 4 packages

> **⚠️ Important:** TurtleBot 4 official launch files (e.g., `robot.launch.py`) **MUST run on the TurtleBot 4 Raspberry Pi**, not on the host computer. They require direct hardware access.

## Prerequisites

### For TurtleBot 4 (Raspberry Pi):
- **Operating System**: Ubuntu 24.04 (Noble) or compatible
- **Internet connection** for package downloads
- **⚠️ IMPORTANT**: Raspberry Pi doesn't have a battery-backed clock. **Clock synchronization must be set up** (see Step 0 below or `docs/TIME_SYNCHRONIZATION.md`)

### For Host Computer (Intel NUC):
- **Operating System**: Ubuntu 24.04 (Noble)
- **Architecture**: AMD64 (x86_64)
- **Internet connection** for package downloads

## Step 0: Clock Synchronization (CRITICAL)

**⚠️ This step is REQUIRED for proper operation!**

The Raspberry Pi doesn't have a battery-backed real-time clock (RTC). When powered off, the clock resets, causing timestamp mismatches that break navigation and localization.

**Before proceeding with installation, set up clock synchronization:**

See detailed instructions in: **`docs/TIME_SYNCHRONIZATION.md`**

### Quick Setup:

**On Raspberry Pi (TurtleBot4):**

```bash
# Install chrony
sudo apt update
sudo apt install -y chrony

# Configure to use internet NTP servers
sudo nano /etc/chrony/chrony.conf
```

Ensure these lines are present (uncomment if needed):
```
pool 0.pool.ntp.org iburst
pool 1.pool.ntp.org iburst
pool 2.pool.ntp.org iburst
pool 3.pool.ntp.org iburst
```

Save and exit (`Ctrl+X`, then `Y`, then `Enter`).

```bash
# Restart and enable chrony
sudo systemctl restart chrony
sudo systemctl enable chrony

# Verify sync
chronyc sources -v
```

You should see `^*` next to a time source, indicating synchronization.

**Verify on both computers:**
```bash
# On both NUC and Raspberry Pi
date +%s
```

Unix timestamps should be within seconds of each other.

### Timezone Configuration

**⚠️ IMPORTANT:** Even with synchronized clocks, **different timezones will cause problems**. **Both systems MUST have the same timezone.**

**Step 1: Check current timezones**

**On NUC:**
```bash
cat /etc/timezone
timedatectl | grep "Time zone"
```

**On Raspberry Pi:**
```bash
cat /etc/timezone
timedatectl | grep "Time zone"
```

**Step 2: Set both systems to the same timezone**

You have two options:

**Option A: Set both to UTC (Recommended for ROS2)**

**On both NUC and Raspberry Pi:**
```bash
# Set timezone to UTC (recommended for ROS2)
sudo timedatectl set-timezone UTC

# Verify
cat /etc/timezone
timedatectl
date
```

**Expected:** Both systems should show UTC in the `date` output and `/etc/timezone` should contain `UTC`.

**Option B: Match NUC's timezone on Raspberry Pi**

If your NUC is set to a local timezone (e.g., `Europe/Luxembourg`), set the Raspberry Pi to match:

**On NUC, check timezone:**
```bash
cat /etc/timezone
# Example output: Europe/Luxembourg
```

**On Raspberry Pi, set to match NUC:**
```bash
# Replace with your NUC's timezone
sudo timedatectl set-timezone Europe/Luxembourg

# Verify
cat /etc/timezone
timedatectl
date
```

**Expected:** Both `/etc/timezone` files should contain the same timezone, and both systems should show the same time.

**For detailed instructions and troubleshooting:** See `docs/TIME_SYNCHRONIZATION.md`

---

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

## Step 2: Install TurtleBot 4 Packages

### On TurtleBot 4 (Raspberry Pi):

Install all TurtleBot 4 packages including the base node:

```bash
sudo apt update
sudo apt install ros-jazzy-turtlebot4-* -y
```

**Important:** The `turtlebot4_base` package and `robot.launch.py` **must** be installed and run on the TurtleBot 4 Raspberry Pi where the robot hardware is connected.

### On Host Computer (Intel NUC):

Install TurtleBot 4 packages (needed for navigation launch files, but **do not run** `robot.launch.py` here):

```bash
sudo apt update
sudo apt install ros-jazzy-turtlebot4-* -y
```

**Note:** You can install the packages on the host computer, but **do not run** `robot.launch.py` or `turtlebot4_base_node` on the host - they will crash because they need hardware access.

This will install:
- `ros-jazzy-turtlebot4-base` - Base node (required for robot.launch.py)
- `ros-jazzy-turtlebot4-bringup` - Robot bringup launch files
- `ros-jazzy-turtlebot4-description` - Robot description (URDF)
- `ros-jazzy-turtlebot4-desktop` - Desktop metapackage
- `ros-jazzy-turtlebot4-diagnostics` - Diagnostics
- `ros-jazzy-turtlebot4-msgs` - TurtleBot 4 messages
- `ros-jazzy-turtlebot4-navigation` - Navigation stack
- `ros-jazzy-turtlebot4-node` - TurtleBot 4 node
- `ros-jazzy-turtlebot4-viz` - Visualization tools

**If you get an error about missing turtlebot4_base, explicitly install it:**
```bash
sudo apt install ros-jazzy-turtlebot4-base -y
```

## Step 3: Install Teleop Keyboard (for mapping)

Install the teleop keyboard package for manual robot control during mapping:

```bash
sudo apt install ros-jazzy-teleop-twist-keyboard -y
```

**Note:** TurtleBot 4 uses the standard ROS2 `teleop_twist_keyboard` package, not a separate turtlebot4_teleop package.

## Step 4: Install Nav2 Navigation Stack

### On Host Computer (Intel NUC):

Install Nav2 and related packages for navigation:

```bash
sudo apt install ros-jazzy-navigation2 ros-jazzy-nav2-* -y
```

**Note:** Nav2 runs on the host computer, not on the TurtleBot 4 Raspberry Pi.

This includes:
- Nav2 core packages
- Nav2 bringup
- Nav2 planners
- Nav2 controllers
- Nav2 recovery behaviors
- Nav2 map server
- Nav2 lifecycle manager
- And other Nav2 components

## Step 5: Install SLAM Toolbox

### On Host Computer (Intel NUC):

Install SLAM Toolbox for mapping:

```bash
sudo apt install ros-jazzy-slam-toolbox -y
```

**Note:** SLAM runs on the host computer, not on the TurtleBot 4 Raspberry Pi.

## Step 6: Install Python Dependencies

### 6.1 Install tkinter (required for GUI)
```bash
sudo apt install python3-tk -y
```

### 6.2 Verify Python3 is installed
```bash
python3 --version
# Should show Python 3.12 or later
```

## Step 7: Install ROS2 Development Tools (optional but recommended)

For building and developing ROS2 packages:

```bash
sudo apt install python3-colcon-common-extensions -y
sudo apt install python3-rosdep -y
sudo rosdep init
rosdep update
```

## Step 8: Verify Installation

### 8.1 Check ROS2 installation
```bash
ros2 --help
echo $ROS_DISTRO
# Should output: jazzy
```

### 8.2 Verify TurtleBot 4 packages
```bash
ros2 pkg list | grep turtlebot4
# Should show multiple turtlebot4 packages
```

### 8.3 Verify Nav2 packages
```bash
ros2 pkg list | grep nav2
# Should show multiple nav2 packages
```

### 8.4 Verify turtlebot4_base is installed
```bash
ros2 pkg executables turtlebot4_base
# Should show: turtlebot4_base turtlebot4_base_node
```

### 8.5 Verify launch files exist
```bash
ls /opt/ros/jazzy/share/turtlebot4_bringup/launch/robot.launch.py
ls /opt/ros/jazzy/share/turtlebot4_navigation/launch/slam.launch.py
ls /opt/ros/jazzy/share/turtlebot4_navigation/launch/localization.launch.py
ls /opt/ros/jazzy/share/turtlebot4_navigation/launch/nav2.launch.py
```

All files should exist without errors.

## Step 9: Set Up Workspace and Build

### 9.1 On Host Computer (Intel NUC) - Navigate to workspace
```bash
cd ~/delivery_bot_ws
```

### 9.2 Install workspace dependencies (if rosdep is set up)
```bash
rosdep install --from-paths src --ignore-src -r -y
```

### 9.3 Build the workspace
```bash
colcon build --symlink-install
```

### 9.4 Source the workspace
```bash
source install/setup.bash
```

Or use the setup script which does all of this automatically:
```bash
cd ~/delivery_bot_ws
./setup.sh
```

The setup script will:
- Check ROS2 is sourced
- Create data directories
- Build the workspace
- Configure .bashrc for automatic environment setup

## Step 10: Verify Complete Setup

### 10.1 Test package visibility
```bash
ros2 pkg list | grep -E "(map_manager|location_manager|initial_pose_setter)"
```

### 10.2 Test executables
```bash
ros2 pkg executables map_manager
ros2 pkg executables location_manager
ros2 pkg executables initial_pose_setter
```

### 10.3 Test GUI dependency
```bash
python3 -c "import tkinter; print('tkinter OK')"
```

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

### Issue: turtlebot4_base not found
Install on **TurtleBot 4 Raspberry Pi**:
```bash
sudo apt install ros-jazzy-turtlebot4-base -y
```

### Issue: turtlebot4_base_node crashes on host computer
**Important:** `turtlebot4_base_node` and `robot.launch.py` **must run on the TurtleBot 4 Raspberry Pi**, not on the host computer. These launch files need direct access to the robot hardware (USB/serial connections).

If you try to run them on the host computer, you'll get segmentation faults because the hardware is not accessible. Always run TurtleBot 4 official launch files on the robot's onboard computer (Raspberry Pi).

### Issue: tkinter import error
```bash
sudo apt install python3-tk -y
```

### Issue: Build errors
Make sure all dependencies are installed:
```bash
sudo apt install ros-jazzy-turtlebot4-* ros-jazzy-navigation2 ros-jazzy-nav2-* ros-jazzy-slam-toolbox ros-jazzy-teleop-twist-keyboard -y
```

### Issue: Package ros-jazzy-turtlebot4-teleop not found
The `turtlebot4_teleop` package doesn't exist in ROS2 Jazzy. Use the standard ROS2 teleop package instead:
```bash
sudo apt install ros-jazzy-teleop-twist-keyboard -y
# Then use: ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

## Quick Install Script

For convenience, here's a script that installs everything:

```bash
#!/bin/bash
set -e

echo "Installing all Delivery Bot dependencies..."

# Update package lists
sudo apt update

# Install ROS2 Jazzy desktop (if not installed)
if [ -z "$ROS_DISTRO" ]; then
    echo "ROS2 not found. Installing ROS2 Jazzy..."
    # Follow Step 1 above first
    echo "Please install ROS2 Jazzy first (see Step 1)"
    exit 1
fi

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
echo "Now run: cd ~/delivery_bot_ws && ./setup.sh"
```

## Next Steps

Once all dependencies are installed:

1. **Verify installation** using Step 10 above
2. **Run the setup script**: `cd ~/delivery_bot_ws && ./setup.sh`
3. **Follow the Quick Start guide**: See `QUICKSTART.md`

## Summary of Installed Packages

### Core ROS2
- `ros-jazzy-desktop` - ROS2 Jazzy desktop installation

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

**After completing this installation guide, proceed to `QUICKSTART.md` to start using the Delivery Bot system.**

