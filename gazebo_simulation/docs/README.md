# Documentation Directory - Simulation

This directory contains detailed step-by-step guides for using the Delivery Bot project **in Gazebo simulation**.

## Available Guides

### 1. [MAPPING_GUIDE.md](MAPPING_GUIDE.md)
**Complete guide for creating SLAM maps in simulation**

This guide walks you through:
- Starting Gazebo simulation with SLAM
- Teleoperating the robot to explore the office world
- Creating and saving a SLAM map of the 8-desk office environment

**When to use:** First time setup, creating a new map for your environment.

---

### 2. [LOCATION_TAGGING_GUIDE.md](LOCATION_TAGGING_GUIDE.md)
**Guide for tagging the 8 desk delivery locations**

This guide explains:
- How to tag all 8 desk locations in the simulation
- How to navigate the robot to each desk
- How to name and save locations
- Viewing and verifying tagged locations

**When to use:** After creating a map, to mark all 8 desk delivery points.

---

### 3. [DELIVERY_BOT_GUIDE.md](DELIVERY_BOT_GUIDE.md)
**Guide for using the delivery bot system in simulation**

This guide covers:
- Loading a saved map with localization
- Starting the navigation stack
- Using the GUI to select destinations
- Autonomous navigation to tagged desk locations

**When to use:** Daily operation of the delivery bot simulation system.

---

## Quick Reference

| Guide | Purpose | Steps |
|-------|---------|-------|
| MAPPING_GUIDE | Create SLAM maps | Simulation + SLAM + Teleoperation + Save Map |
| LOCATION_TAGGING_GUIDE | Tag 8 desk locations | Simulation + Localization + Teleoperation + Tag Locations |
| DELIVERY_BOT_GUIDE | Use delivery bot | Simulation + Localization + Navigator + GUI + Navigate |

---

## System Architecture

All guides are for **simulation-only** setup:

- **Single Computer** - Everything runs on one machine
- **Gazebo Simulation** - Robot simulation in Gazebo
- **No Physical Hardware** - No TurtleBot 4 robot required

---

## Getting Started

1. **Install dependencies:** See `../INSTALLATION.md`
2. **Create a map:** Follow `MAPPING_GUIDE.md`
3. **Tag locations:** Follow `LOCATION_TAGGING_GUIDE.md` to tag all 8 desks
4. **Use delivery bot:** Follow `DELIVERY_BOT_GUIDE.md` to navigate

---

## Related Documentation

- **[../README.md](../README.md)** - Project overview and architecture
- **[../INSTALLATION.md](../INSTALLATION.md)** - Installation instructions for simulation

---

## World Description

The simulation uses a custom world file (`../worlds/office_world_8desks.world`) featuring:
- A 20x20 meter office room with walls
- **8 desks** positioned in a grid layout:
  - Desk 1: Bottom Left (-6, -6)
  - Desk 2: Bottom Center (0, -6)
  - Desk 3: Bottom Right (6, -6)
  - Desk 4: Center Left (-6, 0)
  - Desk 5: Center Right (6, 0)
  - Desk 6: Top Left (-6, 6)
  - Desk 7: Top Center (0, 6)
  - Desk 8: Top Right (6, 6)

---

## Need Help?

If you encounter issues:
1. Check the troubleshooting sections in each guide
2. Verify system requirements in `../INSTALLATION.md`
3. Ensure all prerequisites are met
4. Check that simulation is running correctly

---
