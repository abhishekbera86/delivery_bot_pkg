# Documentation Directory

This directory contains detailed step-by-step guides for using the Delivery Bot project.

## Available Guides

### 1. [MAPPING_GUIDE.md](MAPPING_GUIDE.md)
**Complete guide for creating SLAM maps**

This guide walks you through:
- Starting robot hardware on TurtleBot 4 Raspberry Pi
- Starting SLAM on the host computer
- Teleoperating the robot to explore and map the environment
- Saving the map for later use

**When to use:** First time setup, creating a new map for your environment.

---

### 2. [LOCATION_TAGGING_GUIDE.md](LOCATION_TAGGING_GUIDE.md)
**Guide for tagging delivery locations**

This guide explains:
- How to tag specific locations in your map
- How to navigate the robot to each location
- How to name and save locations
- Viewing and editing tagged locations

**When to use:** After creating a map, to mark delivery points.

---

### 3. [DELIVERY_BOT_GUIDE.md](DELIVERY_BOT_GUIDE.md)
**Guide for using the delivery bot system**

This guide covers:
- Loading a saved map with localization
- Starting the navigation stack
- Using the GUI to select destinations
- Autonomous navigation to locations

**When to use:** Daily operation of the delivery bot system.

---

## Quick Reference

| Guide | Purpose | Systems Used |
|-------|---------|--------------|
| MAPPING_GUIDE | Create SLAM maps | TurtleBot 4 Pi + Host NUC |
| LOCATION_TAGGING_GUIDE | Tag delivery locations | TurtleBot 4 Pi + Host NUC |
| DELIVERY_BOT_GUIDE | Use delivery bot | TurtleBot 4 Pi + Host NUC |

---

## System Architecture

All guides clearly indicate which commands run on which system:

- **📍 On: TurtleBot 4 (Raspberry Pi)** - Robot hardware and sensors
- **📍 On: Host Computer (Intel NUC)** - Navigation, SLAM, GUI, and high-level control

---

## Getting Started

1. **Install dependencies:** See `../INSTALLATION.md`
2. **Create a map:** Follow `MAPPING_GUIDE.md`
3. **Tag locations:** Follow `LOCATION_TAGGING_GUIDE.md`
4. **Use delivery bot:** Follow `DELIVERY_BOT_GUIDE.md`

---

## Related Documentation

- **[../README.md](../README.md)** - Project overview and architecture
- **[../INSTALLATION.md](../INSTALLATION.md)** - Installation instructions
- **[../QUICKSTART.md](../QUICKSTART.md)** - Quick reference guide
- **[../ARCHITECTURE.md](../ARCHITECTURE.md)** - System architecture details

---

## Need Help?

If you encounter issues:
1. Check the troubleshooting sections in each guide
2. Verify system architecture requirements
3. Ensure all prerequisites are met
4. Check that commands are run on the correct system

