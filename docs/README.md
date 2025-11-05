# Documentation

This directory contains detailed step-by-step guides for the Delivery Bot project.

## Available Guides

### [MAPPING_AND_LOCATION_TAGGING.md](MAPPING_AND_LOCATION_TAGGING.md)
**Unified guide for creating SLAM maps and tagging locations**

Complete guide for:
- Starting unified mapping and tagging system (single launch command!)
- Using the unified GUI to configure JSON filename
- Tagging delivery locations during mapping
- Saving maps directly from the GUI
- Exiting cleanly

**Key Features:**
- **Single Launch Command** - Everything starts with one command
- **Unified GUI** - One interface handles everything
- **JSON Filename Configuration** - Set custom location file names
- **Map Saving from GUI** - Save maps directly from the interface

**When to use:** First time setup, creating a new map and tagging delivery locations.

---

### [DELIVERY_BOT_GUIDE.md](DELIVERY_BOT_GUIDE.md)
**Guide for using the delivery bot system for navigation**

Complete guide for:
- Loading saved maps with localization
- Setting initial pose using tagged locations
- Starting navigation stack
- Using the GUI to navigate to destinations

**When to use:** Daily operation for autonomous navigation.

---

### [TIME_SYNCHRONIZATION.md](TIME_SYNCHRONIZATION.md)
**Setting up clock synchronization (CRITICAL)**

Essential guide for:
- Why clock synchronization is critical
- Setting up NTP synchronization
- Verifying synchronization
- Troubleshooting sync issues

**When to use:** Initial setup, before running any delivery bot operations.

**⚠️ IMPORTANT:** Clock synchronization is critical - without it, navigation will fail.

---

## Quick Reference

| Guide | Purpose |
|-------|---------|
| MAPPING_AND_LOCATION_TAGGING | Create maps and tag locations (unified GUI) |
| DELIVERY_BOT_GUIDE | Use delivery bot for navigation |
| TIME_SYNCHRONIZATION | Set up clock sync (critical) |

---

## Getting Started

1. **Install dependencies:** See `../INSTALLATION.md`
2. **Set up clock synchronization:** Follow `TIME_SYNCHRONIZATION.md` (CRITICAL!)
3. **Create map and tag locations:** Follow `MAPPING_AND_LOCATION_TAGGING.md` (single launch command!)
4. **Use delivery bot:** Follow `DELIVERY_BOT_GUIDE.md`

---

## Related Documentation

- **[../README.md](../README.md)** - Project overview
- **[../ARCHITECTURE.md](../ARCHITECTURE.md)** - System architecture
- **[../QUICKSTART.md](../QUICKSTART.md)** - Quick reference
- **[../INSTALLATION.md](../INSTALLATION.md)** - Installation instructions

---

## Workflow Overview

### Workflow 1: Map Creation with Location Tagging (First Time)

**Single unified launch:**

1. Start robot hardware (TurtleBot 4 Pi)
2. Start unified system: `ros2 launch launch/mapping_with_tagging.launch.py` (Host NUC)
3. Configure JSON filename in GUI (optional)
4. Drive robot and tag locations as you map
5. Save map from GUI when complete
6. Exit when done

**Result:**
- Map saved to: `~/delivery_bot_pkg/data/maps/{map_name}.yaml`
- Locations saved to: `~/delivery_bot_pkg/data/locations/{json_filename}.json`

**See:** `MAPPING_AND_LOCATION_TAGGING.md` for complete guide

### Workflow 2: Delivery Bot Application (Daily Use)

1. Start robot hardware (TurtleBot 4 Pi)
2. Load saved map with localization (Host NUC)
3. Set initial pose (use tagged location or manual entry)
4. Start Nav2 navigation (Host NUC)
5. Start delivery navigator (Host NUC)
6. Start delivery GUI (Host NUC)
7. Select location and navigate!

**See:** `DELIVERY_BOT_GUIDE.md` for complete guide
